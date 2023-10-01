import requests

class ZondaCryptoExchange:
    BASE_URL = 'https://api.zondacrypto.exchange/rest/trading/ticker/'

    def get_ticker(self, pair: str):
        url = f"{self.BASE_URL}{pair}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

