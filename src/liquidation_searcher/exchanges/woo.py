import logging

import ccxt.pro

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class Woo:
    symbol: str
    base_symbol: str
    quote_symbol: str
    api_key: str
    secret_key: str
    exchange: ccxt.pro.woo

    def __init__(
        self,
        symbol: str,
        api_key: str,
        secret_key: str,
        proxy: str,
        testnet: bool = False,
    ):
        self.base_symbol, self.quote_symbol = symbol.split("/")
        self.symbol = (
            "PERP_" + self.base_symbol.upper() + "_" + self.quote_symbol.upper()
        )
        self.api_key = api_key
        self.secret_key = secret_key
        self.exchange = ccxt.pro.woo(
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
            logger.info("set woo to testnet")
            self.exchange.set_sandbox_mode(True)
        logger.info("symbol: {}".format(self.symbol))

    def open(self):
        self.exchange.open()

    async def close(self):
        await self.exchange.close()

    async def watch_order_book(self):
        while True:
            try:
                orderbook = await self.exchange.watch_order_book(self.symbol, limit=5)
                print(orderbook["bids"][0], orderbook["asks"][0])
            except Exception as e:
                logger.error(type(e).__name__, str(e))
                break
                break
