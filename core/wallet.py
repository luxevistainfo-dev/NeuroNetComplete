import secrets
import hashlib
import json
import os

WALLETS_DIR = os.path.join(os.path.dirname(file), "..", "data", "wallets")
os.makedirs(WALLETS_DIR, exist_ok=True)

def generate_wallet():
    priv = secrets.token_hex(32)
    addr = hashlib.sha256(priv.encode()).hexdigest()[:40]
    return priv, addr

def create_wallet_file(username=None):
    priv, addr = generate_wallet()
    data = {"private_key": priv, "address": addr, "username": username}
    with open(os.path.join(WALLETS_DIR, f"{addr}.json"), "w") as f:
        json.dump(data, f)
    return data

def load_wallet(address):
    path = os.path.join(WALLETS_DIR, f"{address}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None
