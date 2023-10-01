import json
import re
import sys
import os

from flask import Flask, render_template, request, flash, url_for, session
from werkzeug.utils import redirect
from config import Config
from collections import defaultdict
from decimal import Decimal

parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

from rate_data_providers import BinanceSpotDataProvider, KucoinSpotDataProvider, ZondaCryptoExchange


app = Flask(__name__, static_url_path=Config.flask_static_url_path)
app.config.from_object('config.BaseConfig')


@app.route('/')
@app.route('/about')
def home():
    return render_template('about.html', title='O nas')


def get_crypto_fields(crypto_dict='./data/crypto_names.json'):
    with open(crypto_dict, 'r') as f:
        crypto_fields = json.load(f)
    return crypto_fields


def get_markets(market_dict='./data/markets.json'):
    with open(market_dict, 'r') as f:
        markets = json.load(f)
    return markets


@app.route('/calculator1', methods=['GET', 'POST'])
def calculator1():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        keys_to_check = ['Case_number', 'Owner']
        if any(len(form_data[key]) != 100 for key in keys_to_check):
            flash(f'Numer sprawy i dane właściciela muszą mieć dokładnie 100 znaków!', 'alert alert-danger')
            return render_template('calculator1.html', title='Kalkulator kryptowalut',
                                   crypto_fields=get_crypto_fields(), form_data=form_data)
        allowed_characters = re.compile(r'^[a-zA-Z0-9.-/]+$')
        if not all(allowed_characters.match(form_data[key]) for key in keys_to_check):
            flash(f'Numer sprawy i dane właściciela mogą zawierać tylko znaki alfanumeryczne i symbole ,.”,-„/!"', 'alert alert-danger')
            return render_template('calculator1.html', title='Kalkulator kryptowalut',
                                   crypto_fields=get_crypto_fields(), form_data=form_data)

        if len(request.form) == 3:
            flash(f"Nie dodano żadnego kryptoaktywa", 'alert alert-danger')
            return render_template('calculator1.html', title='Kalkulator kryptowalut',
                                   crypto_fields=get_crypto_fields(), form_data=form_data)

        # delete_prefix and sum coin values
        result_dict = {}
        grouped_dict = defaultdict(int)
        for key, value in form_data.items():
            if key in {'Case_number', 'Enforcement_authority', 'Owner'}:
                result_dict[key] = value
            else:
                prefix = key.split('-')[0]
                grouped_dict[prefix] += Decimal(value)
        result_dict.update(grouped_dict)
        session['form_data1'] = result_dict
        return redirect(url_for('calculator2'))
    return render_template('calculator1.html', title='Kalkulator kryptowalut', crypto_fields=get_crypto_fields())


@app.route('/calculator2', methods=['GET', 'POST'])
def calculator2():
    form_data = session.get('form_data1', {})
    if request.method == 'POST':
        if len(request.form) == 0:
            flash(f"Nie wybranego żadnego dostawcy danych", 'alert alert-danger')
            return redirect(request.url)
        session['form_data2'] = request.form.to_dict()
        return redirect(url_for('show_result'))
    assets = {key.replace(" ", "_"): value for key, value in form_data.items() if key not in ('Case_number', 'Enforcement_authority', 'Owner')}
    return render_template('calculator2.html', title='Kalkulator kryptowalut', assets=assets, markets=get_markets(),
                           form_data=form_data)


@app.route('/result', methods=['GET', 'POST'])
def show_result():
    # form_data1 = session.get('form_data1', {})
    # form_data2 = session.get('form_data2', {})
    # print(form_data1)
    # print(form_data2)
    binance_data_provider = BinanceSpotDataProvider()
    # kucoin_data_provider = KucoinSpotDataProvider()
    # print(binance_data_provider.get_rate_value("Bitcoin", "USD"))
    print(kucoin_data_provider.get_rate_value("Bitcoin", "USD"))
    zonda_crypto = ZondaCryptoExchange()
    pair = 'BTC-PLN'
    ticker = zonda_crypto.get_ticker(pair)
    print(ticker)
    return render_template('about.html', title='Wyniki')


@app.route('/update_directory', methods=['GET'])
def update_directory():
    return render_template('update_directory.html', title='Edycja słownika', crypto_fields=get_crypto_fields())


@app.route("/save", methods=["POST"])
def save():
    data = request.json
    for i, record in enumerate(data, start=1):
        record['id'] = i
    with open(app.config['CRYPTO_NAMES'], 'w') as f:
        json.dump(data, f)
    return {"status": "success"}, 200


if __name__ == '__main__':
    app.run(port=Config.flask_port)
