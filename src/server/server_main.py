#!/home/logan/server/.venv/bin/python
#!/usr/bin/python3
from time import sleep
import msgpack
import socket
import threading
from server_network import network

sleep_ms = lambda x: sleep(x / 1000)

nextclientid = -1


def getnextclientid():
    global nextclientid
    nextclientid += 1
    return nextclientid


# one thread per client, in addition to one for the receiver?
worldstate = {}


def sender():
    # UDP_IP = "127.0.0.1"
    UDP_IP = "192.168.4.95"
    # UDP_IP = "127.0.0.1"
    UDP_PORT = 5003
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
    n = 0
    while True:
        # packet = {"type": "unspecified", "data": n}
        packet = worldstate

        MESSAGE = msgpack.packb(packet)
        sender_socket.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        # print(f"sent {packet}")
        n += 1

        # print("waiting for incoming...")
        # data, addr = sock.recvfrom(1024)
        # data = msgpack.unpackb(data)
        # print(data)

        sleep_ms(10)


# 5002 is for client to server
def receiver():
    global worldstate
    MY_IP = "192.168.4.107"
    UDP_PORT = 5002
    receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
    receiver_sock.bind((MY_IP, 5002))
    while True:
        # print("listening...")
        data, (address, port) = receiver_sock.recvfrom(1024)
        print(f"message received from {address} over port {port}")
        data = msgpack.unpackb(data)
        # print(f"received: {data}")
        if data["type"] == "player_state":
            worldstate[data["id"]] = {
                "address": address,
                "player_state": data["player_state"],
                "timestamp": data["timestamp"],
            }
        if data["type"] == "connection_request":
            print("connection request received, assigning id")
            sender_socket = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM
            )  # Internet  # UDP
            packet = {"type": "id_assignment", "id": getnextclientid()}
            MESSAGE = msgpack.packb(packet)
            while True:
                print(f"sending packet to {address}:{port}")
                sender_socket.sendto(MESSAGE, (address, port))
                sleep_ms(10)


if __name__ == "__main__":
    # while True:
    #     conn, addr = sock.accept
    network = network()
    # network.await_connections()

    # sender_thread = threading.Thread(target=sender, args=())
    # sender_thread.start()

    # receiver_thread = threading.Thread(target=receiver, args=())
    # receiver_thread.start()
    print("I am here now")
