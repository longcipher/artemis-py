from orderly_sdk.orderly_connector import OrderlyClient
from orderly_sdk.orderly_websocket import OrderlyWebsocketClient


class Orderly:
    symbol: str
    base_symbol: str
    quote_symbol: str
    api_key: str
    secret_key: str
    ws_exchange: OrderlyWebsocketClient
    rest_exchange: OrderlyClient
    account_id: str
    common_account_id: str

    def __init__(
        self,
        symbol: str,
        orderly_key: str,
        orderly_secret: str,
        trading_key: str,
        trading_secret: str,
        account_id: str,
        common_account_id: str,
        testnet: bool = False,
    ):
        self.base_symbol, self.quote_symbol = symbol.split("/")
        self.symbol = (
            "PERP_" + self.base_symbol.upper() + "_" + self.quote_symbol.upper()
        )
        self.account_id = account_id
        self.common_account_id = common_account_id
        if testnet:
            self.ws_exchange = OrderlyWebsocketClient(
                id="clientID6",
                application_id=common_account_id,
                endpoint="wss://testnet-ws.orderly.org/ws/stream/",
            )
            self.rest_exchange = OrderlyClient(
                endpoint="https://testnet-api.orderly.network",
                account_id=account_id,
                orderly_key=orderly_key,
                orderly_secret=orderly_secret,
                trading_key=trading_key,
                trading_secret=trading_secret,
            )
        else:
            self.ws_exchange = OrderlyWebsocketClient(
                id="clientID6",
                application_id=common_account_id,
                endpoint="wss://ws.orderly.org/ws/stream/",
            )
            self.rest_exchange = OrderlyClient(
                endpoint="https://api.orderly.network",
                account_id=account_id,
                orderly_key=orderly_key,
                orderly_secret=orderly_secret,
                trading_key=trading_key,
                trading_secret=trading_secret,
            )

    async def watch_boo(self):
        self.ws_exchange.get_bbo(self.symbol)

    async def watch_liquidation_push(self):
        self.ws_exchange.get_liquidation_push()
