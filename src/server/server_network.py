from os import times_result
import ssl
import msgpack
import socket
import threading
from time import sleep
from time import time as epoch
import sys
from msgpack import unpackb as deserialize
from msgpack import packb as serialize
from worldstate import worldstate

sleep_ms = lambda x: sleep(x / 1000)


def sending(sock, connection_id):
    global worldstate

    while True:
        packet = {"type": "worldstate", "worldstate": worldstate, "timestamp": epoch()}
        sock.sendall(serialize(packet))
        sleep_ms(1000)


def receiving(sock, connection_id):
    global worldstate
    # sock.send(serialize(connection_id))
    while True:
        try:
            # print("listening...")
            data = sock.recv(2048)

            packet = deserialize(data, strict_map_key=False)
            if not packet:
                break
            # print(f"received{packet}")
            if packet["type"] == "player_state":
                worldstate["players"][connection_id] = {
                    "player_state": packet["player_state"],
                    "timestamp": packet["timestamp"],
                }
            sleep_ms(10)

        except Exception as e:
            print(e)


class network:
    def __init__(self):
        self.sending_connections = []
        self.receiving_connections = []
        self.incoming_addr = ""
        self.port = 5002
        # context = ssl.create_default_context()

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        self.context.load_cert_chain(
            certfile="/home/logan/certs/rootCA.pem",
            keyfile="/home/logan/certs/rootCA.key",
        )

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock = self.context.wrap_socket(self.sock, server_side=True)
        print("attempting bind:")
        try:
            self.sock.bind((self.incoming_addr, self.port))
            print("socket bound successfully")
        except socket.error as message:
            print("Bind failed. Error Code : " + str(message))
            sys.exit()

        self.handle_new_connections = threading.Thread(target=self.await_connections)
        self.handle_new_connections.start()

    def await_connections(self):
        connection_id = 1
        self.sock.listen(5)
        while True:
            print("awaiting connections...")
            conn, address = self.sock.accept()
            print("connection accepted,spawning client thread")
            sending_thread = threading.Thread(
                target=sending,
                args=(
                    conn,
                    connection_id,
                ),
            )
            receiving_thread = threading.Thread(
                target=receiving,
                args=(
                    conn,
                    connection_id,
                ),
            )
            self.sending_connections.append(sending_thread)
            self.receiving_connections.append(receiving_thread)
            conn.send(serialize(connection_id))

            sending_thread.start()
            receiving_thread.start()
            connection_id += 1
