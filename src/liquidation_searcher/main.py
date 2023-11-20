import argparse
import asyncio
import logging
from argparse import Namespace

import yaml

from liquidation_searcher.collectors.orderly_liquidation import (
    OrderlyLiquidationCollector,
)
from liquidation_searcher.engine.core import Engine
from liquidation_searcher.executors.orderly_executor import OrderlyExecutor
from liquidation_searcher.strategies.direct import DirectStrategy

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


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
    logger.info("parsing config file: %s", args.config)

    with open(args.config, "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    logger.info("parsed configs: %s", config)

    orderly_account_id = config["orderly"]["account_id"]
    orderly_ws_public_endpoint = config["orderly"]["ws_public_endpoint"]
    orderly_rest_endpoint = config["orderly"]["rest_endpoint"]
    orderly_key = config["orderly"]["orderly_key"]
    orderly_secret = config["orderly"]["orderly_secret"]

    engine = Engine()
    orderly_liquidation_collector = OrderlyLiquidationCollector(
        account_id=orderly_account_id,
        endpoint=orderly_ws_public_endpoint,
    )
    engine.add_collector(orderly_liquidation_collector)
    direct_strategy = DirectStrategy()
    engine.add_strategy(direct_strategy)
    orderly_executor = OrderlyExecutor(
        account_id=orderly_account_id,
        endpoint=orderly_rest_endpoint,
        orderly_key=orderly_key,
        orderly_secret=orderly_secret,
    )
    engine.add_executor(orderly_executor)
    await engine.run()


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
