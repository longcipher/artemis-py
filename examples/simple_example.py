#!/usr/bin/env python3
"""
Simple example demonstrating the Artemis framework.

This example shows a basic setup with:
- A simple collector that generates mock price events
- A strategy that detects price changes
- An executor that logs the actions
"""

import asyncio
import random
from typing import Any, Dict, Optional

from artemis import Collector, Engine, Executor, Strategy
from artemis.utils.log import logger, set_level


class MockPriceCollector(Collector):
    """A simple collector that generates mock price events."""

    def __init__(self, symbol: str = "BTC/USDT"):
        self.symbol = symbol
        self.price = 50000.0  # Starting price
        self.is_running = False

    def start(self, timeout: Optional[int] = None) -> None:
        """Start generating price events."""
        self.is_running = True
        logger.info(f"Started price collector for {self.symbol}")

    async def get_event_stream(self) -> Optional[Dict[str, Any]]:
        """Generate a mock price event."""
        if not self.is_running:
            return None

        # Simulate price changes
        change = random.uniform(-0.02, 0.02)  # ±2% change
        self.price *= (1 + change)

        return {
            "event_type": "price_update",
            "symbol": self.symbol,
            "price": round(self.price, 2),
            "change": round(change * 100, 2),  # percentage
            "timestamp": asyncio.get_event_loop().time()
        }


class PriceChangeStrategy(Strategy):
    """A simple strategy that detects significant price changes."""

    def __init__(self, threshold: float = 1.0):
        self.threshold = threshold  # Threshold for significant change (%)
        self.last_prices: Dict[str, float] = {}

    async def sync_state(self) -> None:
        """Initialize strategy state."""
        logger.info(f"Initialized price change strategy with {self.threshold}% threshold")

    async def process_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process price events and detect significant changes."""
        if event.get("event_type") != "price_update":
            return None

        symbol = event["symbol"]
        current_price = event["price"]
        change = abs(event.get("change", 0))

        # Store current price for future reference
        self.last_prices[symbol] = current_price

        # Check if change exceeds threshold
        if change >= self.threshold:
            direction = "UP" if event.get("change", 0) > 0 else "DOWN"
            logger.info(f"Significant price change detected: {symbol} {direction} {change:.2f}%")

            return {
                "action_type": "alert",
                "symbol": symbol,
                "price": current_price,
                "change": change,
                "direction": direction,
                "message": f"{symbol} moved {direction} by {change:.2f}%"
            }

        return None


class AlertExecutor(Executor):
    """A simple executor that logs alerts."""

    def __init__(self):
        self.alert_count = 0

    async def sync_state(self) -> None:
        """Initialize executor state."""
        logger.info("Initialized alert executor")

    async def execute(self, action: Dict[str, Any]) -> None:
        """Execute alert actions."""
        if action.get("action_type") == "alert":
            self.alert_count += 1
            message = action.get("message", "Unknown alert")
            logger.warning(f"🚨 ALERT #{self.alert_count}: {message}")

            # In a real implementation, you might:
            # - Send notifications to Discord/Slack
            # - Write to a database
            # - Trigger other systems
            # - Place orders on an exchange


async def main():
    """Main function to run the example."""
    # Set log level to INFO to see the activity
    set_level("INFO")

    logger.info("Starting Artemis Framework Example...")

    # Create the engine
    engine = Engine(
        event_channel_capacity=100,
        action_channel_capacity=100
    )

    # Add components
    collector = MockPriceCollector("BTC/USDT")
    strategy = PriceChangeStrategy(threshold=0.5)  # Alert on 0.5% changes
    executor = AlertExecutor()

    engine.add_collector(collector)
    engine.add_strategy(strategy)
    engine.add_executor(executor)

    # Run the engine
    try:
        logger.info("Engine is running... Press Ctrl+C to stop")
        await engine.run()
    except KeyboardInterrupt:
        logger.info("Stopping example...")


if __name__ == "__main__":
    asyncio.run(main())
