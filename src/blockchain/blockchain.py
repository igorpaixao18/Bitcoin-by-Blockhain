from threading import Lock
from .block import Block
from .transaction import Transaction
from .miner import Miner


class Blockchain:

    def __init__(self):
        self.lock = Lock()
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block(0, "0", [], 0, 0)

    def get_last_block(self):
        return self.chain[-1]

    # --------------------------
    # TRANSAÇÕES
    # --------------------------

    def add_transaction(self, tx):
        with self.lock:
            if not self.is_valid_transaction(tx):
                return False
            self.pending_transactions.append(tx)
            return True

    def is_valid_transaction(self, tx):
        if tx.value <= 0:
            return False

        if tx.origin == "SYSTEM":
            return True

        return self.get_balance(tx.origin) >= tx.value

    def get_balance(self, user):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.origin == user:
                    balance -= tx.value
                if tx.destination == user:
                    balance += tx.value
        return balance

    # --------------------------
    # MINERAÇÃO
    # --------------------------

    def mine_pending_transactions(self):
        with self.lock:
            if not self.pending_transactions:
                return None

            block = Block(
                len(self.chain),
                self.get_last_block().hash,
                list(self.pending_transactions)
            )

            mined_block = Miner.proof_of_work(block)

            self.chain.append(mined_block)
            self.pending_transactions.clear()

            return mined_block

    # --------------------------
    # VALIDAÇÃO
    # --------------------------

    def is_valid_chain(self, chain):

        if chain[0].hash != self.chain[0].hash:
            return False

        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]

            if current.previous_hash != previous.hash:
                return False

            if not current.hash.startswith(Miner.DIFFICULTY_PREFIX):
                return False

            if current.compute_hash() != current.hash:
                return False

        return True

    def replace_chain(self, new_chain):
        with self.lock:
            if len(new_chain) > len(self.chain) and \
               self.is_valid_chain(new_chain):

                self.chain = new_chain
                self.pending_transactions.clear()
                return True
            return False
