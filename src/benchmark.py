import pygame, sys, os
import pygame._sdl2

from copy import deepcopy
from random import randint

SCREEN_W = 1280
SCREEN_H = 1024

ENTITY_W = 32
ENTITY_H = 32

# os.environ['SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITION'] = os.environ.get("SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR")

pygame.init()

pygame_screen = pygame.display.set_mode(
    (SCREEN_W, SCREEN_H), vsync=0, flags=pygame.SCALED
)
window = pygame._sdl2.Window.from_display_module()

renderer = pygame._sdl2.Renderer.from_window(window)
renderer.draw_color = (255, 255, 255, 255)

image_surface = pygame.image.load("sprite.png").convert_alpha()
base_img_surf = image_surface.copy()
hardware_image_surface = pygame._sdl2.Texture.from_surface(renderer, image_surface)

clock = pygame.time.Clock()

sprite_x, sprite_y = (0, 0)
entities = []


class Entity:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.h = ENTITY_W
        self.w = ENTITY_H
        self.dx = dx
        self.dy = dy

    def get_rect(self, scale_factor):
        return pygame.Rect(
            (
                self.x,
                self.y,
                self.w * scale_factor,
                self.h * scale_factor,
            )
        )

    def step(self):
        self.x += self.dx
        self.y += self.dy

        if self.x <= 0 or self.x >= SCREEN_W + ENTITY_W:
            self.dx = self.dx * -1

        if self.y <= 0 or self.y >= SCREEN_H - ENTITY_H:
            self.dy = self.dy * -1


for i in range(25_000):
    entities.append(
        Entity(
            randint(0 + ENTITY_W, SCREEN_W - ENTITY_W),
            randint(0 + ENTITY_H, SCREEN_H - ENTITY_H),
            randint(-100, 100) / 10,
            randint(-100, 100) / 10,
        )
    )

from time import time as epoch


scale_factor = 1
image_surface = pygame.transform.scale(
    base_img_surf, (ENTITY_W * scale_factor, ENTITY_H * scale_factor)
)

use_sdl2 = False
while True:
    start = epoch()
    # msec = clock.tick(60)
    pygame_screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                quit()

            if event.key == pygame.K_z:
                use_sdl2 = not use_sdl2

            if event.key == pygame.K_d:
                scale_factor += 0.1
                image_surface = pygame.transform.scale(
                    base_img_surf, (ENTITY_W * scale_factor, ENTITY_H * scale_factor)
                )
            if event.key == pygame.K_f:
                scale_factor -= 0.1
                image_surface = pygame.transform.scale(
                    base_img_surf, (ENTITY_W * scale_factor, ENTITY_H * scale_factor)
                )

    [e.step() for e in entities]

    if use_sdl2:
        renderer.clear()
        for e in entities:
            renderer.blit(hardware_image_surface, e.get_rect(scale_factor))
    else:
        for e in entities:
            pygame_screen.blit(image_surface, e.get_rect(scale_factor))

    end = epoch()
    print(f"{1 / (end - start):.2f} fps")
    # print(clock.get_fps(), scale_factor)

    if use_sdl2:
        renderer.present()
    else:
        pygame.display.flip()
