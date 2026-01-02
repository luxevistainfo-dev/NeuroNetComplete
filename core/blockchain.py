import time
import json
import os
import hashlib
import random
import threading

CHAIN_FILE = os.path.join(os.path.dirname(file), "..", "data", "chain.json")
LOCK = threading.Lock()

class Block:
    def init(self, index, previous_hash, transactions, nonce=0, hash_val=None, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.nonce = nonce
        self.timestamp = timestamp or time.time()
        self.hash = hash_val or self.calculate_hash()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

    def calculate_hash(self):
        content = f"{self.index}{self.previous_hash}{self.timestamp}{self.transactions}{self.nonce}"
        return hashlib.sha256(str(content).encode()).hexdigest()

class Blockchain:
    def init(self, difficulty=3):
        self.chain = []
        self.difficulty = int(difficulty)
        self.load_chain()

    def create_genesis_block(self):
        g = Block(0, "0", [], 0, "0", time.time())
        self.chain = [g]
        self.save_chain()
        return g

    def load_chain(self):
        with LOCK:
            if os.path.exists(CHAIN_FILE):
                try:
                    with open(CHAIN_FILE, "r") as f:
                        raw = json.load(f)
                    self.chain = [Block(b["index"], b["previous_hash"], b["transactions"], b["nonce"], b["hash"], b["timestamp"]) for b in raw]
                except Exception:
                    self.create_genesis_block()
            else:
                self.create_genesis_block()

    def save_chain(self):
        with LOCK:
            tmp = CHAIN_FILE + ".tmp"
            with open(tmp, "w") as f:
                json.dump([b.to_dict() for b in self.chain], f, indent=2)
            os.replace(tmp, CHAIN_FILE)

    def last_block(self):
        return self.chain[-1]

    def mine_block(self, transactions, miner_addr=None, max_nonce_rand=1024):
        last = self.last_block()
        index = len(self.chain)
        nonce = 0
        target = "0" * self.difficulty
        # classic PoW: sha256 of content must start with target
        while True:
            # random step for faster exploration
            step = random.randint(1, max(1, max_nonce_rand))
            nonce += step
            ts = time.time()
            content = f"{index}{last.hash}{transactions}{nonce}{ts}"
            h = hashlib.sha256(str(content).encode()).hexdigest()
            if h.startswith(target):
                new_block = Block(index, last.hash, transactions, nonce, h, ts)
                with LOCK:
                    self.chain.append(new_block)
                    self.save_chain()
                # slight difficulty adaptation safe-guard (caps)
                if self.difficulty < 10:
                    self.difficulty = min(10, self.difficulty + 0.001)
                return new_block

    def to_dict(self):
        return [b.to_dict() for b in self.chain]
