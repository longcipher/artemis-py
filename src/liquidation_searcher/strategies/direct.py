import logging
from typing import Set

from liquidation_searcher.types import ActionType, EventType, LiquidationType, Strategy

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class DirectStrategy(Strategy):
    processed_liquidations: Set[int]

    def __init__(self):
        self.processed_liquidations = set()

    async def sync_state(self):
        pass

    async def process_event(self, event):
        logger.info("DirectStrategy process_event: %s", event)
        # ts = event["timestamp"]
        # filter outdated events
        # if datetime.now().timestamp() * 1000 - ts > 300:
        #     return
        if event["event_type"] == EventType.ORDERLY_LIQUIDATION_REST:
            if event["liquidation_id"] in self.processed_liquidations:
                return
            action = {
                "action_type": ActionType.ORDERLY_LIQUIDATION_ORDER,
                "timestamp": event["timestamp"],
                "type": event["type"],
                "liquidation_id": event["liquidation_id"],
                "positions_by_perp": [],
            }
            for position in event["positions_by_perp"]:
                action["positions_by_perp"].append(
                    {
                        "symbol": position["symbol"],
                        "position_qty": position["position_qty"],
                        "liquidator_fee": position["liquidator_fee"],
                    }
                )
                # only process the first position
                if action["type"] == LiquidationType.CLAIM:
                    break
            logger.info("DirectStrategy rest action: %s", action)
            self.processed_liquidations.add(action["liquidation_id"])
            return action
        elif event["event_type"] == EventType.ORDERLY_LIQUIDATION_WS:
            if event["liquidationId"] in self.processed_liquidations:
                return
            action = {
                "action_type": ActionType.ORDERLY_LIQUIDATION_ORDER,
                "timestamp": event["timestamp"],
                "type": event["type"],
                "liquidation_id": event["liquidationId"],
                "positions_by_perp": [],
            }
            for position in event["positions_by_perp"]:
                action["positions_by_perp"].append(
                    {
                        "symbol": position["symbol"],
                        "position_qty": position["positionQty"],
                        "liquidator_fee": position["liquidatorFee"],
                    }
                )
                # only process the first position
                if action["type"] == LiquidationType.CLAIM:
                    break
            logger.info("DirectStrategy ws action: %s", action)
            self.processed_liquidations.add(action["liquidation_id"])
            return action
        else:
            logger.warning("Unknown event type: %s", event["event_type"])
            return
