from os import times_result
import ssl
import msgpack
import socket
import threading
from time import sleep
from time import time as epoch
import sys
from msgpack import unpackb as deserialize
from msgpack import packb as serialize
from worldstate import worldstate

sleep_ms = lambda x: sleep(x / 1000)


class network:
    def __init__(self):
        self.sending_connections = []
        self.receiving_connections = []
        self.incoming_addr = ""
        self.port = 5002
        self.snapshot_interval_ms = 1  # ms
        self.snapshot_buffer_size = 10
        self.queue = []
        # context = ssl.create_default_context()

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        self.context.load_cert_chain(
            certfile="/home/logan/certs/rootCA.pem",
            keyfile="/home/logan/certs/rootCA.key",
        )

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.sock = self.context.wrap_socket(self.sock, server_side=True)
        print("attempting bind:")
        try:
            self.sock.bind((self.incoming_addr, self.port))
            print("socket bound successfully")
        except socket.error as message:
            print("Bind failed. Error Code : " + str(message))
            sys.exit()

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

    def sending(self, sock, connection_id):
        global worldstate

        while True:
            for _ in self.queue:
                sock.sendall(serialize(self.queue.pop()))
            packet = {
                "type": "worldstate",
                "worldstate": worldstate,
                "timestamp": epoch(),
            }
            # packet = {"type": "epoch", "timestamp": epoch()}
            try:
                sock.sendall(serialize(packet))
            except Exception as e:
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
                # print("listening...")
                data = sock.recv(2048)

                packet = deserialize(data, strict_map_key=False)
                if not packet:
                    print("<connection terminated>")
                    break
                # print(f"received{packet}")
                # try:
                if packet["type"] == "player_state":
                    player_state = worldstate["players"][connection_id]["player_state"]
                    timestamp = packet["timestamp"]
                    player_state["snapshots"][timestamp] = packet["player_state"]
                    player_state["buffer"].insert(0, timestamp)
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
                # except Exception as e:
                #     print("error, couldn't add snapshot")
                #     print(e)
                # try:
                #     self.clean_snapshots(connection_id)
                # except Exception as e:
                #     print("error, couldn't clean snapshots")
                #     print(e)

            except Exception as e:
                print(
                    f"receiving messed up for client {connection_id},terminating connection and deleting entries"
                )
                del worldstate["players"][connection_id]
                # raise Exception(e)
                # print(e)
                sock.close()
                break
            # sleep_ms(100)

    def await_connections(self):
        connection_id = 1
        self.sock.listen(5)
        while True:
            print(f"awaiting connections on port {self.port}...")
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
            conn.send(serialize(connection_id))

            sending_thread.start()
            receiving_thread.start()
            connection_id += 1
