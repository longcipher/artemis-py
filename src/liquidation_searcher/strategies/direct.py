import logging
from datetime import datetime

from liquidation_searcher.types import Strategy

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
        ts = event["timestamp"]
        # filter outdated events
        if datetime.now().timestamp() * 1000 - ts > 300:
            return
        action = event
        return action
