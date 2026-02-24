import socket
import threading
import json

from .blockchain import Blockchain
from .transaction import Transaction
from .block import Block
from .protocol import *


class Node:

    def __init__(self, host, port, bootstrap=None):
        self.host = host
        self.port = port
        self.bootstrap = bootstrap
        self.blockchain = Blockchain()
        self.peers = set()

    # --------------------------
    # START
    # --------------------------

    def start(self):
        threading.Thread(target=self.server, daemon=True).start()

        if self.bootstrap:
            self.connect_to_peer(self.bootstrap)

        threading.Thread(target=self.mining_loop, daemon=True).start()

    # --------------------------
    # SERVER
    # --------------------------

    def server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()

        print(f"[Node {self.port}] Listening...")

        while True:
            conn, _ = server.accept()
            threading.Thread(
                target=self.handle_client,
                args=(conn,),
                daemon=True
            ).start()

    def handle_client(self, conn):

        data = conn.recv(65536).decode()
        messages = data.split("\n")

        for raw in messages:
            if not raw.strip():
                continue

            message = json.loads(raw)
            msg_type = message["type"]
            payload = message["data"]

            if msg_type == NEW_TRANSACTION:
                tx = Transaction.from_dict(payload)
                if self.blockchain.add_transaction(tx):
                    self.broadcast(NEW_TRANSACTION, tx.to_dict())

            elif msg_type == NEW_BLOCK:
                block = Block.from_dict(payload, Transaction)
                temp_chain = self.blockchain.chain + [block]

                if self.blockchain.is_valid_chain(temp_chain):
                    self.blockchain.chain.append(block)
                    self.blockchain.pending_transactions.clear()
                    self.broadcast(NEW_BLOCK, block.to_dict())

            elif msg_type == REQUEST_CHAIN:
                self.send_message(conn, RESPONSE_CHAIN,
                                  [b.to_dict() for b in self.blockchain.chain])

            elif msg_type == RESPONSE_CHAIN:
                new_chain = [
                    Block.from_dict(b, Transaction)
                    for b in payload
                ]
                self.blockchain.replace_chain(new_chain)

            elif msg_type == REGISTER_PEER:
                self.peers.add(payload)

        conn.close()

    # --------------------------
    # NETWORK
    # --------------------------

    def send_message(self, conn, msg_type, data):
        message = json.dumps({"type": msg_type, "data": data}) + "\n"
        conn.sendall(message.encode())

    def broadcast(self, msg_type, data):
        for peer in list(self.peers):
            host, port = peer.split(":")
            try:
                with socket.create_connection((host, int(port)), timeout=3) as s:
                    self.send_message(s, msg_type, data)
            except:
                self.peers.discard(peer)

    def connect_to_peer(self, peer):
        self.peers.add(peer)
        host, port = peer.split(":")

        try:
            with socket.create_connection((host, int(port))) as s:
                self.send_message(s, REGISTER_PEER,
                                  f"{self.host}:{self.port}")
                self.send_message(s, REQUEST_CHAIN, None)
        except:
            print("Bootstrap connection failed")

    # --------------------------
    # MINING LOOP
    # --------------------------

    def mining_loop(self):
        while True:
            block = self.blockchain.mine_pending_transactions()
            if block:
                print(f"[Node {self.port}] Mined block {block.index}")
                self.broadcast(NEW_BLOCK, block.to_dict())

    # --------------------------
    # USER ACTIONS
    # --------------------------

    def create_transaction(self, origin, dest, value):
        tx = Transaction(origin, dest, value)
        if self.blockchain.add_transaction(tx):
            self.broadcast(NEW_TRANSACTION, tx.to_dict())
