
import requests
import os
from flask import current_app as app, abort


api_url = "https://api.api-ninjas.com/v1/exchangerate?pair={}_{}"


def get_exchange_rate(currency_to_change, final_currency):
    url = api_url.format(currency_to_change,final_currency)
    response = requests.get(url,headers= {'X-Api-Key': os.getenv('API_NINJA_KEY')})
    if response.status_code != 200:
        app.logger.error(f'API NINJA RESPONSE CODE: {response.status_code}')
        if response.status_code == 400:
            app.logger.error("Check X-Api-Key!")
        abort(500)
    rate = response.json().get('exchange_rate')
    if rate is None:
        app.logger.error("Exchange rate not found in response.")
        abort(500)
    return rate


def change_currency(currency_to_change, final_currency,amount):
    rate = get_exchange_rate(currency_to_change,final_currency)
    after_change = amount * rate
    return after_change