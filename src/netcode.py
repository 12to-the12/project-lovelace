import secrets
import socket
from time import sleep
from ujson import dumps
from ujson import loads as deserialize
import ntptime
from sprite import pos_sprite
import network
from time import time_ns as epoch_ns
from sprite import world
from time import time as epoch
from config import config
import secrets

# from machine import soft_reset as quit
from timing import Pulse
from screenwrite import printsc

from time import ticks_ms, ticks_us
from player_input import button_left, button_right, joystick

# from queue import Queue


# doesn't actually need to be threadsafe
# I'll implement the same api though
class Queue:
    def __init__(self):
        self.q = []

    def get(self):
        return self.q.pop()

    def qsize(self):
        return len(self.q)

    def put(self, data):
        self.q.insert(0, data)

    def task_done(self):
        pass


def epoch_float():
    return float(epoch_ns()) / 1.0e9


def serialize(packet):
    data = dumps(packet)
    data = data.encode()
    return data


sleep_ms = lambda x: sleep(x / 1000)


class Network_Connection:
    def __init__(self):
        self.connect_to_wifi()
        self.init_udp()

    def connect_to_wifi(self):

        print("Wifi")
        wlan = network.WLAN(network.STA_IF)
        print("wlan defined")
        print(wlan)
        wlan.active(True)
        print("wlan activated")
        wlan.connect(secrets.ssid, secrets.wifi_password)
        printsc("Connecting to WiFi", end="")
        while not wlan.isconnected():
            printsc(".", end="")
            # print(wlan)
            # print(wlan.isconnected())
            sleep(1)
        # print(wlan.isconnected())
        # print(wlan.ifconfig())
        printsc()

    def init_udp(self):
        self.listening_port = 5003

        self.udp_receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.udp_receiver_sock.setblocking(False)

        print(f"binding receiver to {self.listening_port}")
        addr = socket.getaddrinfo(
            "0.0.0.0", self.listening_port, 0, socket.SOCK_STREAM
        )[0][-1]
        self.udp_receiver_sock.bind(addr)

        self.udp_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def udp_scan(self):
        data, (address, port) = self.udp_receiver_sock.recvfrom(2048)
        packet = deserialize(data)
        # if addr != self.server_address:
        #     raise (Exception("received packet from non server address"))
        return packet

    def udp_send(self, packet, address, port):
        data = serialize(packet)
        addr = socket.getaddrinfo(address, port, 0, socket.SOCK_STREAM)[0][-1]

        self.udp_sender.sendto(data, addr)


class Server_Connection:
    def __init__(self):
        

        self.snapshot_interval_ms = config.snapshot_interval_ms  # ms

        self.worldstate = {}
        self.addr = secrets.server_address
        self.port = 5002
        self.start = epoch()
        self.packets_received = 0
        self.bad_packets_received = 0
        self.bad_packet_threshold_ms = 1.8

        self.broadcast_queue = Queue()
        self.pings = Pulse()

        printsc("starting network operations")
        self.network = Network_Connection()

        self.syncronize_time()
        self.initiate_duplex_udp_connection()

    def syncronize_time(self):
        from time import localtime

        printsc("syncronizing time with remote server")
        # print(ntptime.time())
        # print(localtime())

        for _ in range(1):
            try:
                ntptime.settime()
                printsc(".", end="")
                sleep(1)
            except:
                break
        printsc()

        self.us_offset = ticks_us
        # this has technique has issues within the second
        self.local_epoch = epoch()
        # except:
        # break
        # print(localtime())

    def timestamp(self):
        time_since = (ticks_us() - self.us_offset()) / 1e6

        return self.local_epoch + time_since

    def initiate_duplex_udp_connection(self):
        # perform connection routine
        # self.machine_id = hash(machine.unique_id())
        JOIN = {
            "type": "join",
            "timestamp": self.timestamp(),
            # "client_id": self.machine_id,
        }

        waiting = True
        while waiting:
            self.network.udp_send(JOIN, self.addr, self.port)
            printsc(
                f"\njoin request sent to {self.addr}, waiting for reply",
                end="",
            )
            for _ in range(10):
                try:
                    packet = self.network.udp_scan()
                    if packet:
                        print(packet)
                        waiting = False
                        break

                except OSError as e:
                    if e.args[0] != 11:  # ignore if just no data (EAGAIN)
                        raise Exception(e)
                sleep_ms(100)
                printsc(".", end="")
            sleep(1)

        printsc()
        print(packet)
        if packet["type"] == "OK":
            printsc("connection established, joining world...")

            self.world_id = packet["world_id"]
            world.legitimize(self.world_id)

    def handle_packet(self, packet):
        if packet["type"] == "worldstate":
            print("received worldstate:")
            print(packet)
            for name, data in packet["worldstate"]["sprites"].items():

                # if name not in world.sprites.keys(): self.world.sprites[name]=pos_sprite()
                world.sprites[name] = data  # dict
        if packet["type"] == "ping":
            response = {
                "type": "pong",
                "timestamp": epoch_float(),
                "original_timestamp": packet["timestamp"],
            }
            self.broadcast_queue.put(response)
        if packet["type"] == "pong":
            original_timestamp = packet["original_timestamp"]
            now = epoch_float()
            elapsed_ms = now - original_timestamp
            print("pong received")
            # print(f"original: {packet["original_timestamp"]:.3f}")
            # print(f"remote: {packet["timestamp"]:.2f}")
            # print(f"now: {now:.2f}")
            print(f"{elapsed_ms}ms roundtrip\n")

    def send_playerstate(self):
        packet = {
            "type": "playerstate",
            # "client_id": self.machine_id,
            "world_id": getattr(self, "world_id", 0),
            "timestamp": epoch_float(),
            "playerstate": {
                "x": joystick.x,
                "y": joystick.y,
                "left": button_left(),
                "right": button_right(),
                "screen_presses": [],
            },
        }
        self.broadcast_queue.put(packet)

    def loop_over_io(self):
        if self.pings.read() and config.pingmode:
            print("sending ping...")
            self.broadcast_queue.put(
                {
                    "type": "ping",
                    "timestamp": epoch_float(),
                }
            )

        try:
            packet = self.network.udp_scan()
            if packet:
                self.handle_packet(packet)
        except OSError as e:
            if e.args[0] != 11:  # ignore if just no data (EAGAIN)
                raise Exception(e)

        while self.broadcast_queue.qsize() > 0:
            packet = self.broadcast_queue.get()
            self.network.udp_send(packet, self.addr, self.port)
            self.broadcast_queue.task_done()


# def test_start_connection():
#     connection = Connection()

if __name__ == "__main__":
    print("This is the networking file!")
