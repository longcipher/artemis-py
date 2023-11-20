import logging

import ccxt.pro

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class Binance:
    symbol: str
    base_symbol: str
    quote_symbol: str
    api_key: str
    secret_key: str
    exchange: ccxt.pro.binance

    def __init__(
        self,
        symbol: str,
        api_key: str,
        secret_key: str,
        proxy: str,
        testnet: bool = False,
    ):
        self.symbol = symbol
        self.base_symbol, self.quote_symbol = symbol.split("/")
        self.api_key = api_key
        self.secret_key = secret_key
        self.exchange = ccxt.pro.binance(
            {
                "apiKey": self.api_key,
                "secret": self.secret_key,
                "enableRateLimit": True,
                "aiohttp_proxy": proxy,
                "options": {
                    "defaultType": "future",
                },
            }
        )
        if testnet:
            logger.info("set binance to testnet")
            self.exchange.set_sandbox_mode(True)

    def open(self):
        self.exchange.open()

    async def close(self):
        await self.exchange.close()

    async def fetch_free_balance(self):
        balance = await self.exchange.fetch_free_balance()
        return {
            self.base_symbol: balance[self.base_symbol],
            self.quote_symbol: balance[self.quote_symbol],
        }

    async def fetch_order_book(self):
        return await self.exchange.fetch_order_book(self.symbol, limit=5)

    async def fetch_perp_symbols(self):
        symbols = await self.exchange.fetch_markets()
        perp_symbols = [
            symbol["id"]
            for symbol in symbols
            if "_PERP" in symbol["id"] and symbol["active"]
        ]
        return perp_symbols

    async def fetch_funding_rate(self):
        return await self.exchange.fetch_funding_rate(self.symbol)

    async def sell(self, amount, price):
        await self.exchange.create_limit_sell_order(self.symbol, amount, price)
        logger.info(
            "Sold {amount} {self.base_symbol}, price: {price} {self.quote_symbol} on Binance: {res}"
        )

    async def buy(self, amount, price):
        await self.exchange.create_limit_buy_order(self.symbol, amount, price)
        logger.info(
            "Bought {amount} {self.base_symbol}, price: {price} {self.quote_symbol} on Binance: {res}"
        )

    async def watch_order_book(self):
        while True:
            try:
                orderbook = await self.exchange.watch_order_book(self.symbol, limit=5)
                print(orderbook["bids"][0], orderbook["asks"][0])
            except Exception as e:
                logger.error(type(e).__name__, str(e))
                break
                logger.error(type(e).__name__, str(e))
                break
