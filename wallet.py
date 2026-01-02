import hashlib
import json
import binascii
import base64
from typing import Tuple, Dict
import os

class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.address = None
        
    def generate_keys(self) -> None:
        """Generate a simple key pair (for demonstration, not cryptographically secure)"""
        # In production, use proper cryptography like ECDSA
        private_key = os.urandom(32).hex()
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        address = hashlib.sha256(public_key.encode()).hexdigest()[:40]
        
        self.private_key = private_key
        self.public_key = public_key
        self.address = f"NN_{address}"
        
        return {
            "private_key": private_key,
            "public_key": public_key,
            "address": self.address
        }
    
    def sign_transaction(self, transaction_data: Dict) -> str:
        """Sign a transaction with private key"""
        if not self.private_key:
            raise ValueError("Wallet not initialized")
            
        transaction_string = json.dumps(transaction_data, sort_keys=True)
        message = transaction_string + self.private_key
        signature = hashlib.sha256(message.encode()).hexdigest()
        
        return signature
    
    def verify_signature(self, transaction_data: Dict, signature: str, public_key: str) -> bool:
        """Verify a transaction signature"""
        transaction_string = json.dumps(transaction_data, sort_keys=True)
        message = transaction_string + public_key
        expected_signature = hashlib.sha256(message.encode()).hexdigest()
        
        return signature == expected_signature
    
    @staticmethod
    def validate_address(address: str) -> bool:
        """Validate wallet address format"""
        return address.startswith("NN_") and len(address) == 43


class WalletManager:
    def __init__(self):
        self.wallets = {}
        
    def create_wallet(self) -> Dict:
        wallet = Wallet()
        keys = wallet.generate_keys()
        self.wallets[keys["address"]] = wallet
        return keys
    
    def get_wallet(self, address: str) -> Wallet:
        return self.wallets.get(address)
    
    def save_wallet_to_file(self, address: str, filename: str):
        wallet = self.get_wallet(address)
        if wallet:
            data = {
                "address": wallet.address,
                "private_key": wallet.private_key,
                "public_key": wallet.public_key
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
    
    def load_wallet_from_file(self, filename: str) -> Wallet:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        wallet = Wallet()
        wallet.address = data["address"]
        wallet.private_key = data["private_key"]
        wallet.public_key = data["public_key"]
        
        self.wallets[wallet.address] = wallet
        return wallet
