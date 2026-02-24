import argparse
from src.blockchain.node import Node

parser = argparse.ArgumentParser()
parser.add_argument("--port", required=True, type=int)
parser.add_argument("--bootstrap", required=False)

args = parser.parse_args()

node = Node("localhost", args.port, args.bootstrap)
node.start()

print(f"Node running on port {args.port}")

while True:
    cmd = input(">> ")

    if cmd.startswith("tx"):
        _, origin, dest, value = cmd.split()
        node.create_transaction(origin, dest, float(value))

    elif cmd == "mine":
        node.mine()

    elif cmd == "chain":
        for block in node.blockchain.chain:
            print(block.to_dict())
