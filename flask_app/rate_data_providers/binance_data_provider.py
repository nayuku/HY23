from binance.client import Client
from decimal import Decimal

from .base_data_provider import BaseDataProvider
from .utils import get_short_name


class BinanceSpotDataProvider(BaseDataProvider):
    source_name = 'Binance'

    def __init__(self):
        client = Client()
        super(BinanceSpotDataProvider, self).__init__(client=client)

    def get_rate_value(self, crypto, currency):
        tickers = self.client.get_ticker()
        prices = []
        for ticker in tickers:
            if ticker["symbol"].startswith(get_short_name(crypto) + currency) and Decimal(
                    ticker["lastPrice"]) > 0:
                prices.append(Decimal(ticker["weightedAvgPrice"]))
        avg_price = None
        if len(prices) > 0:
            avg_price = sum(prices) / Decimal(len(prices))
        return avg_price
