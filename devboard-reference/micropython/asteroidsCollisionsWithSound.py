from utime import sleep
from urandom import randint
from lcd import *
from machine import Pin, SPI, ADC
import _thread
from machine import Pin, PWM
from time import sleep

# Set up the sound pin with PWM
sound = PWM(Pin(13))  # Create a PWM object on Pin 13
lock = _thread.allocate_lock() 

def play_tone(frequency, duration, volume=425):
    lock.acquire()
    """
    Play a tone on the sound pin.
    :param frequency: Frequency of the tone in Hz.
    :param duration: Duration of the tone in seconds.
    :param volume: Duty cycle (0-1023), higher is louder.
    """
    sound.freq(frequency)  # Set the frequency
    sound.duty_u16(volume)  # Set the duty cycle (0 to 1023 for 10-bit resolution)
    sleep(duration)  # Play for the given duration
    sound.duty_u16(0)  # Turn off the sound after the duration
    lock.release()
    

# Example: Play a scale
#def play_scale():
#    notes = [262, 294, 330, 349, 392, 440, 494, 523]  # Frequencies of a C major scale
#    for note in notes:
#        print(note)
#        play_tone(note, 0.5)  # Play each note for 0.5 seconds
#        sleep(0.1)  # Short pause between notes



def threaded_beep():
    """
    Thread-safe beep function.
    """
    if lock.acquire(False):  # Try to acquire the lock without blocking
        try:
            _thread.start_new_thread(play_tone, (392, 0.5))  # Start the thread
        finally:
            lock.release()  # Ensure the lock is released after the thread finishes
    else:
        print("Thread already in use, skipping beep.")


background = (0,0,0)

# all sprites
sprites = []

class Sprite:
    name = ""
    health = 0
    x = 0.
    y = 0.
    vx = 0.
    vy = 0.
    w = 1
    h = 1
    color = (0,0,0)
    def __init__(self, name = "", health = 100, color=None):
        self.name = name
        self.health = health
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

    def draw(self):
        lcd_set_color(*self.color)
        lcd_fill(int(self.x), int(self.y), self.w, self.h)


class Ship(Sprite):
    w = 6
    h = 6
    bulletCount = 0
    tag = 1<<0

    def fire(self):
        if self.bulletCount >= 10:
            return
        self.bulletCount += 1
        bullet = Bullet(f"Bullet {self.bulletCount}", color=(255,255,255))
        bullet.x = self.x
        bullet.y = self.y
        bullet.vx = self.vx * 2
        bullet.vy = self.vy * 2


class Bullet(Sprite):
    w = 3
    h = 3
    tag = 1<<1
    def move(self):
        super().move()
        self.takeDamage(3)
    def destroy(self):
        ship.bulletCount -= 1
        super().destroy()

class Asteroid(Sprite):
    tag = 1<<2
    w = 10
    h = 7

def is_collision(x1_1, y1_1, x2_1, y2_1, x1_2, y1_2, x2_2, y2_2):
    return (
        x1_1 < x2_2 and
        x2_1 > x1_2 and
        y1_1 < y2_2 and
        y2_1 > y1_2
    )

def checkColl():
    for i in reversed(range(len(sprites))):  # Iterate in reverse to safely remove elements
        object_check = sprites[i]
        for v in range(0,i):  # Check against all previous sprites
            object_check_with = sprites[v]
        
            value = object_check.tag | object_check_with.tag
          
            # Check for Asteroid and Bullet types
            if value == (Asteroid.tag | Bullet.tag):
                # Calculate bounding boxes
                asteroid_x1, asteroid_y1 = object_check.x, object_check.y
                asteroid_x2, asteroid_y2 = object_check.x + object_check.w, object_check.y + object_check.h
                
                bullet_x1, bullet_y1 = object_check_with.x, object_check_with.y
                bullet_x2, bullet_y2 = object_check_with.x + object_check_with.w, object_check_with.y + object_check_with.h
                
                # Check for collision
                if is_collision(bullet_x1, bullet_y1, bullet_x2, bullet_y2,
                                asteroid_x1, asteroid_y1, asteroid_x2, asteroid_y2):
                    object_check.destroy()      # Destroy the asteroid
                    object_check_with.destroy()  # Destroy the bullet
                    

                    threaded_beep()
                    return

        

    """
    for bullet in bullet_sprites:
        for ast in asteroid_sprites:
            # Calculate the bounding box of the bullet and asteroid
            bullet_x1 = bullet.x
            bullet_y1 = bullet.y
            bullet_x2 = bullet.x + bullet.w
            bullet_y2 = bullet.y + bullet.h
            
            ast_x1 = ast.x
            ast_y1 = ast.y
            ast_x2 = ast.x + ast.w
            ast_y2 = ast.y + ast.h

            # Check for collision
            if is_collision(bullet_x1, bullet_y1, bullet_x2, bullet_y2, 
                            ast_x1, ast_y1, ast_x2, ast_y2):
                ast.destroy()
                bullet.destroy()
                print("collision")
    """

def play():
    ship.x = width / 2
    ship.y = height / 2
    speed = 10
    while True:
        ship.vx = (joy_x.read_u16() / 2**16 - .5) * speed
        ship.vy = -(joy_y.read_u16() / 2**16 - .5) * speed
        for sprite in sprites:
            sprite.move()
            # sprite.draw()
        if not button_a.value():
            beep()
            pass
        if not button_b.value():
            ship.fire()
        checkColl()
        # print(f'{x=}, {y=}')
        sleep(1/60)

ship = Ship("Player 1", color = (10, 10, 128))

def spawnAsteroid():
    asteroid = Asteroid()
    asteroid.x = randint(0, width-1)
    asteroid.y = randint(0, height - 1)
    asteroid.vx = randint(-3, 3)
    asteroid.vy = randint(-3, 3)
    sprites.append(asteroid)

for _ in range(5):
    spawnAsteroid()

lcd_init()
lcd_clear(*background)
play()
