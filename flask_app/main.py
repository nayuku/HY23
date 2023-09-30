import json
import re

from flask import Flask, render_template, request, flash, url_for
from werkzeug.utils import redirect
from config import Config


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
        print("---------------------------------")
        form_data = request.form.to_dict()
        keys_to_check = ['Case_number', 'Owner']
        if any(len(form_data[key]) != 100 for key in keys_to_check):
            flash(f'Numer sprawy i dane właściciela muszą mieć dokładnie 100 znaków!', 'alert alert-danger')
            return redirect(request.url)
        allowed_characters = re.compile(r'^[a-zA-Z0-9.-/]+$')
        if not all(allowed_characters.match(form_data[key]) for key in keys_to_check):
            flash(f'Numer sprawy i dane właściciela mogą zawierać tylko znaki alfanumeryczne i symbole ,.”,-„/!"', 'alert alert-danger')
            return redirect(request.url)

        if len(request.form) == 3:
            flash(f"Nie dodano żadnego kryptoaktywa", 'alert alert-danger')
            return redirect(request.url)
        return redirect(url_for('calculator2'))
    return render_template('calculator1.html', title='Kalkulator kryptowalut', crypto_fields=get_crypto_fields())


@app.route('/calculator2', methods=['GET', 'POST'])
def calculator2():
    if request.method == 'POST':
        if len(request.form) == 0:
            flash(f"Nie wybranego żadnego dostawcy danych", 'alert alert-danger')
            return redirect(request.url)
        return redirect(url_for('show_result'))
    return render_template('calculator2.html', title='Kalkulator kryptowalut', markets=get_markets())


@app.route('/result', methods=['GET', 'POST'])
def show_result():
    species = json.loads(request.args['species'])
    return render_template('result.html', title='Wyniki', species=species)


def get_form_fields():
    fields = {
        "TYPE STR": {
            "id": "str_var",
            "type": "str",
            "required": True
        },
        "TYPE SELECT": {
            "id": "select_var",
            "type": "select",
            "values": ["Najmniejszej troski", "Nierozpoznane", "Wymarle","Zagrozone"],
            "required": True
        },
        "TYPE BOOL": {
            "id": "bool_var",
            "type": "bool",
            "required": False
        },
        "TYPE INT": {
            "id": "int_var",
            "type": "int",
            "required": False
        }
    }
    return fields


@app.route('/manual_data_provider', methods=['GET', 'POST'])
def add_species():
    if request.method == 'POST':
        print(request.form)  # Wypisanie parametrow z formularza
        gatunek = request.form['gatunek'].replace(' ', '_')
        sposob_odz = request.form['sposob_odzywiania']
        flash(f"Dane zostały dodane", 'alert alert-success')

    return render_template('manual.html', title='Manualne wprowadzanie danych', form_fields=get_form_fields())

@app.route('/update_directory', methods=['GET'])
def update_directory():
    return render_template('update_directory.html', title='Edycja słownika', crypto_fields=get_crypto_fields())

@app.route("/save", methods=["POST"])
def save():
    print('works')
    data = request.json
    for i, record in enumerate(data, start=1):
        record['id'] = i
    with open(app.config['CRYPTO_NAMES'], 'w') as f:
        json.dump(data, f)
    return {"status": "success"}, 200


if __name__ == '__main__':
    app.run(port=Config.flask_port)
