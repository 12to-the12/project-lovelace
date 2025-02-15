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
        # context = ssl.create_default_context()

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        self.context.load_cert_chain(
            certfile="/home/logan/certs/rootCA.pem",
            keyfile="/home/logan/certs/rootCA.key",
        )

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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

    # gets rid of snapshots older than 5 seconds
    def clean_snapshots(self, connection_id):
        global worldstate
        most_recent = 0
        times = worldstate["players"][connection_id]["player_state"].keys()
        most_recent = max(times)
        for timestamp in times:
            if (most_recent - timestamp) > 5:
                del worldstate["players"][connection_id]["player_state"][timestamp]

    def sending(self, sock, connection_id):
        global worldstate

        while True:
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
            sleep_ms(50)

    def receiving(self, sock, connection_id):
        global worldstate
        worldstate["players"][connection_id] = {"player_state": {"buffer": []}}
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
                    # if player_state.get("new"):
                    #     player_state["old"] = player_state["new"]
                    player_state["buffer"].insert(
                        0,
                        {
                            "timestamp": packet["timestamp"],
                            "state": packet["player_state"],
                        },
                    )
                    if len(player_state["buffer"]) > 5:
                        player_state["buffer"].pop()

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
                    f"receiving messed up for client {connection_id},terminating connection"
                )
                raise Exception(e)
                # print(e)
                # sock.close()
                break

    def await_connections(self):
        connection_id = 1
        self.sock.listen(5)
        while True:
            print("awaiting connections...")
            conn, address = self.sock.accept()
            print("connection accepted,spawning client thread")
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
            self.sending_connections.append(sending_thread)
            self.receiving_connections.append(receiving_thread)
            conn.send(serialize(connection_id))

            sending_thread.start()
            receiving_thread.start()
            connection_id += 1
