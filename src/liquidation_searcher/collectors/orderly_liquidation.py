import asyncio

from orderly_sdk.ws import OrderlyPublicWsManager

from liquidation_searcher.types import Collector
from liquidation_searcher.utils.event_loop import get_loop


class OrderlyLiquidationCollector(Collector):
    def __init__(self, account_id, endpoint, loop=None):
        self.orderly_ws_client = OrderlyPublicWsManager(
            account_id=account_id,
            endpoint=endpoint,
        )
        self.orderly_ws_client.subscribe("liquidation")
        self.queue = asyncio.Queue(maxsize=512)
        self.loop = loop or get_loop()

    async def _run(self, timeout=30):
        self.orderly_ws_client.start(timeout=timeout)
        while True:
            res = await self.orderly_ws_client.recv("liquidation")
            await self.queue.put(res)

    def start(self, timeout=30):
        self.loop.call_soon_threadsafe(asyncio.create_task, self._run(timeout))

    async def get_event_stream(self):
        await asyncio.wait_for(self.queue.get(), timeout=None)
