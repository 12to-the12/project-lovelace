from os import times_result
import socket
import time
import pygame
import sys
import asyncio
import msgpack
import threading
from server import worldstate
from spatial import SpatialVector, ball, SpatialObject, build_ball, mix
from network import Frenship
from timing import Pulse

from pygame.time import Clock


from time import time as epoch
from time import sleep


frenship = Frenship()
# print(worldstate)
# quit()
pygame.display.set_caption(str(frenship.connection_id))


# Initialize Pygame
pygame.init()
readout_interval = 1000  # ms
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
# ball.pos.x = width // 2
# ball.pos.y = height // 2

while frenship.worldstate == {}:
    # print("not present")
    print(f"main's worldstate: {frenship.worldstate}")
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

    temporal_adjustment = 50 / 1000  # number of seconds to lag the remote worldstate
    for ID in frenship.worldstate["players"].keys():
        if ID == frenship.connection_id:
            continue

        buffer = frenship.worldstate["players"][ID]["player_state"]["buffer"]
        if buffer == []:
            continue
        snapshots = frenship.worldstate["players"][ID]["player_state"]["snapshots"]

        # timestamps = sorted(snapshots.keys())
        last_timestamp = buffer[0]
        last = snapshots[buffer[0]]

        oldest_timestamp = buffer[-1]
        lastball = build_ball(last)
        # print(type(worldstate[ID]))

        # timestamp = player["timestamp"]
        real_last_age = epoch() - last_timestamp
        last_age = epoch() - last_timestamp - temporal_adjustment
        oldest_age = epoch() - oldest_timestamp - temporal_adjustment

        # this is interpolation
        # we need the one before and the one after
        # print(buffer)
        # print(f"last age: {last_age * 1000:.0f}ms")
        # print(f"oldest age: {oldest_age * 1000:.0f}ms")
        if last_age < 0 and oldest_age > 0:
            target_time = epoch() - temporal_adjustment
            # print(f"{target_time=}")
            after_candidate = 1e20
            before_candidate = 0
            for timestamp in buffer:
                # if before target and right before
                if timestamp < target_time:
                    if timestamp > before_candidate:
                        # print(f"the timestamp {timestamp} might be right before")
                        before_candidate = timestamp

                # if after target and right after

                if timestamp > target_time:
                    if timestamp < after_candidate:
                        # print(f"the timestamp {timestamp} might be right after")
                        after_candidate = timestamp
            # print(before_candidate)
            if before_candidate == 0:
                print("no before candidate found")
                print("this is a race condition")
                continue
            if after_candidate == 1e20:
                print("no after candidate found")
                print("this is a race condition")
                continue
            before_delta = target_time - before_candidate
            after_delta = after_candidate - target_time
            span = after_delta + before_delta
            if span != 0:
                before_weight = after_delta / span
                after_weight = before_delta / span
                before = snapshots[before_candidate]
                after = snapshots[after_candidate]
                mixedball = mix(before, before_weight, after, after_weight)
                moved = (mixedball.pos.x, mixedball.pos.y)
            else:
                myball = build_ball(snapshots[before_candidate])
                moved = (myball.pos.x, myball.pos.y)
            radius = 40 * 0.6**last_age
            pygame.draw.circle(screen, (255, 126, 0), moved, radius)

        # future extrapolation
        # oldest age implied to be bigger than last age
        # temporal adjustment not enough to compensate for latency
        elif last_age > 0:
            # lastball = build_ball(snapshots[last_age])
            moved = (
                lastball.pos.x + (lastball.vel.x * last_age),
                lastball.pos.y + (lastball.vel.y * last_age),
            )

            radius = 40 * 0.6**last_age
            pygame.draw.circle(screen, (200, 200, 255), moved, radius)

            # relic = (lastball.pos.x, lastball.pos.y)
            # radius = 35 * 0.6**last_age
            # pygame.draw.circle(screen, (180, 180, 240), relic, radius)
        # low latency, not enough snapshots, not really a problem?
        # last age implied to be smaller than oldest age
        elif oldest_age < 0:
            # print("the oldest snapshot on record is more recent than our target time ")
            pass

        else:
            raise (Exception("unreachable state"))

        if (epoch() - stamp) * 1000 > readout_interval:
            stamp = epoch()
            # print(f"last age: {last_age * 1000:.0f}ms")
            # print(f"oldest age: {oldest_age * 1000:.0f}ms")
            print(f"worldstate age: {(epoch() - last_timestamp) * 1000:.0f}ms")
            print(f"oldest worldstate age: {(epoch() - oldest_timestamp) * 1000:.0f}ms")
            # print("\n\n\n\n")

        # accelerated = (
        #     myball.pos.x + (age * (myball.vel.x + (age * myball.acc.x))),
        #     myball.pos.y + (age * (myball.vel.y + (age * myball.acc.y))),
        # )
        # radius = 40 * 0.9**age

        # pygame.draw.circle(screen, (255, 100, 0), accelerated, radius)

        moved = (
            lastball.pos.x + (lastball.vel.x * real_last_age),
            lastball.pos.y + (lastball.vel.y * real_last_age),
        )
        radius = 30 * 0.5**real_last_age
        # pygame.draw.circle(screen, (255, 209, 63), moved, radius)

        static = (
            lastball.pos.x,
            lastball.pos.y,
        )
        radius = 20 * 0.3**real_last_age
        # pygame.draw.circle(screen, (245, 243, 255), static, radius)

    # Update the display
    pygame.display.flip()
    end = epoch()
    # asyncio.run(update())
