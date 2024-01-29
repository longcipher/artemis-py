import argparse
import asyncio
from argparse import Namespace
from pprint import pprint

import yaml

from liquidation_searcher.exchanges.woo import Woo


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


async def woo_orderbook(config):
    api_key = config["woo"]["api_key"]
    secret_key = config["woo"]["secret_key"]
    proxy = config["app"]["proxy"]
    testnet = config["woo"]["testnet"]
    uid = config["woo"]["app_id"]

    woo = Woo(api_key, secret_key, uid, testnet, proxy)
    await woo.open()
    # await woo.watch_order_book()
    # markets = await woo.ccxt().fetch_markets()
    # logger.info("markets: {}", markets)
    # for m in markets:
    #     logger.info("market: {}", m)

    # order_book = await woo.ccxt().fetch_order_book(symbol, limit=None, params={})
    # logger.info("order_book: {}", order_book)

    # trades = await woo.ccxt().fetch_trades(symbol, since=None, limit=None, params={})
    # logger.info("trades: {}", trades)
    # for t in trades:
    #     logger.info("time: {}", t["datetime"])

    # ohlcv = await woo.ccxt().fetch_ohlcv(
    #     symbol, timeframe="1m", since=None, limit=None, params={}
    # )
    # logger.info("ohlcv: {}", ohlcv)

    # markets = await woo.ccxt().load_markets()
    # logger.info("loaded markets: {}", markets)

    # all_methods = woo.all_methods()
    # logger.info("all methods: {}", all_methods)

    # all_properties = woo.all_properties()
    # logger.info("all properties: {}", all_properties)
    # all_options = woo.all_options()
    # logger.info("all options: {}", all_options)
    # exchange_info = woo.exchange_info()
    # logger.info("exchange info: {}", exchange_info)
    # pprint(exchange_info)
    # markets = await woo.load_markets()
    # pprint(markets)

    # m = woo.ccxt().markets["BTC/USDT"]
    # m = woo.ccxt().market("BTC/USDT")
    # pprint(m)

    d = woo.ccxt().symbols
    pprint(d)

    # s = woo.ccxt().symbols
    # pprint(s)

    await woo.close()


async def main(args: Namespace):
    print("parsing config file: {}", args.config)

    with open(args.config, "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    print("parsed configs: {}", config)

    await woo_orderbook(config)

    # port = config["app"]["port"]
    # level = config["app"]["level"]
    # set_level(level)
    # orderly_account_id = config["orderly"]["account_id"]
    # orderly_ws_public_endpoint = config["orderly"]["ws_public_endpoint"]
    # orderly_rest_endpoint = config["orderly"]["rest_endpoint"]
    # orderly_key = os.getenv("ORDERLY_KEY")
    # orderly_secret = os.getenv("ORDERLY_SECRET")
    # if orderly_key is None or orderly_secret is None:
    #     logger.error("ORDERLY_KEY or ORDERLY_SECRET is not set")
    #     raise ValueError("ORDERLY_KEY or ORDERLY_SECRET is not set")
    # max_notional = config["orderly"]["max_notional"]
    # liquidation_symbols = config["orderly"]["liquidation_symbols"]

    # loop = get_loop()

    # engine = Engine()
    # orderly_liquidation_ws_collector = OrderlyLiquidationWsCollector(
    #     account_id=orderly_account_id,
    #     endpoint=orderly_ws_public_endpoint,
    #     loop=loop,
    # )
    # engine.add_collector(orderly_liquidation_ws_collector)
    # orderly_liquidation_rest_collector = OrderlyLiquidationRestCollector(
    #     account_id=orderly_account_id,
    #     endpoint=orderly_rest_endpoint,
    #     loop=loop,
    # )
    # engine.add_collector(orderly_liquidation_rest_collector)
    # orderly_hedge_strategy = OrderlyHedgeStrategy()
    # engine.add_strategy(orderly_hedge_strategy)
    # orderly_executor = OrderlyExecutor(
    #     account_id=orderly_account_id,
    #     endpoint=orderly_rest_endpoint,
    #     orderly_key=orderly_key,
    #     orderly_secret=orderly_secret,
    #     max_notional=max_notional,
    #     liquidation_symbols=liquidation_symbols,
    # )
    # engine.add_executor(orderly_executor)
    # # only for k8s health check now
    # await run_web(port)
    # await engine.run()


if __name__ == "__main__":
    asyncio.run(main(parse_args()), debug=True)
