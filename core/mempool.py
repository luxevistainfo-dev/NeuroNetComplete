class Mempool:
    def init(self):
        self.transactions = []

    def add_transaction(self, tx):
        self.transactions.append(tx)

    def snapshot(self):
        return list(self.transactions)

    def clear(self):
        self.transactions = []
