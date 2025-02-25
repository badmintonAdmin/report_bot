import requests
from apis.coingecko.connect import connect


def get_token_price(token_id: str):
    headers = connect.headers
    url = f"{connect.URL}price?ids={token_id}&vs_currencies=USD"

    response = requests.get(url, headers=headers)
    return response.json()[token_id]["usd"]
