#!/usr/bin/python3
from time import sleep
from pickle import dumps as serialize
from pickle import loads as deserialize
# n = 0
# while True:
#     print(f"hello #{n}")
#     sleep(1)
#     n+=1

worldstate = []

import socket
from _thread import start_new_thread
import sys

# server = "47.155.218.95"
server = ""
port = 1111
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("attempting bind:")
try:
    s.bind((server, port))
    print("socket bound successfully")
except socket.error as message:
    print("Bind failed. Error Code : " + str(message))
    sys.exit()


s.listen()


def threaded_client(conn):
    # this is sent upon connection
    conn.send(serialize(worldstate))
    while True:
        
        try:
            data = deserialize(conn.recv(2048))
            if not data:
                print("disconnected")
                break
            else: # here is everything is good
                print(f"received: {data}")
                reply = "ok"

            conn.sendall(serialize(reply))
        except:
            break
    conn.close()


while True:
    print(f"listening on {port}")
    conn, addr = s.accept()
    print(f"connected to {addr}")
    start_new_thread(threaded_client, (conn,))
