import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import threading

class Block:
    def __init__(self, index: int, transactions: List[Dict], timestamp: float, 
                 previous_hash: str, nonce: int = 0, difficulty: int = 4):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.difficulty = difficulty  # Ова мора да биде пред calculate_hash!
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        # Сега self.difficulty веќе постои
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        self.difficulty = difficulty
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
            
        print(f"Block mined: {self.hash}")

    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty
        }


class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.difficulty = 4
        self.mining_reward = 10
        self.lock = threading.Lock()
        
        # Create genesis block
        self.create_genesis_block()

    def create_genesis_block(self):
        # Додади го difficulty како аргумент
        genesis_block = Block(0, ["Genesis Block"], time.time(), "0", difficulty=self.difficulty)
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: Dict) -> None:
        # Basic validation
        required_fields = ["sender", "recipient", "amount", "signature"]
        if not all(field in transaction for field in required_fields):
            raise ValueError("Transaction must contain sender, recipient, amount, and signature")
            
        self.pending_transactions.append(transaction)
        
    def mine_pending_transactions(self, miner_address: str) -> Block:
        with self.lock:
            if not self.pending_transactions:
                raise ValueError("No transactions to mine")
            
            # Add mining reward transaction
            reward_transaction = {
                "sender": "network",
                "recipient": miner_address,
                "amount": self.mining_reward,
                "signature": "mining_reward"
            }
            
            block = Block(
                index=len(self.chain),
                transactions=self.pending_transactions.copy() + [reward_transaction],
                timestamp=time.time(),
                previous_hash=self.get_last_block().hash,
                difficulty=self.difficulty  # Додади го difficulty тука
            )
            
            block.mine_block(self.difficulty)
            
            # Add block to chain
            self.chain.append(block)
            
            # Clear pending transactions
            self.pending_transactions = []
            
            # Adjust difficulty every 10 blocks
            if len(self.chain) % 10 == 0:
                self.adjust_difficulty()
            
            return block

    def adjust_difficulty(self):
        # Simple difficulty adjustment - increase if blocks are mined too fast
        if len(self.chain) < 2:
            return
            
        last_block_time = self.chain[-1].timestamp
        ten_blocks_ago_time = self.chain[-10].timestamp if len(self.chain) >= 10 else self.chain[0].timestamp
        
        time_diff = last_block_time - ten_blocks_ago_time
        target_time = 600  # 10 minutes in seconds (like Bitcoin)
        
        if time_diff < target_time / 2:
            self.difficulty += 1
            print(f"Difficulty increased to {self.difficulty}")
        elif time_diff > target_time * 2:
            self.difficulty = max(1, self.difficulty - 1)
            print(f"Difficulty decreased to {self.difficulty}")

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check if current block hash is valid
            if current_block.hash != current_block.calculate_hash():
                print(f"Invalid hash at block {i}")
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                print(f"Invalid previous hash at block {i}")
                return False
            
            # Check proof of work
            if current_block.hash[:current_block.difficulty] != "0" * current_block.difficulty:
                print(f"Invalid proof of work at block {i}")
                return False
        
        return True

    def get_balance(self, address: str) -> float:
        balance = 0.0
        
        for block in self.chain:
            for transaction in block.transactions:
                if isinstance(transaction, dict):
                    if transaction["recipient"] == address:
                        balance += transaction["amount"]
                    if transaction["sender"] == address:
                        balance -= transaction["amount"]
        
        return balance

    def to_dict(self) -> List[Dict]:
        return [block.to_dict() for block in self.chain]
