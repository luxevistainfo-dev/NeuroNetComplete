"""
Web3 helper utilities using web3.py. Contains Web3Client class to load provider, sign transactions, and interact with simple contracts.
"""
from web3 import Web3
import os
import json

class Web3Client:
    def __init__(self, provider_url: str | None, private_key: str | None):
        if not provider_url:
            raise ValueError("WEB3 provider url not set")
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        if not self.w3.isConnected():
            raise ConnectionError("Failed to connect to WEB3 provider")
        self.private_key = private_key
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
        else:
            self.account = None

    def _load_abi(self, path):
        with open(path, 'r') as f:
            content = json.load(f)
        return content

    def mint_nft(self, contract_address: str, to_address: str, token_uri: str):
        # Expect a contract ABI JSON artifact in contracts/artifacts/ERC721.json
        abi_path = os.path.join('contracts', 'artifacts', 'ERC721.json')
        if not os.path.exists(abi_path):
            raise FileNotFoundError('ABI file not found: ' + abi_path)
        with open(abi_path, 'r') as f:
            artifact = json.load(f)
        abi = artifact.get('abi')
        contract = self.w3.eth.contract(address=self.w3.toChecksumAddress(contract_address), abi=abi)
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = contract.functions.mint(to_address, token_uri).buildTransaction({
            'from': self.account.address,
            'nonce': nonce,
            'gas': 500000,
            'gasPrice': self.w3.toWei('2', 'gwei')
        })
        signed = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return self.w3.toHex(tx_hash)

    # Helper placeholder for recording checkpoint receipt
    def record_checkpoint(self, contract_address: str, token_id: int, ipfs_hash: str):
        pass
