import requests


def get_rate(currency_symbol):
    url = f"http://api.nbp.pl/api/exchangerates/rates/A/{currency_symbol}?format=json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['rates'][0]['mid']
    else:
        response.raise_for_status()
