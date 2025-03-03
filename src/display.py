from lcd import lcd_blit_file


class Texture:
    def __init(self, file, w, h):
        self.file = file
        self.w = w
        self.h = h


class Display:
    def __init__(self):
        self.files = {}
        with open("dragon sample.rgb", "rb") as f:
            self.files["dragon"] = Texture(f.read(32 * 32 * 3), 32, 32)

    def draw_texture(self, texture_name, x, y, w, h):
        lcd_blit_file(
            self.files[texture_name],
            x,
            y,
            self.files[texture_name].w,
            self.files[texture_name].h,
        )


display = Display()
