from os import times_result
import socket
import pygame
import sys
import asyncio
import msgpack
import threading
from network import Frenship

network = Frenship()

from time import time as epoch
from time import sleep


while True:
    # print("polling")
    packet = network.tcp_scan()
    print(f"received: {packet}")
    # MESSAGE = "henlo"
    # print(f"sending... <{MESSAGE}>")
    # # network.udp_send(MESSAGE)


quit()

pygame.display.set_caption("CLIENT")


class spatial_vector:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z


class spatial_object:
    def __init__(
        self, pos=spatial_vector(), vel=spatial_vector(), acc=spatial_vector()
    ):
        self.pos = pos
        self.vel = vel
        self.acc = acc

        self.last_updated = epoch()

    def apply(self):
        timestamp = epoch()
        elapsed = timestamp - self.last_updated
        self.last_updated = timestamp

        self.vel.x += self.acc.x * elapsed
        self.vel.y += self.acc.y * elapsed
        self.vel.z += self.acc.z * elapsed

        self.pos.x += self.vel.x * elapsed
        self.pos.y += self.vel.y * elapsed
        self.pos.z += self.vel.z * elapsed

        self.pos.x

        self.vel.x *= 0.9999**elapsed
        self.vel.y *= 0.9999**elapsed
        self.vel.z *= 0.9999**elapsed


# Initialize Pygame
pygame.init()
update_interval = 20  # ms
# Set up display
width, height = 1500, 1000
# screen = pygame.display.set_mode((width, height))

screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
surface = pygame.Surface((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
print(pygame.display.get_driver())
print(pygame.display.get_surface())

pygame.display.set_caption("Draw a Circle")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
x = 0
y = 0
left = False
right = False
up = False
down = False

ball = spatial_object()
ball.pos.x = 5
ball.pos.y = 5


sleep_ms = lambda x: sleep(x / 1000)
stamp = epoch()
# Main loop

awaiting = None


# async def fetch_worldstate():
#     global worldstate
#     worldstate = network.tcp_send((ball.pos.x, ball.pos.y, ball.pos.z))


# async def update():

#     # global stamp, awaiting
#     # if (epoch() - stamp) * 1000 > update_interval:
#     #     if awaiting:
#     #         await awaiting
#     #     awaiting = asyncio.create_task(fetch_worldstate())
#     #     # await awaiting
#     #     stamp = epoch()
#     #     if worldstate:
#     #         # print(worldstate)
#     #         pass
#     #     else:
#     #         print("error connecting")
#     #     # print(worldstate)

worldstate = {}


def read_world():
    global worldstate
    while True:
        worldstate = network.tcp_scan()
        # print(f"{worldstate=}")
        # print(worldstate)


def send_position():
    while True:
        packet = {
            "type": "player_state",
            "id": 1,
            "player_state": {
                "position": (ball.pos.x, ball.pos.y, ball.pos.z),
                "velocity": (ball.vel.x, ball.vel.y, ball.vel.z),
                "acceleration": (ball.acc.x, ball.acc.y, ball.acc.z),
            },
            "timestamp": epoch(),
        }
        # print(packet)
        network.tcp_send(packet)
        sleep_ms(10)


acc = 1e3


from pygame.time import Clock

clock = Clock()
ball.pos.x = width // 2
ball.pos.y = height // 2
# asyncio.run(fetch_worldstate())

# packet = {
#     "type": "connection_request",
#     "timestamp": epoch(),
# }


# network.udp_send(packet)


# while True:
#     print("waiting for id assignment...")
#     packet = network.udp_scan()
#     print(packet)
#     if packet.get("type") == "id_assignment":
#         ID = packet["id"]
#         break


send_position_thread = threading.Thread(target=send_position)
send_position_thread.start()


read_worldstate_thread = threading.Thread(target=read_world)
read_worldstate_thread.start()


while True:
    clock.tick(100)
    start = epoch()
    # asyncio.run(update())
    # ball.vel.x = 100
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                left = True
            if event.key == pygame.K_RIGHT:
                right = True
            if event.key == pygame.K_UP:
                up = True
            if event.key == pygame.K_DOWN:
                down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left = False
            if event.key == pygame.K_RIGHT:
                right = False
            if event.key == pygame.K_UP:
                up = False
            if event.key == pygame.K_DOWN:
                down = False
    # Fill the background
    screen.fill(BLACK)
    # if right:
    #     ball.acc.x = 1
    # if left:
    #     ball.acc.x = 1
    # if up:
    #     ball.acc.y = 1
    # if down:
    #     ball.acc.y = 1
    if right:
        ball.acc.x = acc
    if left:
        ball.acc.x = -acc
    if right and left:
        ball.acc.x = 0
    if (not right) and (not left):
        ball.acc.x = 0
    if down:
        ball.acc.y = acc
    if up:
        ball.acc.y = -acc
    if down and up:
        ball.acc.y = 0
    if (not up) and (not down):
        ball.acc.y = 0
    ball.apply()

    center = (
        ball.pos.x,
        ball.pos.y,
        # width // 2 + x / 1000,
        # height // 2 + y / 1000,
    )  # Center of the screen
    radius = 50
    pygame.draw.circle(screen, (255, 56, 0), center, radius)
    # Draw a ciK_LEFTrcle
    # if worldstate:
    #     print(worldstate)
    for ID in worldstate.keys():
        # print(type(worldstate[ID]))
        x, y, z = worldstate[ID]["player_state"]["position"]
        vx, vy, vz = worldstate[ID]["player_state"]["velocity"]
        timestamp = worldstate[ID]["timestamp"]
        age = epoch() - timestamp
        # print(f"{age*1000:.0f}ms")
        # print(f"{vx=},{vy=}")
        # print((x,y,z))

        predicted = (
            x + (vx * age),
            y + (vy * age),
        )
        # print(f"{vx=}")
        # print(f"{ball.vel.x=}")
        radius = 50 * 0.9**age
        pygame.draw.circle(screen, (255, 187, 0), predicted, radius)

        center = (
            x,
            y,
        )
        radius = 25 * 0.5**age
        pygame.draw.circle(screen, (221, 246, 255), center, radius)

    # Update the display
    pygame.display.flip()
    end = epoch()
    # asyncio.run(update())
    if (epoch() - stamp) * 1000 > update_interval:
        elapsed = end - start
        # print(f"{1 / elapsed:6.0f} fps")
