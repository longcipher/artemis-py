import inspect
from typing import Optional

import ccxt.pro

from liquidation_searcher.utils.log import logger


class Woo:
    api_key: str
    secret_key: str
    uid: str
    exchange: ccxt.pro.woo

    def __init__(
        self,
        api_key: str,
        secret_key: str,
        uid: str,
        testnet: bool = False,
        proxy: Optional[str] = None,
    ):
        self.api_key = api_key
        self.secret_key = secret_key
        self.uid = uid
        if proxy is None:
            self.exchange = ccxt.pro.woo(
                {
                    "apiKey": self.api_key,
                    "secret": self.secret_key,
                    "uid": self.uid,
                    "timeout": 30000,
                    "options": {
                        "defaultType": "future",
                    },
                }
            )
        else:
            self.exchange = ccxt.pro.woo(
                {
                    "apiKey": self.api_key,
                    "secret": self.secret_key,
                    "uid": self.uid,
                    "aiohttp_proxy": proxy,
                    "timeout": 30000,
                    "options": {
                        "defaultType": "future",
                    },
                }
            )
        if testnet:
            logger.info("set woo to testnet")
            self.exchange.set_sandbox_mode(True)

    async def open(self):
        self.exchange.open()
        await self.exchange.load_markets()

    async def close(self):
        await self.exchange.close()

    def ccxt(self):
        return self.exchange

    def all_methods(self):
        members = inspect.getmembers(self.exchange)
        result = []
        for name, member in members:
            if not name.startswith("__"):
                if inspect.ismethod(member):
                    result.append(name)
        return result

    def all_properties(self):
        members = inspect.getmembers(self.exchange)
        result = []
        for name, member in members:
            if not name.startswith("__"):
                if not inspect.ismethod(member):
                    result.append(name)
        return result

    def exchange_info(self):
        return self.exchange.describe()

    async def all_apis(self):
        return self.exchange.api

    async def watch_order_book(self):
        while True:
            try:
                orderbook = await self.exchange.watch_order_book(self.symbol, limit=5)
                logger.info(orderbook["bids"][0], orderbook["asks"][0])
            except Exception as e:
                logger.error(type(e).__name__, str(e))
                break
