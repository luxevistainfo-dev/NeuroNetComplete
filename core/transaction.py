import time
import hashlib
import json

class Transaction:
    def init(self, sender, receiver, amount, meta=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = float(amount)
        self.meta = meta or {}
        self.timestamp = time.time()
        self.tx_id = self.calculate_tx_id()

    def calculate_tx_id(self):
        content = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}{json.dumps(self.meta, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "meta": self.meta,
            "timestamp": self.timestamp,
            "tx_id": self.tx_id
        }
