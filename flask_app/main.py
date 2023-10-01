import decimal
import json
import re
import uuid
import datetime

from flask import Flask, render_template, request, flash, url_for, session
from werkzeug.utils import redirect
from config import Config
from collections import defaultdict
from decimal import Decimal

from rate_data_providers import BinanceSpotDataProvider, KucoinSpotDataProvider, ZondaSpotDataProvider, get_rate

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


def get_authorities(authorities_file='./data/authorities.txt'):
    with open(authorities_file, 'r', encoding="utf-8") as f:
        authorities = [line.strip() for line in f]
    return authorities


@app.route('/calculator1', methods=['GET', 'POST'])
def calculator1():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        keys_to_check = ['Case_number', 'Owner']
        if any(len(form_data[key]) != 100 for key in keys_to_check):
            flash(f'Numer sprawy i dane właściciela muszą mieć dokładnie 100 znaków!', 'alert alert-danger')
            return render_template('calculator1.html', title='Kalkulator kryptowalut',
                                   crypto_fields=get_crypto_fields(), form_data=form_data, authorities=get_authorities())
        allowed_characters = re.compile(r'^[a-zA-Z0-9.-/]+$')
        if not all(allowed_characters.match(form_data[key]) for key in keys_to_check):
            flash(f'Numer sprawy i dane właściciela mogą zawierać tylko znaki alfanumeryczne i symbole ,.”,-„/!"', 'alert alert-danger')
            return render_template('calculator1.html', title='Kalkulator kryptowalut',
                                   crypto_fields=get_crypto_fields(), form_data=form_data, authorities=get_authorities())

        if len(request.form) == 3:
            flash(f"Nie dodano żadnego kryptoaktywa", 'alert alert-danger')
            return render_template('calculator1.html', title='Kalkulator kryptowalut',
                                   crypto_fields=get_crypto_fields(), form_data=form_data, authorities=get_authorities())

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
    return render_template('calculator1.html', title='Kalkulator kryptowalut', crypto_fields=get_crypto_fields(), authorities=get_authorities())


def calculate_manual_market_values(assets, value):
    market = json.loads(value)
    # TODO: pobierać kurs USD z api NBP
    usd_to_pln = Decimal(4.3)
    manual_market_values = {"name": market["name"] + " (" + market["address_url"] + ")", "type": "manual"}
    for asset in assets:
        if asset not in list(market.keys()):
            # TODO: zwrócić komunikat błędu, bo nie powinniśmy tu trafić, trzeba zawsze określić kurs dla każdego kryptoaktywa
            break
        else:
            rate_usd = "Nie dotyczy"
            rate_pln = "Nie dotyczy"
            rate = market[asset].split(" ")[0]
            currency = market[asset].split(" ")[1]
            value = Decimal(assets[asset])*Decimal(rate)
            if currency == "USD":
                rate_usd = Decimal(rate).quantize(Decimal('0.00'))
                value = value * usd_to_pln
            else:
                rate_pln = Decimal(rate).quantize(Decimal('0.00'))
            manual_market_values[asset] = {"amount": assets[asset], "rate": rate, "currency": currency, "usd_to_pln": usd_to_pln, "rate_usd": rate_usd, "rate_pln": rate_pln, "value": value.quantize(Decimal('0.00'))}
    return manual_market_values


def calculate_auto_market_values(assets, value):
    # TODO: pobierać kurs USD z api NBP
    # get_rate('usd')
    usd_to_pln = Decimal(4.3)
    auto_market_values = {"name": value, "type": "auto"}
    data_provider = None
    if value.startswith("Binance"):
        data_provider = BinanceSpotDataProvider()
    elif value.startswith("Kucoin"):
        data_provider = KucoinSpotDataProvider()
    elif value.startswith("Zonda"):
        data_provider = ZondaSpotDataProvider()
        pass
    else:
        # TODO: zwrócić komunikat błędu, bo nie wspieramy danego data provider-a
        return None
    for asset in assets:
        currency = "PLN"
        rate = data_provider.get_rate_value(asset, currency)
        if rate is None:
            currency = "USD"
            rate = data_provider.get_rate_value(asset, currency)
        if rate is None:
            # Giełda nie obraca danym kryptoaktywem
            auto_market_values[asset] = {}
        else:
            rate_usd = "Nie dotyczy"
            rate_pln = "Nie dotyczy"
            value = Decimal(assets[asset]) * Decimal(rate)
            if currency == "USD":
                rate_usd = Decimal(rate).quantize(Decimal('0.00'))
                value = value * usd_to_pln
            else:
                rate_pln = Decimal(rate).quantize(Decimal('0.00'))
            auto_market_values[asset] = {"amount": assets[asset], "rate": rate, "currency": currency, "usd_to_pln": usd_to_pln, "rate_usd": rate_usd, "rate_pln": rate_pln, "value": value.quantize(Decimal('0.00'))}
    return auto_market_values


