from os import times_result
import ssl
import msgpack
import socket
import threading
from time import sleep
from time import time as epoch
import sys

# from msgpack import unpackb as deserialize
# from msgpack import packb as serialize

from marshal import dumps as serialize
from marshal import loads as deserialize
from config import config
from worldstate import worldstate

sleep_ms = lambda x: sleep(x / 1000)


class network:
    def __init__(self):
        self.sending_connections = []
        self.receiving_connections = []
        self.incoming_addr = ""
        self.tcp_port = 5002
        self.udp_listening_port = 5003
        self.snapshot_interval_ms = config.snapshot_interval_ms  # ms
        self.client_update_interval_ms = config.snapshot_interval_ms  # ms
        # actually dependent on clientside interval, assumed to be same
        self.snapshot_buffer_size = 1 / (
            self.client_update_interval_ms / 1000
        )  # one second
        self.queue = []
        # context = ssl.create_default_context()

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        self.context.load_cert_chain(
            certfile="/home/logan/certs/rootCA.pem",
            keyfile="/home/logan/certs/rootCA.key",
        )

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, False)

        self.sock = self.context.wrap_socket(self.sock, server_side=True)
        print("attempting bind:")
        try:
            self.sock.bind((self.incoming_addr, self.tcp_port))
            print("socket bound successfully")
        except socket.error as message:
            print("Bind failed. Error Code : " + str(message))
            sys.exit()

        self.udp_listening_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.udp_listening_socket.bind(("", self.udp_listening_port))
        except socket.error as message:
            print("Bind failed. Error Code : " + str(message))
            sys.exit()

        self.udp_update_channel = threading.Thread(
            target=self.udp_update, args=(self.udp_listening_socket,)
        )
        self.udp_update_channel.daemon = True
        self.udp_update_channel.start()

        self.handle_new_connections = threading.Thread(target=self.await_connections)
        self.handle_new_connections.start()

    # # gets rid of snapshots older than 5 seconds
    # def clean_snapshots(self, connection_id):
    #     global worldstate
    #     most_recent = 0
    #     times = worldstate["players"][connection_id]["player_state"].keys()
    #     most_recent = max(times)
    #     for timestamp in times:
    #         if (most_recent - timestamp) > 5:
    #             del worldstate["players"][connection_id]["player_state"][timestamp]
    def handle_packet(self, packet, connection_id):
        if not packet:
            raise (Exception("<connection terminated>"))
            # print("<connection terminated>")
            # break
        # print(f"received{packet}")
        # try:
        if packet["type"] == "player_state":
            player_state = worldstate["players"][connection_id]["player_state"]
            timestamp = packet["timestamp"]
            player_state["snapshots"][timestamp] = packet["player_state"]
            player_state["buffer"].insert(0, timestamp)
            # print(len(player_state["buffer"]))
            if len(player_state["buffer"]) > self.snapshot_buffer_size:
                stamptodelete = player_state["buffer"].pop()
                del player_state["snapshots"][stamptodelete]
        if packet["type"] == "ping":
            outgoing = {
                "type": "pong",
                "timestamp": epoch(),
                "client_timestamp": packet["timestamp"],
            }
            self.queue.insert(0, outgoing)

    def udp_update(self, sock):
        global worldstate
        # pass
        while True:
            try:
                (packet, (address, port)) = self.udp_scan(sock)
                connection_id = packet["id"]
                self.handle_packet(packet, connection_id)
            except:
                pass

    def sending(self, sock, connection_id):
        global worldstate

        while True:
            for _ in self.queue:
                self.tcp_send(sock, self.queue.pop())
                # sock.sendall(serialize(self.queue.pop()))
            packet = {
                "type": "worldstate",
                "worldstate": worldstate,
                "timestamp": epoch(),
            }
            # packet = {"type": "epoch", "timestamp": epoch()}
            try:
                self.tcp_send(sock, packet)
                # sock.sendall(serialize(packet))
            except Exception as e:
                print("send error")
                print(
                    f"sending messed up for client {connection_id},terminating connection"
                )
                print(e)
                sock.close()
                break
            sleep_ms(self.snapshot_interval_ms)

    def receiving(self, sock, connection_id):
        global worldstate
        worldstate["players"][connection_id] = {
            "player_state": {"buffer": [], "snapshots": {}}
        }
        # sock.send(serialize(connection_id))
        while True:
            try:
                packet = self.tcp_scan(sock)
                self.handle_packet(packet, connection_id)
            except Exception as e:
                print(
                    f"broken connection for {connection_id},\nterminating connection\nand deleting playerstate"
                )
                del worldstate["players"][connection_id]
                # raise Exception(e)
                print(e)
                print("closing socket")
                sock.close()
                break
            # sleep_ms(100)
        print(f"{connection_id} receiving terminated")

    def ping_mode(self, sock):
        while True:
            packet = self.tcp_scan(sock)
            self.tcp_send(sock, packet)

    def await_connections(self):
        connection_id = 1
        self.sock.listen(5)
        while True:
            print(f"awaiting connections on port {self.tcp_port}...")
            conn, address = self.sock.accept()

            print(f"connection accepted,spawning thread for client {connection_id}")
            sending_thread = threading.Thread(
                target=self.sending,
                args=(
                    conn,
                    connection_id,
                ),
            )
            receiving_thread = threading.Thread(
                target=self.receiving,
                args=(
                    conn,
                    connection_id,
                ),
            )
            # just in case I don't want them to persist
            sending_thread.daemon = True
            receiving_thread.daemon = True

            self.sending_connections.append(sending_thread)
            self.receiving_connections.append(receiving_thread)
            self.tcp_send(conn, connection_id)

            if config.pingmode:
                self.ping_mode(conn)

            sending_thread.start()
            receiving_thread.start()
            connection_id += 1

    def tcp_send(self, sock, packet):
        # print("sending data...")
        sock.sendall(serialize(packet))
        # print("data sent")

    def tcp_scan(self, sock):
        data = sock.recv(2048 * 4)
        try:
            # packet = deserialize(data, strict_map_key=False)
            packet = deserialize(data)

            return packet
        except Exception as e:
            try:
                # for packet in msgpack.unpackb(data, strict_map_key=False):
                for packet in msgpack.unpackb(data):
                    print(packet)
                print("scan error")
                print(f"{e}")
                print(data)
            except:
                print("scan error")
                print(f"{e}")
                print(data)

    def udp_send(self, sock, packet, address, port):
        data = serialize(packet)
        sock.sendto(data, (address, port))

    def udp_scan(self, sock):
        data, (address, port) = sock.recvfrom(2048)
        # packet = deserialize(data, strict_map_key=False)
        packet = deserialize(data)

        return (packet, (address, port))
