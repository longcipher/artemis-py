import asyncio
from typing import List

from liquidation_searcher.types import Collector, Executor, Strategy
from liquidation_searcher.utils.log import logger


class Engine:
    collectors: List[Collector]
    strategies: List[Strategy]
    executors: List[Executor]
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
        self.strategies = []
        self.executors = []
        self.event_channel_capacity = event_channel_capacity
        self.action_channel_capacity = action_channel_capacity
        self.event_queue = asyncio.Queue(self.event_channel_capacity)
        self.action_queue = asyncio.Queue(self.action_channel_capacity)

    def add_collector(self, collector: Collector):
        self.collectors.append(collector)

    def add_strategy(self, strategy: Strategy):
        self.strategies.append(strategy)

    def add_executor(self, executor: Executor):
        self.executors.append(executor)

    async def run_collector(self, collector: Collector):
        collector.start(timeout=30)
        while True:
            event = await collector.get_event_stream()
            if event is not None:
                logger.info("engine collector event: {}", event)
                await self.event_queue.put(event)
            await asyncio.sleep(0.1)

    async def run_strategy(self, strategy: Strategy):
        await strategy.sync_state()
        while True:
            if not self.event_queue.empty():
                event = await self.event_queue.get()
                logger.info("engine strategy event: {}", event)
                if event is not None:
                    action = await strategy.process_event(event)
                    await self.action_queue.put(action)
            await asyncio.sleep(0.1)

    async def run_executor(self, executor: Executor):
        await executor.sync_state()
        while True:
            if not self.action_queue.empty():
                action = await self.action_queue.get()
                logger.info("engine executor action: {}", action)
                if action is not None:
                    logger.info("executor action: {}", action)
                    await executor.execute(action)
            await asyncio.sleep(0.1)

    async def run(self):
        tasks = []
        for executor in self.executors:
            tasks.append(asyncio.create_task(self.run_executor(executor)))
        for strategy in self.strategies:
            tasks.append(asyncio.create_task(self.run_strategy(strategy)))
        for collector in self.collectors:
            tasks.append(asyncio.create_task(self.run_collector(collector)))
        await asyncio.gather(*tasks)
