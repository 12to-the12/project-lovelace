import pygame
import sys

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

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
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

from network import Network
network = Network()

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                ball.acc.x = -1
            if event.key == pygame.K_RIGHT:
                ball.acc.x = 1
            if event.key == pygame.K_UP:
                ball.acc.y = -1
            if event.key == pygame.K_DOWN:
                ball.acc.y = 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                ball.acc.x = 0
            if event.key == pygame.K_RIGHT:
                ball.acc.x = 0
            if event.key == pygame.K_UP:
                ball.acc.y = 0
            if event.key == pygame.K_DOWN:
                ball.acc.y = 0

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
    ball.apply()
    # Draw a ciK_LEFTrcle
    center = (
        width // 2 + ball.pos.x / 1000,
        height // 2 + ball.pos.y / 1000,
    )  # Center of the screen
    radius = 50
    pygame.draw.circle(screen, RED, center, radius)

    # Update the display
    pygame.display.flip()
