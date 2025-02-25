import requests
from requests.exceptions import RequestException
from apis.coingecko.connect import connect


def get_token_price(token_id: str):
    headers = connect.headers
    url = f"{connect.URL}price?ids={token_id}&vs_currencies=usd"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except RequestException as e:
        print(f"Request error: {e}")
        return None

    try:
        data = response.json()
    except ValueError:
        print("Error: API return not Json")
        return None

    return data
