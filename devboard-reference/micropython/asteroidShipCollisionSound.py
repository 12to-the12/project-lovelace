# Copyright (c) 2025 by Alfred Morgan <alfred@54.org>
# Copyright (c) 2025 by Mitchell Tucker
# License https://opensource.org/license/isc-license-txt
# Version 0.2.1

from utime import sleep
from urandom import randint, uniform
from lcd import *
import _thread
from math import atan2, degrees, pi, cos, sin

background = (0, 0, 0)

sprites = []  # all sprites
stars = []
beeperLock = _thread.allocate_lock()

# Sound
volume = 15000


class Sprite:
    name = ""
    health = 0
    maxHealth = 0
    damage = 10
    x = 0.0
    y = 0.0
    vx = 0.0
    vy = 0.0
    w = 1
    h = 1
    color = (0, 0, 0)

    def __init__(self, name="", health=100, color=None):
        self.name = name
        self.health = health
        self.maxHealth = health
        self.color = color or (randint(0, 255), randint(0, 255), randint(0, 255))
        sprites.append(self)

    def move(self):
        self.erase()
        self.x += self.vx
        self.y += self.vy
        if self.x >= width - 1:
            self.x -= width
        elif self.x < 0:
            self.x += width
        if self.y >= height - 1:
            self.y -= height
        elif self.y < 0:
            self.y += height
        self.draw()

    def draw(self):
        lcd_set_color(*self.color)
        lcd_fill(int(self.x), int(self.y), self.w, self.h)

    def erase(self):
        lcd_set_color(*background)
        lcd_fill(int(self.x), int(self.y), self.w, self.h)

    def takeDamage(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            self.destroy()

    def destroy(self):
        self.erase()
        sprites.remove(self)


class Ship(Sprite):
    health = 100
    w = 12
    h = 12
    bulletCount = 0
    tag = 1 << 0
    angle = 0  # Angle in degrees

    def fire(self):
        if self.bulletCount >= 10:
            return
        self.bulletCount += 1
        bullet = Bullet(f"Bullet {self.bulletCount}", color=(255, 255, 255))
        v = sqrt(self.vx**2 + self.vy**2)
        bullet.x = self.x
        bullet.y = self.y
        bullet.vx = self.vx / v * 5 + self.vx
        bullet.vy = self.vy / v * 5 + self.vy
        fire_beep(500, 0.01)

    def draw(self):
        # If there's no velocity, use a default angle (e.g., 0 degrees).
        # Otherwise, compute the orientation from vx, vy.
        if self.vx == 0 and self.vy == 0:
            # Keep the last angle OR set a default angle
            # self.angle = 0
            pass
        else:
            self.angle = atan2(self.vy, self.vx)

        # Set draw color to the ship's color
        lcd_set_color(*self.color)

        # Calculate the center of the ship
        center_x = int(self.x) + (self.w // 2)
        center_y = int(self.y) + (self.h // 2)

        size = self.w // 2  # Half-width used to form the triangle

        # Calculate the 3 corner points of the triangle
        tip_x = center_x + int(size * cos(self.angle))
        tip_y = center_y + int(size * sin(self.angle))
        left_x = center_x + int(size * cos(self.angle + 2 * pi / 3))
        left_y = center_y + int(size * sin(self.angle + 2 * pi / 3))
        right_x = center_x + int(size * cos(self.angle - 2 * pi / 3))
        right_y = center_y + int(size * sin(self.angle - 2 * pi / 3))

        lcd_set_color(*self.color)
        lcd_draw_h_line(int(self.x), int(self.y), int(self.x) + self.w - 1)
        lcd_draw_h_line(int(self.x), int(self.y) + self.h - 1, int(self.x) + self.w - 1)
        midX = int(self.x) + self.w // 2 - 1
        if midX < width:
            lcd_draw_v_line(midX, int(self.y), int(self.y) + self.h - 1)

        # Draw the triangle
        lcd_draw_line(tip_x, tip_y, left_x, left_y)
        lcd_draw_line(left_x, left_y, right_x, right_y)
        lcd_draw_line(right_x, right_y, tip_x, tip_y)


class Bullet(Sprite):
    w = 3
    h = 3
    tag = 1 << 1

    def move(self):
        super().move()
        self.takeDamage(3)

    def destroy(self):
        ship.bulletCount -= 1
        super().destroy()

    def draw(self):
        lcd_set_color(*self.color)
        lcd_fill(int(self.x), int(self.y), self.w, self.h)


class Asteroid(Sprite):
    health = 100
    damage = 100
    w = 10
    h = 7
    tag = 1 << 2
    angle = 0
    spin_speed = 2  # degrees per frame (if you want it spinning)

    def takeDamage(self, dmg):
        super().takeDamage(dmg)

        healthPercent = self.health / self.maxHealth
        redDark = 255 - 180
        total = (healthPercent * redDark) + 180

        self.color = (int(total), 0, 0)


class Star:
    x = 0
    y = 0
    c = 0


def play_tone(frequency, duration):
    beeperLock.acquire()
    """
    Play a tone on the beeper pin.
    :param frequency: Frequency of the tone in Hz.
    :param duration: Duration of the tone in seconds.
    :param volume: Duty cycle (0-1023), higher is louder.
    """
    lcd_start_tone(frequency, volume)
    sleep(duration)  # Play for the given duration
    lcd_stop_tone()
    beeperLock.release()


def fire_beep(frequency, duration):
    if beeperLock.acquire(False):  # Try to acquire the beeperLock without blocking
        try:
            _thread.start_new_thread(
                play_tone, (frequency, duration)
            )  # Start the thread
        finally:
            beeperLock.release()  # Ensure the beeperLock is released after the thread finishes


def crash_beep(frequency):
    if beeperLock.acquire(False):  # Try to acquire the beeperLock without blocking
        try:
            _thread.start_new_thread(play_tone, (frequency, 0.05))  # Start the thread
        finally:
            beeperLock.release()  # Ensure the beeperLock is released after the thread finishes


def threaded_beep():
    if beeperLock.acquire(False):  # Try to acquire the beeperLock without blocking
        try:
            _thread.start_new_thread(play_tone, (6400, 0.05))  # Start the thread
        finally:
            beeperLock.release()  # Ensure the beeperLock is released after the thread finishes


def is_collision(x1_1, y1_1, x2_1, y2_1, x1_2, y1_2, x2_2, y2_2):
    return x1_1 < x2_2 and x2_1 > x1_2 and y1_1 < y2_2 and y2_1 > y1_2


def checkColl():
    for i in reversed(
        range(len(sprites))
    ):  # Iterate in reverse to safely remove elements
        object_check = sprites[i]
        for v in range(0, i):  # Check against all previous sprites
            object_check_with = sprites[v]

            value = object_check.tag | object_check_with.tag

            # Check for Asteroid and Bullet types
            if value == (Asteroid.tag | Bullet.tag):
                # Calculate bounding boxes
                asteroid_x1, asteroid_y1 = object_check.x, object_check.y
                asteroid_x2, asteroid_y2 = (
                    object_check.x + object_check.w,
                    object_check.y + object_check.h,
                )

                bullet_x1, bullet_y1 = object_check_with.x, object_check_with.y
                bullet_x2, bullet_y2 = (
                    object_check_with.x + object_check_with.w,
                    object_check_with.y + object_check_with.h,
                )

                # Check for collision
                if is_collision(
                    bullet_x1,
                    bullet_y1,
                    bullet_x2,
                    bullet_y2,
                    asteroid_x1,
                    asteroid_y1,
                    asteroid_x2,
                    asteroid_y2,
                ):
                    object_check.takeDamage(object_check_with.damage)  # Damage object 1
                    object_check_with.takeDamage(object_check.damage)  # Damage object 2

                    threaded_beep()
                    return
            if value == (Ship.tag | Asteroid.tag):
                # Calculate bounding boxes
                asteroid_x1, asteroid_y1 = object_check.x, object_check.y
                asteroid_x2, asteroid_y2 = (
                    object_check.x + object_check.w,
                    object_check.y + object_check.h,
                )

                ship_x1, ship_y1 = object_check_with.x, object_check_with.y
                ship_x2, ship_y2 = (
                    object_check_with.x + object_check_with.w,
                    object_check_with.y + object_check_with.h,
                )

                if is_collision(
                    asteroid_x1,
                    asteroid_y1,
                    asteroid_x2,
                    asteroid_y2,
                    ship_x1,
                    ship_y1,
                    ship_x2,
                    ship_y2,
                ):
                    object_check.takeDamage(object_check_with.damage)  # Damage object 1
                    object_check_with.takeDamage(object_check.damage)  # Damage object 2
                    crash_beep(180)
                    sleep(0.3)
                    crash_beep(160)
                    sleep(0.3)
                    crash_beep(140)
                    return


def drawStars():
    for star in stars:
        lcd_set_color(star.c, star.c, star.c)
        lcd_draw_pixel(star.x, star.y)


def play():
    spawnShip()
    ship.x = width / 2
    ship.y = height / 2
    speed = 10
    while True:
        drawStars()
        ship.vx = (joy_x.read_u16() / 2**16 - 0.5) * speed
        ship.vy = -(joy_y.read_u16() / 2**16 - 0.5) * speed
        for sprite in sprites:
            sprite.move()
        if not button_a.value():
            break
        if not button_b.value():
            ship.fire()

        checkColl()
        # sleep(1/60)


def clear():
    lcd_clear()
    sprites.clear()
    stars.clear()


def bgProcess():
    while True:
        pass


def spawnShip():
    global ship
    ship = Ship("Player 1", color=(0, 128, 0))


def spawnAsteroid():
    asteroid = Asteroid()
    asteroid.x = uniform(0, width - 1)
    asteroid.y = uniform(0, height - 1)
    asteroid.vx = uniform(-4, 4)
    asteroid.vy = uniform(-4, 4)
    size = randint(3, 10)
    asteroid.w = randint(7, 20)
    asteroid.h = randint(7, 20)
    asteroid.health = int(asteroid.w * asteroid.h)
    asteroid.maxHealth = asteroid.health
    asteroid.color = (255, 0, 0)


def spawnStar():
    s = Star()
    s.x = randint(0, width - 1)
    s.y = randint(0, height - 1)
    s.c = randint(10, 200)
    stars.append(s)


def wave1():
    clear()
    for _ in range(5):
        spawnAsteroid()
    for _ in range(25):
        spawnStar()
    play()


def main():
    lcd_init()

    while True:
        wave1()
        sleep(0.1)


if __name__ == "__main__":
    main()
