import asyncio
from typing import List

from liquidation_searcher.types import Collector, Executor, Strategy


class Engine:
    collectors: List[Collector]
    strategy: Strategy
    executor: Executor
    event_channel_capacity: int
    action_channel_capacity: int
    event_queue: asyncio.Queue
    action_queue: asyncio.Queue

    def __init__(
        self,
        event_channel_capacity: int = 512,
        action_channel_capacity: int = 512,
    ):
        self.collectors = []
        self.event_channel_capacity = event_channel_capacity
        self.action_channel_capacity = action_channel_capacity
        self.event_queue = asyncio.Queue(self.event_channel_capacity)
        self.action_queue = asyncio.Queue(self.action_channel_capacity)

    def add_collector(self, collector: Collector):
        self.collectors.append(collector)

    def add_strategy(self, strategy: Strategy):
        self.strategy = strategy

    def add_executor(self, executor: Executor):
        self.executor = executor

    async def run_collector(self, collector: Collector):
        collector.start(timeout=30)
        while True:
            event = await collector.get_event_stream()
            await self.event_queue.put(event)

    async def run_strategy(self):
        while True:
            event = await self.event_queue.get()
            action = await self.strategy.process_event(event)
            await self.action_queue.put(action)

    async def run_executor(self):
        while True:
            action = await self.action_queue.get()
            await self.executor.execute(action)

    async def run(self):
        tasks = []
        tasks.append(asyncio.create_task(self.run_executor()))
        tasks.append(asyncio.create_task(self.run_strategy()))
        for collector in self.collectors:
            tasks.append(asyncio.create_task(self.run_collector(collector)))
        await asyncio.gather(*tasks)
