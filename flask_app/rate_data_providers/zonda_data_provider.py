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
            return response.json()
        else:
            response.raise_for_status()

    def get_rate_value(self, crypto, currency):
        pair = get_short_name(crypto) + "-" + currency
        tickers = self.get_ticker(pair)
        rate = tickers['ticker']['rate']
        return rate
