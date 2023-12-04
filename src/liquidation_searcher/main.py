import argparse
import asyncio
from argparse import Namespace

import yaml

from liquidation_searcher.collectors.orderly_liquidation_rest import (
    OrderlyLiquidationRestCollector,
)
from liquidation_searcher.collectors.orderly_liquidation_ws import (
    OrderlyLiquidationWsCollector,
)
from liquidation_searcher.engine.core import Engine
from liquidation_searcher.executors.orderly_executor import OrderlyExecutor
from liquidation_searcher.router import run_web
from liquidation_searcher.strategies.direct import DirectStrategy
from liquidation_searcher.utils.event_loop import get_loop
from liquidation_searcher.utils.log import logger, set_level


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
    set_level("INFO")
    logger.info("parsing config file: {}", args.config)

    with open(args.config, "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    logger.info("parsed configs: {}", config)

    orderly_account_id = config["orderly"]["account_id"]
    orderly_ws_public_endpoint = config["orderly"]["ws_public_endpoint"]
    orderly_rest_endpoint = config["orderly"]["rest_endpoint"]
    orderly_key = config["orderly"]["orderly_key"]
    orderly_secret = config["orderly"]["orderly_secret"]
    port = config["app"]["port"]

    loop = get_loop()

    engine = Engine()
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
    direct_strategy = DirectStrategy()
    engine.add_strategy(direct_strategy)
    orderly_executor = OrderlyExecutor(
        account_id=orderly_account_id,
        endpoint=orderly_rest_endpoint,
        orderly_key=orderly_key,
        orderly_secret=orderly_secret,
    )
    engine.add_executor(orderly_executor)
    # only for k8s health check now
    await run_web(port)
    await engine.run()


if __name__ == "__main__":
    asyncio.run(main(parse_args()), debug=True)
