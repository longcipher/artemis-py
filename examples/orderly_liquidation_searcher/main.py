"""
Orderly Liquidation Searcher Example

This example demonstrates how to use the Artemis framework to build a 
liquidation searcher for the Orderly Network. It shows the complete workflow:

1. Collect liquidation events from Orderly's REST and WebSocket APIs
2. Process events to identify profitable liquidation opportunities
3. Execute liquidation claims and hedge positions

Usage:
    python main.py -c ../../conf/staging.yml

Requirements:
    - orderly-sdk>=0.2.2
    - Environment variables: ORDERLY_KEY, ORDERLY_SECRET
"""

import argparse
import asyncio
import os
from argparse import Namespace

import yaml

from artemis import Engine
from artemis.utils.log import logger, set_level
from artemis.utils.event_loop import get_loop

from collectors.orderly_liquidation_rest import OrderlyLiquidationRestCollector
from collectors.orderly_liquidation_ws import OrderlyLiquidationWsCollector
from strategies.orderly_hedge import OrderlyHedgeStrategy
from executors.orderly_executor import OrderlyExecutor
from router import run_web


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description="Liquid Searcher")
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        required=True,
        help="config file",
    )
    args = parser.parse_args()
    return args


async def main(args: Namespace):
    """Main entry point for the liquidation searcher."""
    logger.info("Starting Orderly Liquidation Searcher...")
    logger.info(f"Parsing config file: {args.config}")

    # Load configuration
    with open(args.config, "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    logger.info(f"Loaded configuration: {config}")

    # Extract configuration values
    port = config["app"]["port"]
    level = config["app"]["level"]
    set_level(level)
    
    orderly_account_id = config["orderly"]["account_id"]
    orderly_ws_public_endpoint = config["orderly"]["ws_public_endpoint"]
    orderly_rest_endpoint = config["orderly"]["rest_endpoint"]
    max_notional = config["orderly"]["max_notional"]
    liquidation_symbols = config["orderly"]["liquidation_symbols"]

    # Get API credentials from environment
    orderly_key = os.getenv("ORDERLY_KEY")
    orderly_secret = os.getenv("ORDERLY_SECRET")
    if orderly_key is None or orderly_secret is None:
        logger.error("ORDERLY_KEY or ORDERLY_SECRET is not set")
        raise ValueError("ORDERLY_KEY or ORDERLY_SECRET is not set")

    # Initialize the Artemis engine
    loop = get_loop()
    engine = Engine()

    # Add collectors
    orderly_liquidation_ws_collector = OrderlyLiquidationWsCollector(
        account_id=orderly_account_id,
        endpoint=orderly_ws_public_endpoint,
        loop=loop,
    )
    engine.add_collector(orderly_liquidation_ws_collector)

    orderly_liquidation_rest_collector = OrderlyLiquidationRestCollector(
        account_id=orderly_account_id,
        endpoint=orderly_rest_endpoint,
        loop=loop,
    )
    engine.add_collector(orderly_liquidation_rest_collector)

    # Add strategy
    orderly_hedge_strategy = OrderlyHedgeStrategy()
    engine.add_strategy(orderly_hedge_strategy)

    # Add executor
    orderly_executor = OrderlyExecutor(
        account_id=orderly_account_id,
        endpoint=orderly_rest_endpoint,
        orderly_key=orderly_key,
        orderly_secret=orderly_secret,
        max_notional=max_notional,
        liquidation_symbols=liquidation_symbols,
    )
    engine.add_executor(orderly_executor)

    # Start health check server for monitoring
    await run_web(port)
    
    # Start the engine
    await engine.run()


if __name__ == "__main__":
    asyncio.run(main(parse_args()), debug=True)
