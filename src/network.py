import socket
import ssl
from time import sleep

# from msgpack import unpackb as deserialize
# from msgpack import packb as serialize

# import marshal

from marshal import dumps as serialize
from marshal import loads as deserialize
from time import time as epoch
from timing import Pulse
from spatial import ball
from config import config

sleep_ms = lambda x: sleep(x / 1000)
# import threading
import _thread

class Frenship:
    def __init__(self):
        self.snapshot_interval_ms = config.snapshot_interval_ms  # ms

        self.worldstate = {}
        self.server_address = config.server_address

        self.start = epoch()
        self.packets_received = 0
        self.bad_packets_received = 0
        self.bad_packet_threshold_ms = 1.8
        self.init_tcp()
        self.init_udp()

        if config.pingmode:
            self.ping_mode()

        self.launch_streams()

    def ping_mode(self):
        while True:
            self.tcp_send(epoch())
            packet = self.tcp_scan()
            ping = (epoch() - packet) * 1000
            if ping > self.bad_packet_threshold_ms:
                self.bad_packets_received += 1
                badrate = self.bad_packets_received / (epoch() - self.start)
                print(
                    f"packets above {self.bad_packet_threshold_ms}ms per second: {badrate:.2f}"
                )

    def init_tcp(self):

        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.load_verify_locations("rootCA.pem")

        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.tcp_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        # self.tcp_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, False)

        self.server_port = 5002
        self.tcp_sock = context.wrap_socket(
            self.tcp_sock, server_hostname=self.server_address
        )

        self.connection_id = self.tcp_connect()
        print(f"assigned connection ID: {self.connection_id}")

    def tcp_connect(self):
        try:
            print("attempting connection...")
            self.tcp_sock.connect((self.server_address, self.server_port))
            print("connection successful")
            # return deserialize(self.tcp_sock.recv(2048), strict_map_key=False)
            return deserialize(self.tcp_sock.recv(2048))
        except:
            print("connection failed")
            pass

    def tcp_send(self, data):
        try:
            self.tcp_sock.sendall(serialize(data))
        except socket.error as e:
            print(e)
            return None

    def tcp_scan(self):
        data = self.tcp_sock.recv(2048 * 8)
        try:
            # packet = deserialize(data, strict_map_key=False)
            packet = deserialize(data)
            self.packets_received += 1

            return packet
        except Exception as e:
            raise (Exception(e))

    def launch_streams(self):
        global worldstate
        worldstate = {1: 2}
        # self.send_position_thread = threading.Thread(target=self.sending)
        self.send_position_thread = _thread.start_new_thread(self.sending, ())

        # this prevents threads from persisting past main
        # self.send_position_thread.daemon = True
        # self.send_position_thread.start()

        # self.read_worldstate_thread = threading.Thread(target=self.receiving)
        self.read_worldstate_thread = _thread.start_new_thread(self.receiving, ())
        # self.read_worldstate_thread.daemon = True
        # self.read_worldstate_thread.start()

    def receiving(self):
        global worldstate
        while True:
            try:
                packet = self.tcp_scan()
                if packet == None:
                    continue
                if not packet:
                    print("<connection terminated>")
                    break

                if packet["type"] == "worldstate":
                    self.worldstate = packet["worldstate"]

                if packet["type"] == "pong":
                    original = packet["client_timestamp"]
                    remote = packet["timestamp"]
                    now = epoch()
                    # print("ping")
                    # print(f"\tto server: {(remote - original) * 1_000:0.2f}ms")
                    # print(f"\treturn: {(now - remote) * 1000:.2f}ms")
                    print(f"ping: {(now - original) * 1000:.2f}ms")

            except:
                continue
        # sleep_ms(100)

    def sending(self):
        timing_pulse = Pulse(period=(1000 / 1000))
        while True:
            if timing_pulse.read():
                # send epoch packet
                # print("sending ping")
                packet = {
                    "type": "ping",
                    "timestamp": epoch(),
                }
                self.tcp_send(packet)

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
            self.udp_send(packet)
            sleep_ms(self.snapshot_interval_ms)

    def init_udp(self):
        # self.MY_IP = "192.168.4.95"
        # UDP_PORT = 5003
        # self.SERVER_TO_CLIENT_PORT = 5003
        self.CLIENT_TO_SERVER_PORT = 5003

        # self.downstream = socket.socket(
        #     socket.AF_INET, socket.SOCK_DGRAM
        # )  # Internet  # UDP
        # self.downstream.bind((MY_IP, self.SERVER_TO_CLIENT_PORT))

        self.udp_sender_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.upstream.bind((UDP_IP, self.CLIENT_TO_SERVER_PORT))

    def udp_scan(self):
        data, addr = self.downstream.recvfrom(1024)
        # packet = deserialize(data, strict_map_key=False)
        packet = deserialize(data)
        return data

    def udp_send(self, packet):
        data = serialize(packet)
        self.udp_sender_sock.sendto(
            data, (self.server_address, self.CLIENT_TO_SERVER_PORT)
        )
