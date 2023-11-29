import logging
from datetime import datetime

from liquidation_searcher.types import ActionType, EventType, Strategy

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class DirectStrategy(Strategy):
    def __init__(self):
        pass

    async def sync_state(self):
        pass

    async def process_event(self, event):
        logger.info("DirectStrategy process_event: %s", event)
        ts = event["timestamp"]
        # filter outdated events
        if datetime.now().timestamp() * 1000 - ts > 300:
            return
        if event["event_type"] == EventType.ORDERLY_LIQUIDATION_REST:
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
            return action
        elif event["event_type"] == EventType.ORDERLY_LIQUIDATION_WS:
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
            return action
        else:
            logger.warning("Unknown event type: %s", event["event_type"])
            return
