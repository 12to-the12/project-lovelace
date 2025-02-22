# from profile import timefunct, profile
from time import sleep,sleep_us,sleep_ms
from time import time as epoch
from time import time_ns as epoch_ns


import sys
import socket
import time
import sys
import asyncio

# # import msgpack
# # import threading
from spatial import ball, build_ball, mix
import network
from netcode import Connection

# print(machine.unique_id())
# from time import time as epoch
# from time import sleep
# import gc
from config import config
from lcd import *
from random import randint
from time import sleep
from profile import profile
import machine

from joystick import joystick


class InputState:
    def __init__(self):
        self.right = False
        self.left = False
        self.up = False
        self.down = False


# print(machine.freq())
# cpu_frequency = machine.freq()


def readout(things):
    global stamp_ns
    if (epoch_ns() - stamp_ns)/1e6 > config.readout_interval_ms:
        stamp_ns = epoch_ns()
        print(things)
        # for thing in things:print(thing)
        # print(f"last age: {last_age * 1000:.0f}ms")
        # print(f"oldest age: {oldest_age * 1000:.0f}ms")
        # print(f"worldstate age: {(epoch() - last_timestamp) * 1000:.0f}ms")
        # print(f"oldest worldstate age: {(epoch() - oldest_timestamp) * 1000:.0f}ms")
        # print("\n\n\n\n")


def draw_circles():
    global stamp_ns, config
    for ID in frenship.worldstate["players"].keys():
        if ID == frenship.connection_id and not config.draw_self:
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
        last_age = epoch() - last_timestamp - config.temporal_adjustment
        oldest_age = epoch() - oldest_timestamp - config.temporal_adjustment

        # this is interpolation
        # we need the one before and the one after
        if last_age < 0 and oldest_age > 0:
            target_time = epoch() - config.temporal_adjustment
            # print(f"{target_time=}")
            after_candidate = 1e20
            before_candidate = 0
            for timestamp in buffer:
                # if before target and right before
                if timestamp < target_time:
                    if timestamp > before_candidate:
                        before_candidate = timestamp

                # if after target and right after

                if timestamp > target_time:
                    if timestamp < after_candidate:
                        after_candidate = timestamp
            if before_candidate == 0:
                print("no before candidate found")
                print("this is likely a race condition")
                continue
            if after_candidate == 1e20:
                print("no after candidate found")
                print("this is likely a race condition")
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
            if config.desktop_mode:
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
            if config.draw_time_dilated:
                if config.desktop_mode:
                    pygame.draw.circle(screen, (200, 200, 255), moved, radius)
        # low latency, not enough snapshots, not really a problem?
        # last age implied to be smaller than oldest age
        elif oldest_age < 0:
            # print("the oldest snapshot on record is more recent than our target time ")
            pass

        else:
            raise (Exception("unreachable state"))

        readout(last_timestamp, oldest_timestamp)

        moved = (
            lastball.pos.x + (lastball.vel.x * real_last_age),
            lastball.pos.y + (lastball.vel.y * real_last_age),
        )
        radius = 30 * 0.5**real_last_age
        if config.draw_interpolated:
            if config.desktop_mode:
                pygame.draw.circle(screen, (255, 209, 63), moved, radius)

        static = (
            lastball.pos.x,
            lastball.pos.y,
        )
        radius = 20 * 0.3**real_last_age
        if config.draw_last_pos:
            if config.desktop_mode:
                pygame.draw.circle(screen, (245, 243, 255), static, radius)


def connect_to_wifi():
    from secrets import ssid, password

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print("waiting for connection...")
        sleep(1)
    print(wlan.isconnected())
    print(wlan)


# @timefunct
def game_loop(inputstate):
    global erase
    # network io
    # control input
    # draw sprites
    # movement and collisions
    # update audio

    # clock.tick(20)
    # clock_wait(100000)
    start = epoch_ns()
    if config.desktop_mode:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    inputstate.left = True
                if event.key == pygame.K_RIGHT:
                    inputstate.right = True
                if event.key == pygame.K_UP:
                    inputstate.up = True
                if event.key == pygame.K_DOWN:
                    inputstate.down = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    inputstate.left = False
                if event.key == pygame.K_RIGHT:
                    inputstate.right = False
                if event.key == pygame.K_UP:
                    inputstate.up = False
                if event.key == pygame.K_DOWN:
                    inputstate.down = False
        screen.fill(BLACK)
    # ball.push_binary(inputstate.right, inputstate.left, inputstate.up, inputstate.down)
    
    lcd_set_color(0, 0, 0)
    for coords in erase:
        lcd_fill(*erase.pop(),10,10)

    ball.push(inputstate)

    coords = (
        int(ball.pos.x),
        int(ball.pos.y),
    )
    # print(">")
    # print(inputstate)
    # print(f"{ball.acc.x} {ball.acc.y}")
    # print(f"{ball.vel.x} {ball.vel.y}")
    # print(f"{ball.pos.x} {ball.pos.y}")
    # print(coords)
    
    

    if config.desktop_mode:
        radius = 50
        pygame.draw.circle(screen, (255, 56, 0), center, radius)
    else:
        lcd_set_color(255, 0, 255)
        lcd_fill(*coords,10,10)
        erase.insert(0,coords)
    # draw_circles()
    # Update the display
    if config.desktop_mode:
        pygame.display.flip()
    end = epoch_ns()
    elapsed_ns = end-start
    elapsed = elapsed_ns/1e9
    target = 1/config.fps
    diff = target-elapsed
    if elapsed < target:

        sleep_us(int(diff*1e6))
        readout(f"fps: {1/elapsed}")



def game_init():
    global erase,stamp_ns
    stamp_ns=epoch_ns()
    erase = []

    connect_to_wifi()
    lcd_init()
    lcd_clear(0, 0, 0)

    print("starting network operations")
    connection = Connection()

    # if config.desktop_mode:
    #     import pygame
    #     from pygame.time import Clock

    #     pygame.display.set_caption(str(frenship.connection_id))
    #     pygame.init()

    #     width, height = 1500, 1000

    #     screen = pygame.display.set_mode(
    #         (width, height), pygame.HWSURFACE | pygame.DOUBLEBUF
    #     )
    #     surface = pygame.Surface((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)

    #     clock = Clock()

    # BLACK = (0, 0, 0)
    # WHITE = (255, 255, 255)
    # RED = (255, 0, 0)
    # GREEN = (0, 255, 0)
    # BLUE = (0, 0, 255)
    # x = 0
    # y = 0

    # sleep_ms = lambda x: sleep(x / 1000)
    # stamp = epoch()

    # awaiting = None

    # while frenship.worldstate == {}:
    #     print(f"main's worldstate: {frenship.worldstate}")
    #     sleep_ms(1000)

    # print("starting gameloop")

    # # stampb = epoch()
    while True:
        center = (
        ball.pos.x,
        ball.pos.y,
        )
        game_loop(joystick.read())
