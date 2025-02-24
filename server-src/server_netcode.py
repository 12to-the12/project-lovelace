from os import times_result, wait

# import ssl

# import msgpack
import random
import socket
import threading
from time import sleep
from time import time as epoch
import sys

from queue import Queue

# from msgpack import unpackb as deserialize
# from msgpack import packb as serialize

# from marshal import dumps as serialize
# from marshal import loads as deserialize

from json import dumps
from json import loads as deserialize


def epoch_ms():
    return epoch() * 1e3


def serialize(packet):
    # if isinstance(packet, str):
    #     print("encoding string to bytes")
    #     packet = packet.encode()
    #     print(packet)
    data = dumps(packet)
    data = bytes(data, encoding="utf-8")
    return data


from config import config
from worldstate import worldstate

sleep_ms = lambda x: sleep(x / 1000)


class World:
    def __init__(self):
        self.clients = []

    def add_client(self, client_id):
        self.clients.append(client_id)


class network:
    def __init__(self):
        self.sending_connections = []
        self.receiving_connections = []
        self.incoming_addr = ""
        self.tcp_port = 5004
        self.udp_listening_port = 5002
        self.client_listening_port = 5003
        self.snapshot_interval_ms = config.snapshot_interval_ms  # ms
        self.client_update_interval_ms = config.snapshot_interval_ms  # ms
        # actually dependent on clientside interval, assumed to be same
        self.snapshot_buffer_size = 1 / (
            self.client_update_interval_ms / 1000
        )  # one second
        self.worlds = {0: World()}
        self.client_handlers = []
        self.address_lookup = {}

        self.udp_sending_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.udp_listening_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("attempting UDP socket bind:")
        try:
            self.udp_listening_sock.bind(("", self.udp_listening_port))
            print("UDP socket bound successfully")
        except socket.error as message:
            print("Bind failed. Error Code : " + str(message))
            sys.exit()

        print("starting udp listening thread...")

        self.udp_loop_thread = threading.Thread(
            target=self.udp_packet_input_hub, args=(self.udp_listening_sock,)
        )
        self.udp_loop_thread.daemon = True  # disposable
        self.udp_loop_thread.start()

        print("starting udp broadcasting thread...")
        self.broadcast_queue = Queue()
        self.udp_broadcaster_thread = threading.Thread(
            target=self.broadcaster, args=(self.udp_sending_sock,)
        )
        self.udp_broadcaster_thread.daemon = True  # disposable
        self.udp_broadcaster_thread.start()

        self.worldstate_writer_thread = threading.Thread(
            target=self.worldstate_writer, args=()
        )
        self.worldstate_writer_thread.daemon = True  # disposable
        self.worldstate_writer_thread.start()

        while True:
            sleep(10)

    def handle_packet(self, packet, address):
        if not packet:
            raise (Exception("<connection terminated>"))
        try:
            if packet["type"] == "ping":
                response = {
                    "type": "pong",
                    "timestamp": epoch(),
                    "original_timestamp": packet["timestamp"],
                }
                self.broadcast_queue.put((response, address))
            if packet["type"] == "join":
                response = {
                    "type": "OK",
                    "timestamp": epoch(),
                    "world_id": 0,
                }
                print("new client sent join request, returning OK request")
                client_id = packet["client_id"]
                self.worlds[0].add_client(client_id)
                self.address_lookup[client_id] = address
                self.broadcast_queue.put((response, address))
                print("response added to queue")

                # client_thread = threading.Thread(
                #     target=self.client_handler, args=(,)
                # )
                # self.client_handlers.append(client_thread)
                # self.udp_loop_thread.daemon = True  # blocks main from exiting
                # self.udp_loop_thread.start()
        except Exception as e:
            self.udp_listening_sock.close()
            self.udp_sending_sock.close()
            raise (Exception(e))

    def address_from_id(self, client_id):
        return self.address_lookup[client_id]

    def worldstate_writer(self):
        WORLDSTATE = {
            "type": "worldstate",
            "timestamp": epoch(),
            "friend": (random.randint(0, 480), random.randint(0, 320)),
        }
        self.broadcast_queue.put((WORLDSTATE, "192.168.4.150"))
        sleep_ms(1000)

    # world packets will be added to it's queue
    def broadcaster(self, sock):
        while True:
            try:
                while self.broadcast_queue.qsize() > 0:
                    (packet, address) = self.broadcast_queue.get()
                    # address = self.address_from_id(connecton_id)
                    print(
                        f"sending:\n{packet} to {address}:{self.client_listening_port}"
                    )
                    self.udp_send(sock, packet, address, self.client_listening_port)
                    print("packet sent")
                    self.broadcast_queue.task_done()
                    sleep_ms(1)

            except Exception as e:
                self.udp_listening_sock.close()
                self.udp_sending_sock.close()
                raise (Exception(e))
        # the broadcaster ingests the broadcast queue,
        # as well as broadcasting the correct world to the correct clients
        # sleep_ms(self.snapshot_interval_ms)

    def udp_packet_input_hub(self, sock):
        global worldstate
        # pass
        while True:
            try:
                (packet, (address, port)) = self.udp_scan(sock)
                print(f"{packet} from {address}:{port}")
                # self.udp_send(sock, packet, address, port)
                self.handle_packet(packet, address)
            except Exception as e:
                self.udp_listening_sock.close()
                self.udp_sending_sock.close()
                raise (Exception(e))

    def udp_send(self, sock, packet, address, port):
        data = serialize(packet)

        addr = socket.getaddrinfo(address, port, 0, socket.SOCK_STREAM)[0][-1]

        bytes_sent = sock.sendto(data, addr)

    def udp_scan(self, sock):
        data, (address, port) = sock.recvfrom(2048)
        # packet = deserialize(data, strict_map_key=False)
        packet = deserialize(data)

        return (packet, (address, port))
