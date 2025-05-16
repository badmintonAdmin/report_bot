import os
import json
from web3 import Web3
from contracts.contract_config import config


class ContractData:
    def __init__(self):
        self.arb_url = f"{config.arb_url}{config.INF_KEY}"
        self.eth_url = f"{config.eth_url}{config.INF_KEY}"
        self.sell_contract = config.sell_contract
        self.provider_arb = Web3(Web3.HTTPProvider(self.arb_url))
        self.provider_eth = Web3(Web3.HTTPProvider(self.eth_url))
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

    def contract_factory(self, address: str, abi: str, chain: str):
        if chain == "eth":
            provider = self.provider_eth
        else:
            provider = self.provider_arb

        try:
            file_path = os.path.join(self.current_dir, "abi", abi)
            with open(file_path, "r") as abi_file:
                contract_abi = json.load(abi_file)
        except Exception as e:
            print(f"Error loading ABI file: {e}")
            return None
        try:
            contract = provider.eth.contract(address=address, abi=contract_abi)
            return contract
        except Exception as e:
            print(f"Error interacting with contract: {e}")
            return None

    def get_xtokens_data(self, token: str):
        contract = self.contract_factory(token, "xToken.json", "arb")
        if not contract:
            return None
        try:
            count = contract.functions.totalAvailableToClaim().call()
            return count
        except Exception as e:
            print(f"Error interacting with xToken contract: {e}")
            return None

    def get_ctokens_data(self, token: str):
        contract = self.contract_factory(token, "cToken.json", "arb")
        if not contract:
            return None
        try:
            count = contract.functions.totalSupply().call()
            balance = contract.functions.balanceOf(self.sell_contract).call()
            return {"count": count, "balance": balance}
        except Exception as e:
            print(f"Error interacting with cToken contract: {e}")
            return None

    def get_epoch(self, chain: str):
        data = {
            "eth": {
                "abi": "eth_8020.json",
                "address": "0x0743ab8f59952b42d56DFAAce6ca60113b19b9a3",
            },
            "arb": {
                "abi": "arb_8020.json",
                "address": "0x2B893Bb1cA5bee6Db4c50909c9AEa1e640FC7e54",
            },
        }

        if chain not in data:
            print(f"Chain {chain} not supported.")
            return None

        contract = self.contract_factory(
            data[chain]["address"], data[chain]["abi"], chain
        )
        if not contract:
            return None

        try:
            epoch = contract.functions.getCurrentEpoch().call()
            next_epoch = contract.functions.epoch(epoch[0] + 1).call()
            return {"epoch": epoch, "next_epoch": next_epoch}
        except Exception as e:
            print(f"Error interacting with epoch contract: {e}")
            return None

    def get_total_borrowed(self, contract_address=config.eth_lcg_borrower):
        contract = self.contract_factory(
            contract_address, "eth_lcg_borrower.json", "eth"
        )
        if not contract:
            return None
        try:
            total_borrowed = contract.functions.totalBorrowed().call()
            borrow_apr = contract.functions.getCurrentWeightedAverageRate().call()
            return {"total_borrowed": total_borrowed, "borrow_apr": borrow_apr}
        except Exception as e:
            print(f"Error interacting with borrower contract: {e}")
            return None

    def get_total_staked(self, contract_address=config.eth_lcg_staking):
        contract = self.contract_factory(
            contract_address, "eth_lcg_staking.json", "eth"
        )
        if not contract:
            return None
        try:
            total_staked = contract.functions.totalStaked().call()
            return {"total_staked": total_staked}
        except Exception as e:
            print(f"Error interacting with staking contract: {e}")
            return None

    def get_available(self, contract_address=config.eth_usdc):
        contract = self.contract_factory(contract_address, "eth_usdc.json", "eth")
        if not contract:
            return None
        try:
            balance = contract.functions.balanceOf(config.eth_lcg_vault).call()
            return {"balance": balance}
        except Exception as e:
            print(f"Error interacting with USDC contract: {e}")
            return None

    def get_aave_data(self, contract_address=config.eth_aave):
        contract = self.contract_factory(contract_address, "aave_v3_eth.json", "eth")
        if not contract:
            return None

        try:
            user_data = contract.functions.getUserAccountData(config.dao).call()
            if not user_data or all(v == 0 for v in user_data):
                print("No Aave data returned (all zero).")
                return None

            data = {
                "supply": user_data[0] / 1e8,
                "borrowed": user_data[1] / 1e8,
                "net": user_data[0] / 1e8 - user_data[1] / 1e8,
                "hf": user_data[5] / 1e18,
            }

            return {"user_data": data}

        except Exception as e:
            print(f"Error interacting with Aave contract: {e}")
            return None


contract_data = ContractData()
