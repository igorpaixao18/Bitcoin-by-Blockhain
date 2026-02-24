import uuid
import time


class Transaction:
    def __init__(self, origin, destination, value, timestamp=None, tx_id=None):
        if value <= 0:
            raise ValueError("Transaction value must be positive")

        self.id = tx_id or str(uuid.uuid4())
        self.origin = origin
        self.destination = destination
        self.value = float(value)
        self.timestamp = timestamp or time.time()

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        return Transaction(
            data["origin"],
            data["destination"],
            data["value"],
            data["timestamp"],
            data["id"]
        )
