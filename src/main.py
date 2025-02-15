from os import times_result
import socket
import time
import pygame
import sys
import asyncio
import msgpack
import threading
from server import worldstate
from spatial import SpatialVector, ball, SpatialObject, build_ball
from network import Frenship

from pygame.time import Clock


from time import time as epoch
from time import sleep


frenship = Frenship()
# print(worldstate)
# quit()
pygame.display.set_caption("CLIENT")


# Initialize Pygame
pygame.init()
update_interval = 1000  # ms
# Set up display
width, height = 1500, 1000
# screen = pygame.display.set_mode((width, height))

screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
surface = pygame.Surface((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
print(pygame.display.get_driver())
print(pygame.display.get_surface())


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


sleep_ms = lambda x: sleep(x / 1000)
stamp = epoch()
# Main loop

awaiting = None


clock = Clock()
ball.pos.x = width // 2
ball.pos.y = height // 2

while frenship.worldstate == {}:
    # print("not present")
    print(f"main's worldstate: {worldstate}")
    sleep_ms(1000)

print("starting gameloop")

while True:
    # clock.tick(20)
    start = epoch()
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
    screen.fill(BLACK)
    ball.push(right, left, up, down)

    center = (
        ball.pos.x,
        ball.pos.y,
    )
    radius = 50
    pygame.draw.circle(screen, (255, 56, 0), center, radius)
    # Draw a ciK_LEFTrcle
    # if worldstate:
    #     print(worldstate)

    temporal_adjustment = 50 / 1000  # run remote on 50ms lag
    for ID in frenship.worldstate["players"].keys():
        # if ID == frenship.connection_id:
        #     continue
        snapshots = frenship.worldstate["players"][ID]["player_state"]["buffer"]

        # timestamps = sorted(snapshots.keys())
        last_timestamp = snapshots[0]["timestamp"]
        last = snapshots[0]["state"]

        oldest_timestamp = snapshots[-1]["timestamp"]
        lastball = build_ball(last)
        # print(type(worldstate[ID]))

        # timestamp = player["timestamp"]

        # last_age = epoch() - last_timestamp - temporal_adjustment
        # if last_age<0:
        moved = (
            lastball.pos.x + (lastball.vel.x * last_age),
            lastball.pos.y + (lastball.vel.y * last_age),
        )
        
        radius = 30 * 0.9**last_age
        pygame.draw.circle(screen, (255, 187, 0), moved, radius)

        if (epoch() - stamp) * 1000 > update_interval:
            stamp = epoch()
            print(f"last snapshot age against rewind:  {last_age * 1000:.0f}ms")
            # print(snapshots)
            # print("\n\n\n\n")

        # accelerated = (
        #     myball.pos.x + (age * (myball.vel.x + (age * myball.acc.x))),
        #     myball.pos.y + (age * (myball.vel.y + (age * myball.acc.y))),
        # )
        # radius = 40 * 0.9**age

        # pygame.draw.circle(screen, (255, 100, 0), accelerated, radius)

        # moved = (
        #     myball.pos.x + (myball.vel.x * age),
        #     myball.pos.y + (myball.vel.y * age),
        # )
        # radius = 30 * 0.9**age
        # pygame.draw.circle(screen, (255, 187, 0), moved, radius)

        # static = (
        #     myball.pos.x,
        #     myball.pos.y,
        # )
        # radius = 25 * 0.5**age
        # pygame.draw.circle(screen, (221, 246, 255), static, radius)

    # Update the display
    pygame.display.flip()
    end = epoch()
    # asyncio.run(update())
