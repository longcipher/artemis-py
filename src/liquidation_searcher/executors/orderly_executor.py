import asyncio
from decimal import ROUND_DOWN, Decimal
from typing import Any, Dict, Tuple

from orderly_sdk.rest import AsyncClient

from liquidation_searcher.types import ActionType, Executor, LiquidationType
from liquidation_searcher.utils.log import logger


class OrderlyExecutor(Executor):
    symbol_info: Dict[str, Any]
    claim_percent: float
    symbol_qty: Dict[str, Any]

    def __init__(
        self,
        account_id,
        orderly_key,
        orderly_secret,
        endpoint,
        claim_percent,
        symbol_qty,
    ):
        self.orderly_client = AsyncClient(
            account_id=account_id,
            orderly_key=orderly_key,
            orderly_secret=orderly_secret,
            endpoint=endpoint,
        )
        self.symbol_info = dict()
        self.claim_percent = claim_percent
        self.symbol_qty = dict()
        for symbol, info in symbol_qty.items():
            self.symbol_qty[symbol] = {
                "max_qty": info["max_qty"],
                "min_qty": info["min_qty"],
            }

    async def sync_state(self):
        symbols = await self.orderly_client.get_available_symbols()
        for symbol in symbols["data"]["rows"]:
            self.symbol_info[symbol["symbol"]] = {
                "base_tick": str(symbol["base_tick"]),
                "base_min": str(symbol["base_min"]),
                "min_notional": str(symbol["min_notional"]),
            }
        balance = await self.orderly_client.get_current_holding()
        logger.info("orderly executor balance: {}", balance)
        info = await self.orderly_client.get_account_info()
        logger.info("orderly executor account info: {}", info)

    async def execute(self, action):
        if action["action_type"] == ActionType.ORDERLY_LIQUIDATION_ORDER:
            for position in action["positions_by_perp"]:
                if position["symbol"] not in self.symbol_qty:
                    logger.error(
                        "orderly executor claim ignored symbol: {}, not configed in symbol_qty",
                        position["symbol"],
                    )
                    continue
                (qty, ratio) = self.calc_claim_qty(
                    position["symbol"],
                    position["position_qty"],
                )
                if qty == 0 or ratio == 0:
                    logger.error(
                        "orderly executor calc_claim_qty failed symbol: {}, qty: {}",
                        position["symbol"],
                        position["position_qty"],
                    )
                    continue
                if action["type"] == LiquidationType.LIQUIDATED:
                    json = dict(
                        liquidation_id=action["liquidation_id"],
                        ratio_qty_request=ratio,
                    )
                    logger.info(
                        "orderly executor claim_liquidated_positions json: {}", json
                    )
                    res = await self.orderly_client.claim_liquidated_positions(json)
                    logger.info(
                        "orderly executor claim_liquidated_positions res: {}", res
                    )

                elif action["type"] == LiquidationType.CLAIM:
                    json = dict(
                        liquidation_id=action["liquidation_id"],
                        symbol=position["symbol"],
                        qty_request=self.format_qty(position["symbol"], qty),
                    )
                    logger.info("orderly executor claim_insurance_fund json: {}", json)
                    res = await self.orderly_client.claim_insurance_fund(json)
                    logger.info("orderly executor claim_insurance_fund res: {}", res)

                else:
                    logger.error(f"Unknown liquidation type: {action['type']}")

            # wait for position transfer
            await asyncio.sleep(15)

            positions = await self.orderly_client.get_all_positions()
            logger.info("orderly executor positions: {}", positions)
            for position in positions["data"]["rows"]:
                side = ""
                if position["position_qty"] > 0:
                    side = "SELL"
                elif position["position_qty"] < 0:
                    side = "BUY"
                else:
                    logger.debug(
                        f"Unknown position symbol: {position['symbol']}, qty: {position['position_qty']}"
                    )
                    continue
                json = dict(
                    symbol=position["symbol"],
                    order_type="MARKET",
                    side=side,
                    order_quantity=self.format_qty(
                        position["symbol"], abs(position["position_qty"])
                    ),
                    # reduce_only=True,
                )
                logger.info("orderly executor create_order json: {}", json)
                res = await self.orderly_client.create_order(json)
                logger.info("orderly executor create_order res: {}", res)
        else:
            logger.error(f"Unknown action type: {action['action_type']}")
            return

    def calc_claim_qty(
        self,
        symbol,
        position_qty,
    ) -> Tuple[float, float]:
        if position_qty == 0:
            return (0, 0)
        qty = abs(position_qty * self.claim_percent)
        if qty < self.symbol_qty[symbol]["min_qty"]:
            qty = self.symbol_qty[symbol]["min_qty"]
        elif qty > self.symbol_qty[symbol]["max_qty"]:
            qty = self.symbol_qty[symbol]["max_qty"]
        else:
            return (0, 0)
        ratio = abs(
            float(
                Decimal(str(qty / position_qty)).quantize(
                    Decimal("0.001"),
                    rounding=ROUND_DOWN,
                )
            )
        )
        qty = qty if position_qty > 0 else -qty
        return (qty, ratio)

    def format_qty(self, symbol, qty):
        return float(
            Decimal(str(qty)).quantize(
                Decimal(self.symbol_info[symbol]["base_tick"]),
                rounding=ROUND_DOWN,
            )
        )
