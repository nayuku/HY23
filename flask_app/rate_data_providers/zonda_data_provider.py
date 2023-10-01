import requests

from .base_data_provider import BaseDataProvider
from .utils import get_short_name

class ZondaSpotDataProvider(BaseDataProvider):
    source_name = 'Zonda'
    BASE_URL = 'https://api.zondacrypto.exchange/rest/trading/ticker/'

    def __init__(self):
        client = None
        super(ZondaSpotDataProvider, self).__init__(client=client)

    def get_ticker(self, pair: str):
        url = f"{self.BASE_URL}{pair}"
        response = requests.get(url)
        if response.status_code == 200:
            json_r = response.json()
            if json_r["status"] != "Fail":
                return json_r
            else:
                return None
        else:
            return None

    def get_rate_value(self, crypto, currency):
        pair = get_short_name(crypto) + "-" + currency
        rate = None
        tickers = self.get_ticker(pair)
        if tickers is not None:
            rate = tickers['ticker']['rate']
        return rate
