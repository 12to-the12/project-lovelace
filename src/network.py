import socket
import msgpack

# from ssl import SSLSocket as socket
import ssl
from time import sleep
from msgpack import unpackb as deserialize
from msgpack import packb as serialize
from time import time as epoch
from spatial import ball

sleep_ms = lambda x: sleep(x / 1000)
import threading

# # import pickle
# from pickle import dumps as serialize
# from pickle import loads as deserialize


class Frenship:
    def __init__(self):
        self.snapshot_interval_ms = 50  # ms

        self.worldstate = {}
        # worldstate["this is apossible alernativet"] = "2"

        # print(worldstate)
        self.server_address = "lovelace.loganhillyer.me"
        # self.server_address = "47.155.218.95"
        # self.server_address = "192.168.4.107"

        self.init_tcp()
        self.launch_streams()
        # self.init_udp()

    def launch_streams(self):
        global worldstate
        worldstate = {1: 2}
        self.send_position_thread = threading.Thread(target=self.sending)
        self.send_position_thread.start()

        self.read_worldstate_thread = threading.Thread(target=self.receiving)
        self.read_worldstate_thread.start()

    def receiving(self):
        global worldstate
        while True:
            # print("listening...")
            # try:
            packet = self.tcp_scan()
            if packet == None:
                continue
            if not packet:
                print("<connection terminated>")
                break

            # print(f"packet received: {packet}")
            if packet["type"] == "worldstate":
                # print(f"worldstate updated")
                # print(f"networking's worldstate: {worldstate}")
                self.worldstate = packet["worldstate"]

            if packet["type"] == "epoch":
                remote = packet["timestamp"]
                local = epoch()
                diff = local - remote
                print(diff)
        # except:
        #     print("failed while scanning")
        # print(worldstate)
        # sleep_ms(100)

    def sending(self):
        while True:
            packet = {
                "type": "player_state",
                "id": self.connection_id,
                "player_state": {
                    "position": (ball.pos.x, ball.pos.y, ball.pos.z),
                    "velocity": (ball.vel.x, ball.vel.y, ball.vel.z),
                    "acceleration": (ball.acc.x, ball.acc.y, ball.acc.z),
                },
                "timestamp": epoch(),
            }
            # print(packet)
            # print("sending position")
            # try:
            self.tcp_send(packet)
            # except Exception as e:
            #     print("failed to send packet")
            sleep_ms(self.snapshot_interval_ms)

    def init_tcp(self):
        # context = ssl.create_default_context()
        #  context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.load_verify_locations("rootCA.pem")

        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

        self.server_port = 5002

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
            self.tcp_sock.connect((self.server_address, self.server_port))
            print("connection successful")
            return deserialize(self.tcp_sock.recv(2048), strict_map_key=False)
        except:
            print("connection failed")
            pass

    def tcp_send(self, data):
        try:
            # print("sending data...")
            self.tcp_sock.send(serialize(data))
            # print("data sent")
        except socket.error as e:
            print(e)
            return None

    def tcp_scan(self):
        # try:
        data = self.tcp_sock.recv(2048 * 2)
        try:
            packet = deserialize(data, strict_map_key=False)
            return packet
        except Exception as e:
            try:
                for packet in msgpack.unpackb(data, strict_map_key=False):
                    print(packet)
                print(f"{e}")
                print(data)
            except:
                print(f"{e}")
                print(data)

    # except Exception as e:
    #     print("problem receiving data")
    # raise(Exception(e))

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
