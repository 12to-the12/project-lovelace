import socket

# from ssl import SSLSocket as socket
import ssl
from time import sleep

# import pickle
from pickle import dumps as serialize
from pickle import loads as deserialize


class Network:
    def __init__(self):
        # context = ssl.create_default_context()
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        # context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
        context.load_verify_locations("rootCA.pem")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server = "lovelace.loganhillyer.me"
        # self.server = "47.155.218.95"

        self.port = 5002

        self.addr = (self.server, self.port)
        # self.socket = socket.create_connection(self.addr)
        self.socket = context.wrap_socket(self.socket, server_hostname=self.server)

        self.connection_id = self.connect()
        # print("connection successful ")
        print(f"assigned connection ID: {self.connection_id}")

    def connect(self):
        try:
            print("attempting connection...")
            self.socket.connect(self.addr)
            return deserialize(self.socket.recv(2048))
        except:
            print("connection failed")
            pass

    def send(self, data):
        try:
            # print("sending data...")
            self.socket.send(serialize(data))
            # print("data sent\nreceiving world state...")
            return deserialize(self.socket.recv(2048))
        except socket.error as e:
            print(e)
            return None


# network = Network()
# from time import sleep
# from random import randint
# while True:
#     network.send(str(randint(0,100)))
#     sleep(1)
