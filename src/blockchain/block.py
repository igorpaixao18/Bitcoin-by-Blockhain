import hashlib
import json
import time


class Block:
    def __init__(self, index, previous_hash, transactions,
                 nonce=0, timestamp=None, block_hash=None):

        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.nonce = nonce
        self.timestamp = timestamp or time.time()
        self.hash = block_hash or self.compute_hash()

    def compute_hash(self):
        block_data = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "nonce": self.nonce,
            "timestamp": self.timestamp
        }

        return hashlib.sha256(
            json.dumps(block_data, sort_keys=True).encode()
        ).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "nonce": self.nonce,
            "timestamp": self.timestamp,
            "hash": self.hash
        }

    @staticmethod
    def from_dict(data, Transaction):
        txs = [Transaction.from_dict(tx) for tx in data["transactions"]]
        return Block(
            data["index"],
            data["previous_hash"],
            txs,
            data["nonce"],
            data["timestamp"],
            data["hash"]
        )
