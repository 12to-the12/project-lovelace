#!/usr/bin/python3
from time import sleep
from pickle import dumps as serialize
from pickle import loads as deserialize
# n = 0
# while True:
#     print(f"hello #{n}")
#     sleep(1)
#     n+=1


# an entry per connection
# worldstate = ["deadbeef"]*10
worldstate = []

import socket
from _thread import start_new_thread
import sys

# server = "47.155.218.95"
server = ""
port = 1111
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("attempting bind:")
try:
    s.bind((server, port))
    print("socket bound successfully")
except socket.error as message:
    print("Bind failed. Error Code : " + str(message))
    sys.exit()


s.listen()


def threaded_client(conn,connection_id):
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
            else: # here is everything is good
                print(f"received and verified: {data} for ID:{connection_id}")
                print("updating worldstate...")
                try: worldstate[connection_id] = data
                except: worldstate.append(data)
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
    conn, addr = s.accept()
    print(f"connected to {addr}, assigned ID {connection_id}")
    start_new_thread(threaded_client, (conn,connection_id))
    connection_id+=1
