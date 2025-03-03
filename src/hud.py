from math import sin
from lcd import *


class View:
    x = 0
    y = 0
    height = 0
    width = 0
    z = 0
    name = ""
    color = (2, 255, 255)

    def __init__(self, name="", color=None):
        self.name = name

    def update(self):
        return

    def draw(self):
        return

    def checkOverLap(self, sprite):
        return sprite.x > self.x and sprite.y > self.height


class Menu(View):
    def __init__(self, name="", color=None):
        self.width = width  # global var width is in lcd ~480
        self.height = 20
        self.draw()

    def update(self, update_health=-1, update_sheild=-1, update_lifes=-1):
        if update_health != -1:
            self.health_bar.update(fill_precent=update_health)
        if update_sheild != -1:
            self.sheild_bar.update(fill_precent=update_sheild)
        if update_lifes != -1:
            self.heart_view.update_lifes(update_lifes)
        return

    def update_bullets(self):
        # self.ammo_view.fire_counter()
        return

    def checkOverLap(self, sprite):
        return super().checkOverLap(sprite)

    def draw(self):
        lcd_set_color(*self.color)

        lcd_draw_line(0, 0, self.height, self.height)
        lcd_draw_line(self.height, self.height, width, self.height)

        padding = 10
        # self.ammo_view = AmmoView()
        # Set poition of both bars and
        self.health_bar = BarView(
            x_pos=width, y_pos=5, width=100, height=10, color=(55, 255, 55)
        )
        # bar_offset = width
        self.sheild_bar = BarView(
            x_pos=(width - 100) - padding,
            y_pos=5,
            width=100,
            height=10,
            color=(0, 0, 255),
        )
        lcd_set_color(*(0, 0, 0))
        self.heart_view = HeartView(x_pos=width, y_pos=5, width=100, height=10)


class AmmoView(View):
    def __init__(self, name="", color=None):
        self.width = width  # global var width is in lcd ~480
        self.bottom_bar_height = 20
        self.color = (255, 255, 255)
        self.bullet_counter = 10
        self.draw()

    def refill_ammo(self, amount):
        self.bullet_counter = amount

    def fire_counter(self):
        if self.bullet_counter != 0:
            self.bullet_counter -= 1
            self.ammo_counter()
        else:
            lcd_rgb_led(25, 0, 0)

    def ammo_counter(self):
        lcd_set_color(*(0, 0, 0))
        lcd_fill(width - 30, height - 30, 50, 10)
        lcd_draw_text(width - 30, height - 30, str(self.bullet_counter))

    def draw(self):
        self.ammo_counter()
        lcd_set_color(*self.color)
        lcd_draw_line(width - 81, height, width - 1, height - 80)


class BarView(View):
    def __init__(
        self, name="", x_pos=10, y_pos=5, width=100, height=10, color=(255, 255, 255)
    ):
        self.width = width
        self.height = height
        self.x = x_pos
        self.y = y_pos
        self.color = color
        self.fill_size = 100  # in precentage
        self.draw()

    def clear(self):
        lcd_set_color(*(0, 0, 0))
        lcd_fill((self.x - self.width) - 9, self.y + 1, self.width - 1, self.height - 1)

    def update(self, fill_precent):
        self.fill_size = fill_precent
        self.clear()
        self.draw()

    def draw(self):
        lcd_set_color(*self.color)

        lcd_fill((self.x - self.width) - 10, self.y, self.fill_size, self.height)

        lcd_set_color(*self.color)
        lcd_draw_box(
            (self.x - self.width) - 10, self.y, self.x - 10, self.y + self.height
        )


class HeartView(View):
    def __init__(self, name="", x_pos=10, y_pos=5, width=100, height=10):
        self.width = width
        self.height = height
        self.x = x_pos
        self.y = y_pos

        self.lifes = 3
        self.draw()

    def update_lifes(self, lifes):
        self.lifes = lifes
        self.draw()

    def draw(self):
        # ship padding
        heart_padding = 0
        heart_pos = 50
        for h in range(self.lifes):
            lcd_set_color(*(0, 0, 0))
            lcd_fill(heart_pos + heart_padding, self.y - 3, 16, 16)
            lcd_blit_file("heart.rgb", heart_pos + heart_padding, self.y - 3, 16, 16)
            heart_padding += 20

        lcd_set_color(*(0, 0, 0))
