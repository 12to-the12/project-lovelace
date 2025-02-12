import socket
# import pickle
from pickle import dumps as serialize
from pickle import loads as deserialize


class Network:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server = "lovelace.loganhillyer.me"
        # self.server = "47.155.218.95"

        self.port = 1111

        self.addr = (self.server, self.port)

        self.connection_id = self.connect()
        print("connection successful ")
        print(f"response: {self.connection_id}")

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
            self.socket.send(serialize(data))
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