def calculate_portfolio_values(form_data1, form_data2):
    assets = {key: value for key, value in form_data1.items() if key not in ('Case_number', 'Enforcement_authority', 'Owner')}
    portfolio_values = []
    for key, value in form_data2.items():
        if key.startswith('manual_data_'):
            portfolio_values.append(calculate_manual_market_values(assets, value))
        else:
            portfolio_values.append(calculate_auto_market_values(assets, value))
    print(portfolio_values)
    return portfolio_values


def is_portfolio_values_correct(form_data1, portfolio_values):
    assets = {key: value for key, value in form_data1.items() if key not in ('Case_number', 'Enforcement_authority', 'Owner')}
    for asset in assets:
        valid_flag = False
        for values in portfolio_values:
            if len(values[asset].keys()) > 0:
                valid_flag = True
                break
        if not valid_flag:
            return False
    return True


@app.route('/calculator2', methods=['GET', 'POST'])
def calculator2():
    form_data = session.get('form_data1', {})
    if request.method == 'POST':
        if len(request.form) < 3:
            flash(f"Nie zdefiniowano minimum 3 dostawców danych", 'alert alert-danger')
            return redirect(request.url)
        portfolio_values = calculate_portfolio_values(form_data, request.form.to_dict())
        if not is_portfolio_values_correct(form_data, portfolio_values):
            flash(f"Wybrani dostawcy danych nie obsługują przynajmniej jednej z badanych kryptowalut. Zdefiniuj manualnie kursy kryptowalut!", 'alert alert-danger')
            return redirect(request.url)
        session['form_data2'] = request.form.to_dict()
        session['portfolio_values'] = portfolio_values
        return redirect(url_for('show_result'))
    assets = {key.replace(" ", "_"): value for key, value in form_data.items() if key not in ('Case_number', 'Enforcement_authority', 'Owner')}
    return render_template('calculator2.html', title='Kalkulator kryptowalut', assets=assets, markets=get_markets(),
                           form_data=form_data)


def calculate_asset_values(assets, portfolio_values):
    asset_values = []
    for asset_name in assets:
        asset = {"name": asset_name, "amount": 0, "markets": "", "avg_USD_price": 0}
        for values in portfolio_values:
            if len(values[asset_name].keys()) > 0:
                asset["amount"] = values[asset_name]["amount"]
                if asset["markets"] == "":
                    asset["markets"] = '"'+values["name"]+'"'
                else:
                    asset["markets"] = asset["markets"] + ", " + '"'+values["name"]+'"'
                asset["avg_USD_price"] = decimal.Decimal(values[asset_name]["usd_to_pln"]).quantize(Decimal('0.00'))
        asset_values.append(asset)
    return asset_values


def calculate_portfolio_value():
    # TODO: Zaimplementować
    return 0


@app.route('/result', methods=['GET', 'POST'])
def show_result():
    form_data1 = session.get('form_data1', {})
    form_data2 = session.get('form_data2', {})
    portfolio_values = session.get('portfolio_values', {})
    assets = {key: value for key, value in form_data1.items() if key not in ('Case_number', 'Enforcement_authority', 'Owner')}
    asset_values = calculate_asset_values(assets, portfolio_values)
    return render_template('result.html', title='Szacowanie wartości kryptoaktywów', raport_id=str(uuid.uuid4()),
                           raport_date=datetime.datetime.now().strftime("%d.%m.%Y"), case_number=form_data1["Case_number"],
                           owner=form_data1["Owner"], portfolio_value=calculate_portfolio_value(), assets=assets, asset_values=asset_values, portfolio_values=portfolio_values)


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
