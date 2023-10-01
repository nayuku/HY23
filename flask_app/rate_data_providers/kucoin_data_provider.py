from kucoin.client import Market
from decimal import Decimal

from .base_data_provider import BaseDataProvider
from .utils import get_short_name


class KucoinSpotDataProvider(BaseDataProvider):
    source_name = 'Kucoin'

    def __init__(self):
        client = Market(url='https://api.kucoin.com')
        super(KucoinSpotDataProvider, self).__init__(client=client)

    def get_rate_value(self, crypto, currency):
        tickers = self.client.get_all_tickers()["ticker"]
        prices = []
        for ticker in tickers:
            if ticker["symbol"].startswith(get_short_name(crypto) + "-" + currency):
                prices.append(Decimal(ticker["last"]))
        avg_price = None
        if len(prices) > 0:
            avg_price = sum(prices) / Decimal(len(prices))
        return avg_price
