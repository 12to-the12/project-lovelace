from math import sin
from lcd import *

sprites = []

class Sprite:
    fname = ""
    w = 32
    h = 32
    x = 0.0
    xv = 0.25
    y = 0.0
    yv = 0.25
    def __init__(self, fname, w, h):
        self.fname = fname
        self.w = w
        self.h = h
        sprites.append(self)
    def draw(self):
        x = int(self.x)
        y = int(self.y)
        xv = int(abs(self.xv)) or 1
        yv = int(abs(self.yv)) or 1
        lcd_fill(x - xv, y - yv, self.w + 2*xv, yv) # top TODO: not sure why I had to do height of 2 (should be 1) in order to avoid artifacts
        lcd_fill(x - xv, y + self.h, self.w + 2*xv, yv) # bottom TODO: not sure why I had to do height of 2 (should be 1) in order to avoid artifacts
        lcd_fill(x - xv, y, xv, self.h) # left
        lcd_fill(x + self.w, y, xv, self.h) # right
        lcd_blit_file(self.fname, x, y, self.w, self.h)
    def move(self):
        self.x += self.xv
        x = int(self.x)
        if self.x < 0:
            x = 0
            self.xv = -self.xv
        elif x + self.w >= width:
            self.x = width - self.w
            self.xv = -self.xv
        self.y += self.yv
        y = int(self.y)
        if y < 0:
            y = 0
            self.yv = -self.yv
        elif y + self.h >= height:
            y = height - self.h
            self.yv = -self.yv
    def die(self):
        self.draw()
        x = int(self.x)
        y = int(self.y)
        lcd_fill(x, y, self.w, self.h)
        sprites.remove(self)

class Player(Sprite):
    age = 0
    def __init__(self):
        Sprite.__init__(self, "dragon sample.rgb", 32, 32)
    def move(self):
        Sprite.move(self)
        self.age += 1
        if self.age % 25 == 0:
            Fireball(self.x, self.y, randint(-6, 6), randint(-6, 6))

class Fireball(Sprite):
    ttl = 100
    def __init__(self, x, y, xv, yv):
        Sprite.__init__(self, "fireball sample.rgb", 16, 16)
        self.x = x
        self.y = y
        self.xv = xv
        self.yv = yv
    def move(self):
        Sprite.move(self)
        self.ttl -= 1
        if self.ttl <= 0:
            self.die()


def main():
    lcd_init()
    lcd_clear()
    player = Player()
    while True:
        for sprite in sprites:
            sprite.draw()
            sprite.move()

if __name__ == "__main__":
    main()
