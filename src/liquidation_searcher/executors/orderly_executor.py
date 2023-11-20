import asyncio
import logging

from orderly_sdk.rest import AsyncClient

from liquidation_searcher.types import Executor

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class OrderlyExecutor(Executor):
    def __init__(self, account_id, orderly_key, orderly_secret, endpoint):
        self.orderly_client = AsyncClient(
            account_id=account_id,
            orderly_key=orderly_key,
            orderly_secret=orderly_secret,
            endpoint=endpoint,
        )

    async def execute(self, action):
        # "data":[
        #     {
        #        "liquidationId":1,
        #        "timestamp":1684821114917,
        #        "type":"liquidated",
        #        "positionsByPerp":[
        #           {
        #              "symbol":"PERP_NEAR_USDC",
        #              "positionQty":12.6,
        #              "liquidatorFee":0.0175
        #           }
        #        ]
        #     },
        #     ...
        #  ]
        for liquidation in action:
            if liquidation["type"] == "liquidated":
                json = dict(
                    liquidation_id=liquidation["liquidationId"],
                    ratio_qty_request=1,
                )
                await self.orderly_client.claim_liquidated_positions(json)
            elif liquidation["type"] == "claim":
                for position in liquidation["positionsByPerp"]:
                    json = dict(
                        liquidation_id=liquidation["liquidationId"],
                        symbol=position["symbol"],
                        qty_request=position["positionQty"],
                    )
                    await self.orderly_client.claim_insurance_fund(json)
            else:
                logger.error(f"Unknown liquidation type: {liquidation['type']}")
            await asyncio.sleep(5)
            positions = await self.orderly_client.get_all_positions()
            for position in positions["rows"]:
                side = ""
                if position["position_qty"] > 0:
                    side = "SELL"
                elif position["position_qty"] < 0:
                    side = "BUY"
                else:
                    logger.error(f"Unknown position qty: {position['position_qty']}")
                if side != "":
                    json = dict(
                        symbol=position["symbol"],
                        order_type="MARKET",
                        side=side,
                    )
                    await self.orderly_client.create_order(json)
