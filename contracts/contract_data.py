import os
import json
from web3 import Web3
from general_config import config


class ContractData:
    def __init__(self):
        self.url = config.URL
        self.sell_contract = config.SELL_CONTRACT
        self.provider = Web3(Web3.HTTPProvider(self.url))
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

    def get_xtokens_data(self, token: str):
        try:
            file_path = os.path.join(self.current_dir, "abi", "xToken.json")
            with open(file_path, "r") as abi_file:
                contract_abi = json.load(abi_file)
        except Exception as e:
            print(f"Error loading ABI file: {e}")
            return None
        try:
            contract = self.provider.eth.contract(address=token, abi=contract_abi)
            count = contract.functions.totalAvailableToClaim().call()
            return count
        except Exception as e:
            print(f"Error interacting with contract: {e}")
            return None

    def get_ctokens_data(self, token: str):
        try:
            file_path = os.path.join(self.current_dir, "abi", "cToken.json")
            with open(file_path, "r") as abi_file:
                contract_abi = json.load(abi_file)
        except Exception as e:
            print(f"Error loading ABI file: {e}")
            return None
        try:
            contract = self.provider.eth.contract(address=token, abi=contract_abi)
            count = contract.functions.totalSupply().call()
            balance = contract.functions.balanceOf(self.sell_contract).call()
            return {"count": count, "balance": balance}
        except Exception as e:
            print(f"Error interacting with contract: {e}")
            return None


contract_data = ContractData()
