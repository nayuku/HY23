import json

from flask import Flask, render_template, request, flash, url_for
from werkzeug.utils import redirect
from flask_app.config import Config

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


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    if request.method == 'POST':
        if len(request.form) == 0:
            flash(f"Nie dodano żadnego kryptoaktywa", 'alert alert-danger')
            return redirect(request.url)
        # return redirect(url_for('show_result', species=json.dumps(species)))
    return render_template('calculator.html', title='Kalkulator kryptowalut', crypto_fields=get_crypto_fields())


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


if __name__ == '__main__':
    app.run(port=Config.flask_port)
