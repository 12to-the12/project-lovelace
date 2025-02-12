import socket
# import pickle
from pickle import dumps as serialize
from pickle import loads as deserialize


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "lovelace.loganhillyer.me"
        # self.server = "47.155.218.95"

        self.port = 1111

        self.addr = (self.server, self.port)

        self.id = self.connect()
        print("connection successful ")
        print(f"response: {self.id}")

    def connect(self):

        try:
            print("attempting connection...")
            self.client.connect(self.addr)
            return deserialize(self.client.recv(2048))
        except:
            print("connection failed")
            pass

    def send(self, data):
        print(f"sending the string '{data}'")
        try:
            self.client.send(serialize(data))
            return deserialize(self.client.recv(2048))
        except socket.error as e:
            print(e)




# network = Network()
# from time import sleep
# from random import randint
# while True:
#     network.send(str(randint(0,100)))
#     sleep(1)
