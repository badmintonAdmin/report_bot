import os
import json
import time
from web3 import Web3
from sqlalchemy import select

from contracts.contract_config import config
from local_db.sync_ldb import sync_session
from local_db.models.lcg_loan import LCGLoanModel
from local_db.models.sync_state import SyncStateModel

LCG_BORROWER_LAST_BLOCK_KEY = "lcg_borrower_last_block"
LCG_EVENT_NAMES = ("Opened", "Borrowed", "InterestPaid", "Repaid")
GETLOGS_CHUNK = 9000
EPOCH_CACHE_TTL_SECONDS = 30 * 60
EPOCH_CACHE_KEY_PREFIX = "epoch_cache_"


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

        cache_key = f"{EPOCH_CACHE_KEY_PREFIX}{chain}"
        now_ts = int(time.time())

        with sync_session() as session:
            cached = session.get(SyncStateModel, cache_key)
            if cached:
                try:
                    payload = json.loads(cached.value)
                    epoch = tuple(payload["epoch"])
                    next_epoch = tuple(payload["next_epoch"])
                    cached_at = int(payload.get("cached_at", 0))
                    fresh = (
                        now_ts - cached_at < EPOCH_CACHE_TTL_SECONDS
                        and now_ts < epoch[2]
                    )
                    if fresh:
                        return {"epoch": epoch, "next_epoch": next_epoch}
                except (ValueError, KeyError, TypeError) as e:
                    print(f"[epoch cache] invalid cached value for {chain}: {e}")

        try:
            epoch = contract.functions.getCurrentEpoch().call()
            next_epoch = contract.functions.epoch(epoch[0] + 1).call()
        except Exception as e:
            print(f"Error interacting with epoch contract: {e}")
            return None

        with sync_session() as session:
            payload = json.dumps(
                {
                    "epoch": list(epoch),
                    "next_epoch": list(next_epoch),
                    "cached_at": now_ts,
                }
            )
            cached = session.get(SyncStateModel, cache_key)
            if cached is None:
                session.add(SyncStateModel(id=cache_key, value=payload))
            else:
                cached.value = payload
            session.commit()

        return {"epoch": epoch, "next_epoch": next_epoch}

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

    def _fetch_loan_struct(self, contract, loan_id: int) -> dict:
        row = contract.functions.loans(loan_id).call()
        return {
            "id": loan_id,
            "borrower": row[0],
            "amount": row[1],
            "annual_rate": row[2],
            "interest_payment_period": row[3],
            "duration": row[4],
            "borrowed_at": row[5],
            "principal_debt": row[6],
            "borrowed": row[7],
            "repaid": row[8],
            "days_in_period_paid": row[9],
            "last_interest_paid_at": row[10],
        }

    def _affected_loan_ids_from_events(
        self, contract, from_block: int, to_block: int
    ) -> set:
        affected = set()
        for event_name in LCG_EVENT_NAMES:
            event = getattr(contract.events, event_name)
            cursor = from_block
            while cursor <= to_block:
                chunk_end = min(cursor + GETLOGS_CHUNK, to_block)
                logs = event.get_logs(from_block=cursor, to_block=chunk_end)
                for log in logs:
                    affected.add(int(log.args.creditLineID))
                cursor = chunk_end + 1
        return affected

    def get_lcg_loans(self, contract_address=config.eth_lcg_borrower):
        contract = self.contract_factory(
            contract_address, "eth_lcg_borrower.json", "eth"
        )
        if not contract:
            return None
        try:
            current_block = self.provider_eth.eth.block_number

            with sync_session() as session:
                state = session.get(SyncStateModel, LCG_BORROWER_LAST_BLOCK_KEY)
                last_block = int(state.value) if state else None

                if last_block is None:
                    count = contract.functions.loansCount().call()
                    affected_ids = set(range(count))
                    print(f"[lcg cache] bootstrap: syncing {count} loans")
                else:
                    affected_ids = self._affected_loan_ids_from_events(
                        contract, last_block + 1, current_block
                    )
                    print(
                        f"[lcg cache] incremental: blocks {last_block+1}..{current_block} "
                        f"-> {len(affected_ids)} affected loan(s)"
                    )

                for loan_id in sorted(affected_ids):
                    data = self._fetch_loan_struct(contract, loan_id)
                    cached = session.get(LCGLoanModel, loan_id)
                    if cached is None:
                        session.add(LCGLoanModel(**data))
                    else:
                        for key, value in data.items():
                            if key != "id":
                                setattr(cached, key, value)

                if state is None:
                    session.add(
                        SyncStateModel(
                            id=LCG_BORROWER_LAST_BLOCK_KEY, value=str(current_block)
                        )
                    )
                else:
                    state.value = str(current_block)

                session.commit()

                now_ts = int(time.time())
                cached_loans = (
                    session.scalars(select(LCGLoanModel).order_by(LCGLoanModel.id))
                    .all()
                )

                dynamic_refreshed = 0
                for c in cached_loans:
                    if not c.borrowed or c.repaid:
                        continue
                    needs_refresh = (
                        c.id in affected_ids
                        or c.dynamic_synced_block == 0
                        or (c.next_interest_ts and c.next_interest_ts <= now_ts)
                    )
                    if not needs_refresh:
                        continue
                    interest_amount, _periods = (
                        contract.functions.previewInterestToPay(c.id).call()
                    )
                    next_dt = contract.functions.getNextInterestPayDate(c.id).call()
                    unpaid = contract.functions.getUnpaidInterestPeriods(c.id).call()
                    c.interest_due = interest_amount
                    c.next_interest_ts = next_dt
                    c.unpaid_periods = unpaid
                    c.dynamic_synced_block = current_block
                    dynamic_refreshed += 1

                if dynamic_refreshed:
                    print(
                        f"[lcg cache] dynamic refresh: {dynamic_refreshed} loan(s)"
                    )

                session.commit()

                snapshot = [
                    {
                        "id": c.id,
                        "borrower": c.borrower,
                        "borrowed_at": c.borrowed_at,
                        "duration": c.duration,
                        "principal_debt": c.principal_debt,
                        "borrowed": c.borrowed,
                        "repaid": c.repaid,
                        "interest_due": c.interest_due,
                        "next_interest_ts": c.next_interest_ts,
                        "unpaid_periods": c.unpaid_periods,
                    }
                    for c in cached_loans
                ]

            loans = []
            for c in snapshot:
                if not c["borrowed"] or c["repaid"]:
                    continue
                loans.append(
                    {
                        "id": c["id"],
                        "borrower": c["borrower"],
                        "principal_debt": c["principal_debt"],
                        "interest_due": c["interest_due"],
                        "next_interest_ts": c["next_interest_ts"],
                        "maturity_ts": c["borrowed_at"] + c["duration"],
                        "unpaid_periods": c["unpaid_periods"],
                    }
                )
            return loans
        except Exception as e:
            print(f"Error reading LCG loans: {e}")
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

            return data

        except Exception as e:
            print(f"Error interacting with Aave contract: {e}")
            return None


contract_data = ContractData()
