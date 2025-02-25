from general_config import config


class ConnectGecko:
    def __init__(self):
        self.TOKEN = config.COINGECKO_API
        self.URL = config.COINGECKO_URL
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": self.TOKEN,
        }


connect = ConnectGecko()
