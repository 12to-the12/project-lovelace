# from os import posix_fadvise, times_result, wait

# import ssl

# import msgpack
import random
import socket
import threading
from time import sleep
from time import time as epoch
import sys

from queue import Queue
from server_sprite import Entity

# from msgpack import unpackb as deserialize
# from msgpack import packb as serialize

# from marshal import dumps as serialize
# from marshal import loads as deserialize

from json import dumps
from json import loads as deserialize


def epoch_ms():
    return epoch() * 1e3


def serialize(packet):
    data = dumps(packet)
    data = bytes(data, encoding="utf-8")
    return data


from config import config
from worldstate import worldstate

sleep_ms = lambda x: sleep(x / 1000)



class World:
    next_player_id = 0
    def __init__(self, world_id):
        self.world_id = world_id
        self.clients = {}
        self.friend_x = random.randint(0, 480 - 32)
        self.friend_y = random.randint(0, 320 - 32)
        self.friend_vx = random.randint(-5, 5)
        self.friend_vy = random.randint(-5, 5)

        self.display_width = 480
        self.display_height = 320
        # where the world is in relation to the viewport
        # top left corner of the screen
        self.viewport_entity = Entity(world=self)

    def add_client(self, client_address: str):
        # assert type(client_address) == str, client_address
        entity = Entity(world=self)
        entity.player_id = self.next_player_id
        self.next_player_id += 1
        self.clients[client_address] = entity

    def update_client(self, client_address, playerstate=None):
        if not client_address in self.clients.keys():
            self.add_client(client_address)
        if playerstate:

            # print(f"{playerstate}")
            # assert "pos" in playerstate.keys()
            # position_list = playerstate["pos"]
            x = playerstate["x"]
            y = playerstate["y"]
            self.clients[client_address].push([x, y])
            self.clients[client_address].apply()

    def get_state_packet(self):
        self.friend_x += self.friend_vx
        self.friend_y += self.friend_vy
        self.friend_x %= 480
        self.friend_y %= 320
        sprites = {}
        for client_address, client_sprite in self.clients.items():
            sprites[f"player{client_sprite.player_id}"] = {
                "pos": [client_sprite.pos.x, client_sprite.pos.y, client_sprite.pos.z],
                "fname": client_sprite.fname,
                "dim": (client_sprite.w, client_sprite.h),
                "frame": client_sprite.frame
            }

        # sprites = {}
        # sprites["player"] = {"pos": (self.friend_x, self.friend_y, 0)}
        sprites["hole"] = {"fname": "blackhole.rgb", "dim": (64, 64), "pos": (240, 160, 0)}
        # for client in self.clients:
        #     sprites[client.client_id] = {"pos": client.pos}

        WORLDSTATE = {
            "type": "worldstate",
            "timestamp": epoch(),
            "worldstate": {"sprites": sprites},
        }
        return WORLDSTATE


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
        self.worlds = {0: World(0)}
        self.client_handlers = []

        self.clients = {}

        self.sockets = []

        self.udp_sending_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sockets.append(self.udp_sending_sock)
        self.udp_listening_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sockets.append(self.udp_listening_sock)

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
            target=self.udp_packet_output_hub, args=(self.udp_sending_sock,)
        )
        self.udp_broadcaster_thread.daemon = True  # disposable
        self.udp_broadcaster_thread.start()

        self.worldstate_writer_thread = threading.Thread(
            target=self.worldstate_writer, args=()
        )
        self.worldstate_writer_thread.daemon = True  # disposable
        self.worldstate_writer_thread.start()

        while True:
            sleep(1 / 2)

    def close_sockets(self):
        for sock in self.sockets:
            sock.close()

    def handle_packet(self, packet: str, address: str):
        if not packet:
            raise (Exception("<connection terminated>"))
        try:
            if packet["type"] == "playerstate":
                client_id = packet["client_id"]
                world_id = packet["world_id"]
                self.worlds[world_id].update_client(address, packet["playerstate"])

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
                self.worlds[0].update_client(address)
                # self.address_lookup[client_id] = address
                self.broadcast_queue.put((response, address))
                print("response added to queue")

                # client_thread = threading.Thread(
                #     target=self.client_handler, args=(,)
                # )
                # self.client_handlers.append(client_thread)
                # self.udp_loop_thread.daemon = True  # blocks main from exiting
                # self.udp_loop_thread.start()
        except Exception as e:
            self.close_sockets()
            raise (Exception(e))

    # def address_from_id(self, client_id):
    #     return self.address_lookup[client_id]

    # sends worldstate of given worlds to the IP addresses of connected clients
    def worldstate_writer(self):
        delay = 1 / config.fps
        while True:
            for world in self.worlds.values():
                for address, entity in world.clients.items():
                    self.broadcast_queue.put((world.get_state_packet(), address))
            sleep(delay)

    # world packets will be added to it's queue
    def udp_packet_output_hub(self, sock):
        while True:
            try:
                while self.broadcast_queue.qsize() > 0:
                    (packet, address) = self.broadcast_queue.get()
                    assert type(address) == str
                    # address = self.address_from_id(connecton_id)
                    print(
                        f"sending:\n{packet} to {address}:{self.client_listening_port}"
                    )
                    self.udp_send(sock, packet, address, self.client_listening_port)
                    # print("packet sent")
                    self.broadcast_queue.task_done()
                    sleep_ms(1)

            except Exception as e:
                self.close_sockets()
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
                self.close_sockets()
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
