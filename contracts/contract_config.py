from general_config import Config


class ContractConfig(Config):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arb_url = "https://arbitrum-mainnet.infura.io/v3/"
        self.eth_url = "https://mainnet.infura.io/v3/"
        self.sell_contract = "0x87160689F109D95F05bD0bfBcca7A6dF1b2438B3"
        self.eth_lcg_borrower = "0x2280BE9E5e37Ba1dA98bD1086bAb8B78697C9Fde"
        self.eth_lcg_staking = "0x134ee64cCF2151452B0fBd757f9aE1a09304036B"
        self.eth_lcg_vault = "0xe5d2eB7f4f1ecFA1113E8A5b5c6DF42d8376460f"
        self.eth_usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        self.eth_aave = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
        self.dao = "0x1A427D8717C16788a8A4a265804f489B9aB1e798"


config = ContractConfig()
