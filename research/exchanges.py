import argparse
import asyncio
import logging
import time
from argparse import Namespace
from pprint import pprint

import yaml

from liquidation_searcher.exchanges.binance import Binance
from liquidation_searcher.exchanges.orderly import Orderly
from liquidation_searcher.exchanges.woo import Woo

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
    subparsers = parser.add_subparsers(
        title="list all perp market symbols",
        dest="subcommand",
        description="list all perp market symbols",
    )
    subparsers.add_parser("list_perp_symbols", help="list all perp market symbols")
    args = parser.parse_args()
    return args


async def woo_orderbook(config):
    symbol = config["woo"]["symbol"]
    api_key = config["woo"]["api_key"]
    secret_key = config["woo"]["secret_key"]
    proxy = config["app"]["proxy"]
    testnet = config["woo"]["testnet"]
    woo = Woo(symbol, api_key, secret_key, proxy, testnet)
    woo.open()
    await woo.watch_order_book()
    await woo.close()


async def orderly_orderbook(config):
    symbol = config["orderly"]["symbol"]
    orderly_key = config["orderly"]["orderly_key"]
    orderly_secret = config["orderly"]["orderly_secret"]
    trading_key = config["orderly"]["trading_key"]
    trading_secret = config["orderly"]["trading_secret"]
    account_id = config["orderly"]["account_id"]
    common_account_id = config["orderly"]["common_account_id"]
    orderly_testnet = config["orderly"]["testnet"]
    orderly = Orderly(
        symbol,
        orderly_key,
        orderly_secret,
        trading_key,
        trading_secret,
        account_id,
        common_account_id,
        orderly_testnet,
    )
    await orderly.watch_boo()
    while True:
        time.sleep(1)


async def binance_orderbook(args, config):
    symbol = config["binance"]["symbol"]
    api_key = config["binance"]["api_key"]
    secret_key = config["binance"]["secret_key"]
    proxy = config["app"]["proxy"]
    testnet = config["binance"]["testnet"]

    binance = Binance(symbol, api_key, secret_key, proxy, testnet)

    binance.open()
    if args.subcommand == "list_perp_symbols":
        symbols = await binance.fetch_perp_symbols()
        pprint(symbols)
        await binance.close()
        return

    # balance = await binance.fetch_free_balance()
    # logger.info("fetch free balance: {}".format(balance))

    orderbook = await binance.fetch_order_book()
    logger.info("fetch order book: {}".format(orderbook))
    funding_rate = await binance.fetch_funding_rate()
    logger.info("fetch funding rate: {}".format(funding_rate))

    await binance.watch_order_book()

    await binance.close()


async def main(args: Namespace):
    logger.info("parsing config file: {args.config}")

    with open(args.config, "r") as config_file:
        config = yaml.safe_load(config_file)
    logger.info("pared configs: {}".format(config))

    # await orderly_orderbook(config)
    # await binance_orderbook(args, config)
    await woo_orderbook(config)


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
