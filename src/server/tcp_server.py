#!/home/logan/server/.venv/bin/python
#!/usr/bin/python3
from time import sleep
from pickle import dumps as serialize
from pickle import loads as deserialize
import ssl
import msgpack

import socket
import threading
# an entry per connection
# worldstate = ["deadbeef"]*10
worldstate = []


# class ClientConnection:
#     def __init__(self, client_ip):
#         self.client_ip = client_ip


# UDP_IP = "127.0.0.1"
# UDP_IP = "192.168.4.95"
# UDP_IP = "127.0.0.1"
# UDP_PORT = 5003

# n = 0
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
# while True:
#     MESSAGE = str(n).encode("utf-8")
#     MESSAGE = msgpack.packb(n)
#     sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
#     print(f"sent {n}")
#     n += 1

#     # print("waiting for incoming...")
#     # data, addr = sock.recvfrom(1024)
#     # data = msgpack.unpackb(data)
#     # print(data)

#     sleep(1)


# n = 0
# while True:
#     print(f"hello #{n}")
#     sleep(1)
#     n+=1


import socket
from _thread import start_new_thread
import sys

# server = "47.155.218.95"
server = ""
port = 5002

# context = ssl.create_default_context()
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(
    certfile="/home/logan/certs/rootCA.pem", keyfile="/home/logan/certs/rootCA.key"
)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# s = socket.create_connection((server, port))
sock = context.wrap_socket(sock, server_side=True)
print("attempting bind:")
try:
    sock.bind((server, port))
    print("socket bound successfully")
except socket.error as message:
    print("Bind failed. Error Code : " + str(message))
    sys.exit()


sock.listen()


def threaded_client(conn, connection_id):
    global worldstate
    # this is sent upon connection

    conn.send(serialize(connection_id))
    while True:
        try:
            data = deserialize(conn.recv(2048))
            print(f"received {data}")
            if not data:
                print("disconnected")
                break
            else:  # here is everything is good
                print(f"received and verified: {data} for ID:{connection_id}")
                print("updating worldstate...")
                try:
                    worldstate[connection_id] = data
                except:
                    worldstate.append(data)
                print(f"world updated")
                reply = worldstate
                print(f"responding with {reply}")

            conn.sendall(serialize(reply))
        except:
            break
    conn.close()


connection_id = 0
while True:
    print(f"listening on {port}")
    conn, addr = sock.accept()
    print(f"connected to {addr}, assigned ID {connection_id}")
    start_new_thread(threaded_client, (conn, connection_id))
    connection_id += 1
