from general_config import Config


class ContractConfig(Config):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arb_url = "https://arbitrum-mainnet.infura.io/v3/"
        self.eth_url = "https://mainnet.infura.io/v3/"
        self.sell_contract = "0x87160689F109D95F05bD0bfBcca7A6dF1b2438B3"


config = ContractConfig()
