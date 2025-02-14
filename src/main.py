import pygame
import sys
import asyncio

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

    def apply(self):
        self.vel.x += self.acc.x
        self.vel.y += self.acc.y
        self.vel.z += self.acc.z

        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        self.pos.z += self.vel.z

        self.vel.x *= 0.998
        self.vel.y *= 0.998
        self.vel.z *= 0.998


# Initialize Pygame
pygame.init()
update_interval = 20  # ms
# Set up display
width, height = 800, 600
# screen = pygame.display.set_mode((width, height))

screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
surface = pygame.Surface((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
print(pygame.display.get_driver())
print(pygame.display.get_surface())

pygame.display.set_caption("Draw a Circle")

# Define colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
x = 0
y = 0
left = False
right = False
up = False
down = False

ball = spatial_object()
ball.pos.x = 5
ball.pos.y = 5


from network import Network

network = Network()

from time import time as epoch
from time import sleep

stamp = epoch()
# Main loop

awaiting = None


async def fetch_worldstate():
    global worldstate
    worldstate = network.send((ball.pos.x, ball.pos.y, ball.pos.z))


async def update():
    global stamp, awaiting
    if (epoch() - stamp) * 1000 > update_interval:
        if awaiting:
            await awaiting
        awaiting = asyncio.create_task(fetch_worldstate())
        # await awaiting
        stamp = epoch()
        if worldstate:
            # print(worldstate)
            pass
        else:
            print("error connecting")
        # print(worldstate)


ball.pos.x = width // 2
ball.pos.y = height // 2
worldstate = []
# asyncio.run(fetch_worldstate())
while True:
    start = epoch()
    asyncio.run(update())
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
        ball.acc.x = 1e-3
    if left:
        ball.acc.x = -1e-3
    if right and left:
        ball.acc.x = 0
    if (not right) and (not left):
        ball.acc.x = 0
    if down:
        ball.acc.y = 1e-3
    if up:
        ball.acc.y = -1e-3
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
    pygame.draw.circle(screen, RED, center, radius)
    # Draw a ciK_LEFTrcle
    for x, y, z in worldstate:
        center = (
            x,
            y,
        )
        radius = 50
        pygame.draw.circle(screen, RED, center, radius)

    # Update the display
    pygame.display.flip()
    end = epoch()
    asyncio.run(update())
    if (epoch() - stamp) * 1000 > update_interval:
        elapsed = end - start
        print(f"{1 / elapsed:6.0f} fps")
