from lcd import *


class Texture:
    def __init(self, file, w, h):
        self.file = file
        self.w = w
        self.h = h


class Display:
    def __init__(self):
        self.erase = []
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
                values["fname"], int(x - w / 2), int(y - w / 2), w, h, values.get("frame")
            )
            self.erase.insert(0, (x, y, w, h))


display = Display()
