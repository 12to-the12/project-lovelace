from time import sleep, sleep_ms, sleep_us
from time import time as epoch
from time import time_ns as epoch_ns
import sys

from sprite import Sprite
import network
from netcode import Connection
from config import config
from lcd import *
from time import sleep
from player_input import readinput
from sprite import player
from timing import Pulse
from world import world


def readout(things):
    global readouts
    if readouts.read():
        print(things)


def draw_circles():
    global clock_stamp_ns, config
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
        lastball = build_sprite(last)
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
                myball = build_sprite(snapshots[before_candidate])
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

        # readout(last_timestamp, oldest_timestamp)

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


def clock_wait():
    global clock_stamp_ns
    now = epoch_ns()
    elapsed_ns = now - clock_stamp_ns

    elapsed = elapsed_ns / 1e9
    target = 1 / config.fps  # seconds per frame
    diff = target - elapsed  # time needed to sleep in seconds
    # readout(f"elapsed: {elapsed*1_000:5.2f}ms")
    
    # readout(
    #     f"elapsed: {elapsed*1_000:5.2f}ms,target: {target*1_000:5.2f}ms, sleeping {int(diff * 1e3)} ms"
    # )

    # readout(f"fps: {1 / elapsed}")

    if elapsed < target:
        # print("sleeping...")
        sleep_us(int(diff * 1e6))

    clock_stamp_ns = epoch_ns()


def do_physics(player, direction):
    player.push(direction)


def draw_sprites():
    global erase
    lcd_set_color(randint(0, 255), randint(100, 255), randint(0, 100))
    for _ in erase:
        erase_rect(*erase.pop(), 10, 10)
    for sprite in world.sprites.values():

        draw_rect(*sprite.screen_coords(), 10, 10)

    erase.insert(0, player.screen_coords())


# @timefunct
def game_loop():
    global erase, connection
    direction, button1, button2 = readinput()

    # network io
    # control input
    # draw sprites
    # movement and collisions
    # update audio

    do_physics(player, direction)
    draw_sprites()

    connection.loop_over_io()

    clock_wait()


def game_init():
    global erase, clock_stamp_ns, readout_timer_ns, connection, readouts
    clock_stamp_ns = epoch_ns()
    readouts = Pulse()
    erase = []

    lcd_init()
    lcd_clear()

    print("starting network operations")
    connection = Connection()
    # world = connection.world

    while True:

        game_loop()
