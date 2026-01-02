"""
Simple web3 utilities for loading ABIs and interacting with contracts.
This module intentionally keeps a small surface area; expand as needed.
"""
import os
import json
from web3 import Web3
from eth_account import Account


def get_web3(provider_uri: str = None):
    provider_uri = provider_uri or os.environ.get("WEB3_PROVIDER_URI")
    if not provider_uri:
        raise RuntimeError("WEB3_PROVIDER_URI not configured")
    w3 = Web3(Web3.HTTPProvider(provider_uri))
    if not w3.isConnected():
        raise RuntimeError("Failed to connect to web3 provider")
    return w3


def load_abi(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"ABI not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    # If file contains whole artifact, extract 'abi' key
    if isinstance(data, dict) and "abi" in data:
        return data["abi"]
    return data


def load_contract(w3: Web3, abi_path: str, address: str):
    abi = load_abi(abi_path)
    return w3.eth.contract(address=w3.toChecksumAddress(address), abi=abi)


def sign_and_send_transaction(w3: Web3, private_key: str, tx: dict) -> str:
    acct = Account.from_key(private_key)
    # Ensure nonce
    tx.setdefault("nonce", w3.eth.getTransactionCount(acct.address))
    # Set reasonable defaults if missing
    if "gasPrice" not in tx and w3.eth.isConnected():
        try:
            tx["gasPrice"] = w3.eth.gas_price
        except Exception:
            pass
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    return tx_hash.hex()
