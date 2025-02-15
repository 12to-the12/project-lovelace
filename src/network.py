import socket
import msgpack

# from ssl import SSLSocket as socket
import ssl
from time import sleep
from msgpack import unpackb as deserialize
from msgpack import packb as serialize

# # import pickle
# from pickle import dumps as serialize
# from pickle import loads as deserialize


class Frenship:
    def __init__(self):
        # self.server_address = "lovelace.loganhillyer.me"
        # self.server_address = "47.155.218.95"
        self.server_address = "192.168.4.107"

        self.init_tcp()
        # self.init_udp()

    def init_tcp(self):
        # context = ssl.create_default_context()
        #  context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.load_verify_locations("rootCA.pem")

        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.port = 5002

        # self.addr = (self.server_address, self.port)
        # self.socket = socket.create_connection(self.addr)
        self.tcp_sock = context.wrap_socket(
            self.tcp_sock, server_hostname=self.server_address
        )
        # self.tcp_sock = self.socket

        self.connection_id = self.tcp_connect()
        # print("connection successful ")
        print(f"assigned connection ID: {self.connection_id}")

    def tcp_connect(self):
        try:
            print("attempting connection...")
            self.tcp_sock.connect((self.server_address, self.port))
            print("connection successful")
            return deserialize(self.tcp_sock.recv(2048))
        except:
            print("connection failed")
            pass

    def tcp_send(self, data):
        try:
            # print("sending data...")
            self.tcp_sock.send(serialize(data))
            # print("data sent\nreceiving world state...")
            return deserialize(self.tcp_sock.recv(2048))
        except socket.error as e:
            print(e)
            return None

    def tcp_scan(self):
        data = self.tcp_sock.recv(2048)
        packet = deserialize(data)
        return packet

    def init_udp(self):
        # IP = "47.155.218.95"
        # UDP_IP = "192.168.4.95"
        # UDP_IP = "127.0.0.1"
        MY_IP = "192.168.4.95"
        # UDP_PORT = 5003
        self.SERVER_TO_CLIENT_PORT = 5003
        self.CLIENT_TO_SERVER_PORT = 5002

        self.downstream = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )  # Internet  # UDP
        self.downstream.bind((MY_IP, self.SERVER_TO_CLIENT_PORT))

        self.upstream = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )  # Internet  # UDP
        # self.upstream.bind((UDP_IP, self.CLIENT_TO_SERVER_PORT))

    def udp_scan(self):
        data, addr = self.downstream.recvfrom(1024)
        data = msgpack.unpackb(data, strict_map_key=False)
        return data

    def udp_send(self, data):
        data = msgpack.packb(data)
        self.upstream.sendto(data, (self.server_address, self.CLIENT_TO_SERVER_PORT))
