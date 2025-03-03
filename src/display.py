from random import randint
import sprite


class Texture:
    def __init(self, file, w, h):
        self.file = file
        self.w = w
        self.h = h


class BoardDisplay:
    def __init__(self):
        from lcd import lcd_init, lcd_clear

        lcd_init()
        lcd_clear()
        self.erase = []
        self.init_write()

        # self.files = {}
        # with open("dragon sample.rgb", "rb") as f:
        #     self.files["dragon"] = Texture(f.read(32 * 32 * 3), 32, 32)

    # def draw_texture(self, texture_name, x, y, w, h):
    #     lcd_blit_file(
    #         self.files[texture_name],
    #         x,
    #         y,
    #         self.files[texture_name].w,
    #         self.files[texture_name].h,
    #     )
    def draw_world(self, world):
        from lcd import lcd_blit_file, lcd_set_color, lcd_fill

        lcd_set_color(0, 0, 0)
        for _ in self.erase:
            x, y, w, h = self.erase.pop()
            lcd_fill(int(x - w / 2), int(y - w / 2), w, h)
        for name, values in world.sprites.items():
            print(f"{name}:{values}")
            x, y, _ = values["pos"]
            # print(sprite)
            # sprite.draw()
            w, h = values["dim"]
            lcd_blit_file(
                values["fname"],
                int(x - w / 2),
                int(y - w / 2),
                w,
                h,
                values.get("frame"),
            )
            self.erase.insert(0, (x, y, w, h))

    def init_write(self):
        self.col_start = randint(10, 120)
        self.col = self.col_start
        self.row = randint(10, 120)

    def stdout(self, text="", end="\n"):
        from lcd import lcd_draw_char

        col_start = self.col_start
        col = self.col
        row = self.row
        text = text.upper()
        text += end
        for char in text:
            print(char, end="")
            if col >= 400:
                col = col_start
                row += 12
            if char == "\n":
                col = col_start
                row += 12

            else:
                lcd_draw_char(col, row, char)
                col += 6


class PygameDisplay:

    def __init__(self):
        import pygame
        from config import config

        self.erase = []

        pygame.init()
        pygame.display.set_caption("lovelace")
        self.screen = pygame.display.set_mode((480, 320))
        self.clock = pygame.time.Clock()

    def draw_world(self, world):
        import pygame

        self.screen.fill((0, 0, 0))
        for name, values in world.sprites.items():
            print(f"{name}:{values}")
            x, y, _ = values["pos"]

            w, h = values["dim"]
            pygame.draw.circle(self.screen, (255, 255, 0), (x, y), w)
        pygame.display.flip()


def printsc(text="", end=""):
    print(text, end=end)


class Fake_Display:
    def __init__(self):
        pass

    def draw_world(self, world):
        pass

    def stdout(self, text):
        pass


def test_display():
    from time import sleep
    import pygame

    display = PygameDisplay()

    from world import World

    world = World(world_id=0)
    world.sprites["mysprite"] = {"pos": [10, 10, 0], "dim": [10, 10]}
    print(world.sprites)
    # world.
    for _ in range(1_00):
        display.draw_world(world)
        world.sprites["mysprite"]["pos"][0] += 1
        world.sprites["mysprite"]["pos"][1] += 1
        world.sprites["mysprite"]["dim"][0] += 1
        sleep(1e-2)


if __name__ != "__main__":
    display = BoardDisplay()
