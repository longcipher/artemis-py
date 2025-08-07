"""
Core engine implementation for the Artemis framework.

The Engine class is the central coordinator that manages the lifecycle and
interactions between collectors, strategies, and executors.
"""

import asyncio
from typing import List

from ..types import Collector, Executor, Strategy
from ..utils.log import logger


class Engine:
    """
    The main engine that orchestrates collectors, strategies, and executors.
    
    The engine operates three main loops concurrently:
    1. Collector loop: Gathers events and queues them
    2. Strategy loop: Processes events and generates actions
    3. Executor loop: Executes actions on external systems
    """

    def __init__(
        self,
        event_channel_capacity: int = 512,
        action_channel_capacity: int = 512,
    ):
        """Initialize the engine with configurable queue capacities."""
        self.collectors: List[Collector] = []
        self.strategies: List[Strategy] = []
        self.executors: List[Executor] = []
        self.tasks: List[asyncio.Task] = []
        
        self.event_channel_capacity = event_channel_capacity
        self.action_channel_capacity = action_channel_capacity
        
        # Create async queues for event and action processing
        self.event_queue: asyncio.Queue = asyncio.Queue(self.event_channel_capacity)
        self.action_queue: asyncio.Queue = asyncio.Queue(self.action_channel_capacity)

    def add_collector(self, collector: Collector) -> None:
        """Add a collector to the engine."""
        self.collectors.append(collector)

    def add_strategy(self, strategy: Strategy) -> None:
        """Add a strategy to the engine."""
        self.strategies.append(strategy)

    def add_executor(self, executor: Executor) -> None:
        """Add an executor to the engine."""
        self.executors.append(executor)

    async def run_collectors(self) -> None:
        """Main collector loop."""
        logger.info(f"Starting {len(self.collectors)} collectors...")
        
        # Start all collectors
        for collector in self.collectors:
            collector.start(timeout=30)
        
        # Main collector event loop
        while True:
            for collector in self.collectors:
                try:
                    event = await collector.get_event_stream()
                    if event is not None:
                        logger.debug("Engine received collector event: {}", event)
                        await self.event_queue.put(event)
                except Exception as e:
                    logger.error(f"Error in collector {collector.__class__.__name__}: {e}")
            await asyncio.sleep(0.1)

    async def run_strategies(self) -> None:
        """Main strategy loop."""
        logger.info(f"Starting {len(self.strategies)} strategies...")
        
        # Sync state for all strategies
        for strategy in self.strategies:
            try:
                await strategy.sync_state()
            except Exception as e:
                logger.error(f"Error syncing strategy {strategy.__class__.__name__}: {e}")

        # Main strategy processing loop
        while True:
            if not self.event_queue.empty():
                event = await self.event_queue.get()
                if event is not None:
                    logger.debug("Engine processing strategy event: {}", event)

                    # Process event with all strategies concurrently
                    async def process_event(strategy: Strategy, event):
                        try:
                            action = await strategy.process_event(event)
                            if action is not None:
                                await self.action_queue.put(action)
                        except Exception as e:
                            logger.error(f"Error in strategy {strategy.__class__.__name__}: {e}")

                    tasks = []
                    for strategy in self.strategies:
                        tasks.append(asyncio.create_task(process_event(strategy, event)))
                    
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.1)

    async def run_executors(self) -> None:
        """Main executor loop."""
        logger.info(f"Starting {len(self.executors)} executors...")
        
        # Sync state for all executors
        for executor in self.executors:
            try:
                await executor.sync_state()
            except Exception as e:
                logger.error(f"Error syncing executor {executor.__class__.__name__}: {e}")

        # Main executor processing loop
        while True:
            if not self.action_queue.empty():
                action = await self.action_queue.get()
                if action is not None:
                    logger.debug("Engine executing action: {}", action)

                    # Execute action with all executors concurrently
                    async def execute_action(executor: Executor, action):
                        try:
                            await executor.execute(action)
                        except Exception as e:
                            logger.error(f"Error in executor {executor.__class__.__name__}: {e}")

                    tasks = []
                    for executor in self.executors:
                        tasks.append(asyncio.create_task(execute_action(executor, action)))
                    
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.1)

    async def run(self) -> None:
        """Start the engine and run all components concurrently."""
        logger.info("Starting Artemis Engine...")
        
        # Create and start all component tasks
        self.tasks = [
            asyncio.create_task(self.run_collectors()),
            asyncio.create_task(self.run_strategies()),
            asyncio.create_task(self.run_executors()),
        ]
        
        try:
            # Run all tasks concurrently
            await asyncio.gather(*self.tasks)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            await self.shutdown()
        except Exception as e:
            logger.error(f"Engine error: {e}")
            await self.shutdown()
            raise

    async def shutdown(self) -> None:
        """Gracefully shutdown the engine and all components."""
        logger.info("Shutting down Artemis Engine...")
        
        # Cancel all running tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete cancellation
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("Engine shutdown complete.")
