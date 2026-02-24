class Miner:

    DIFFICULTY_PREFIX = "000"

    @staticmethod
    def proof_of_work(block):
        while not block.compute_hash().startswith(Miner.DIFFICULTY_PREFIX):
            block.nonce += 1

        block.hash = block.compute_hash()
        return block
