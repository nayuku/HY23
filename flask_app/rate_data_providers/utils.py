import json


def get_short_name(crypto, crypto_dict='../flask_app/data/crypto_names.json'):
    with open(crypto_dict, 'r') as f:
        crypto_fields = json.load(f)
        for field in crypto_fields:
            if field["name"] == crypto:
                return field["short_name"]
    return None
