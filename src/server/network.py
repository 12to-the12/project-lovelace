from os import times_result
import ssl
import msgpack
import socket
import threading
from time import sleep
import sys
from msgpack import unpackb as deserialize
from msgpack import packb as serialize


def threaded_client(sock, connection_id):
    sock.send(serialize(connection_id))
    while True:
        sock.sendall(serialize("hello from the server!"))
        sleep(1)


class TCPNetwork:
    def __init__(self):
        self.client_connections = []
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

    def await_connections(self):
        connection_id = 0
        self.sock.listen(5)
        while True:
            print("awaiting connections...")
            conn, address = self.sock.accept()
            print("connection accepted,spawning client thread")
            thread = threading.Thread(
                target=threaded_client,
                args=(
                    conn,
                    connection_id,
                ),
            )
            connection_id += 1
            self.client_connections.append(thread)
            thread.start()
