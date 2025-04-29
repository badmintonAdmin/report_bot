import os
import json
from web3 import Web3
from general_config import config


class ContractData:
    def __init__(self):
        self.url = config.URL
        self.eth_url = config.ETH_URL
        self.sell_contract = config.SELL_CONTRACT
        self.provider = Web3(Web3.HTTPProvider(self.url))
        self.provider_eth = Web3(Web3.HTTPProvider(self.eth_url))
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

    def get_epoch(self, chain: str):

        data = {
            "eth": {
                "chain_abi": "eth_8020.json",
                "contract_address": "0x0743ab8f59952b42d56DFAAce6ca60113b19b9a3",
                "provider": self.provider_eth,
            },
            "arb": {
                "chain_abi": "arb_8020.json",
                "contract_address": "0x2B893Bb1cA5bee6Db4c50909c9AEa1e640FC7e54",
                "provider": self.provider,
            },
        }
        if chain not in data:
            print(f"Chain {chain} not supported.")
            return None
        provider = data[chain]["provider"]
        try:
            file_path = os.path.join(self.current_dir, "abi", data[chain]["chain_abi"])
            with open(file_path, "r") as abi_file:
                contract_abi = json.load(abi_file)
        except Exception as e:
            print(f"Error loading ABI file: {e}")
            return None
        try:
            contract = provider.eth.contract(
                address=data[chain]["contract_address"], abi=contract_abi
            )
            epoch = contract.functions.getCurrentEpoch().call()
            return {
                "epoch": epoch,
            }
        except Exception as e:
            print(f"Error interacting with contract: {e}")
            return None


contract_data = ContractData()
