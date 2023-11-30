import asyncio
import logging
from decimal import ROUND_DOWN, Decimal
from typing import Dict

from orderly_sdk.rest import AsyncClient

from liquidation_searcher.types import ActionType, Executor, LiquidationType

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class OrderlyExecutor(Executor):
    symbol_base_ticks: Dict[str, Decimal]

    def __init__(self, account_id, orderly_key, orderly_secret, endpoint):
        self.orderly_client = AsyncClient(
            account_id=account_id,
            orderly_key=orderly_key,
            orderly_secret=orderly_secret,
            endpoint=endpoint,
        )
        self.symbol_base_ticks = dict()

    async def sync_state(self):
        symbols = await self.orderly_client.get_available_symbols()
        for symbol in symbols["data"]["rows"]:
            self.symbol_base_ticks[symbol["symbol"]] = Decimal(symbol["base_tick"])

    async def execute(self, action):
        if action["action_type"] == ActionType.ORDERLY_LIQUIDATION_ORDER:
            if action["type"] == LiquidationType.LIQUIDATED:
                json = dict(
                    liquidation_id=action["liquidation_id"],
                    ratio_qty_request=0.001,
                )
                await self.orderly_client.claim_liquidated_positions(json)
            elif action["type"] == LiquidationType.CLAIM:
                for position in action["positions_by_perp"]:
                    json = dict(
                        liquidation_id=action["liquidation_id"],
                        symbol=position["symbol"],
                        qty_request=Decimal(position["position_qty"] / 1000).quantize(
                            self.symbol_base_ticks[position["symbol"]],
                            rounding=ROUND_DOWN,
                        ),
                    )
                    logger.info("orderly executor claim_insurance_fund json: %s", json)
                    await self.orderly_client.claim_insurance_fund(json)
            else:
                logger.error(f"Unknown liquidation type: {action['type']}")

            # wait for position transfer
            await asyncio.sleep(15)

            positions = await self.orderly_client.get_all_positions()
            logger.info("orderly executor positions: %s", positions)
            for position in positions["data"]["rows"]:
                side = ""
                if position["position_qty"] > 0:
                    side = "SELL"
                elif position["position_qty"] < 0:
                    side = "BUY"
                else:
                    logger.error(f"Unknown position qty: {position['position_qty']}")
                    return
                json = dict(
                    symbol=position["symbol"],
                    order_type="MARKET",
                    side=side,
                    order_quantity=abs(position["position_qty"]),
                )
                logger.info("orderly executor create_order json: %s", json)
                res = await self.orderly_client.create_order(json)
                logger.info("orderly executor create_order res: %s", res)
        else:
            logger.error(f"Unknown action type: {action['action_type']}")
            return
