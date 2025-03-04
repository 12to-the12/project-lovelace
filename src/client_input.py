from config import config


class BoardInput:
    def __init__(self):
        from machine import ADC, Pin, PWM, SPI

        self.x_pin = ADC(Pin(26, pull=None))
        self.y_pin = ADC(Pin(27, pull=None))
        self.left_pin = Pin(15, Pin.IN)
        self.right_pin = Pin(14, Pin.IN)

    @property
    def x(self):
        x = (self.x_pin.read_u16() / 2**16 - 0.5) * 2
        return x**3

    @property
    def y(self):
        y = (self.y_pin.read_u16() / 2**16 - 0.5) * 2
        return -(y**3)

    @property
    def button_left(self):
        return not self.left_pin.value()

    @property
    def button_right(self):
        return not self.right_pin.value()

    def read(self):
        return (self.x, self.y)


class PygameInput:
    def __init__(self):
        self.x_state = 0
        self.y_state = 0
        self.q = False
        self.w = False

        self.left = False
        self.right = False
        self.up = False
        self.down = False

    @property
    def x(self):
        self.update_keypresses()
        return self.x_state**3

    @property
    def y(self):
        self.update_keypresses()
        return self.y_state**3

    @property
    def button_left(self):
        self.update_keypresses()
        return self.q

    @property
    def button_right(self):
        self.update_keypresses()
        return self.w

    def update_keypresses(self):
        import pygame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                # sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    left = True
                if event.key == pygame.K_RIGHT:
                    right = True
                if event.key == pygame.K_UP:
                    up = True
                if event.key == pygame.K_DOWN:
                    down = True
                if event.key == pygame.K_q:
                    self.q = True
                if event.key == pygame.K_w:
                    self.w = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    left = False
                if event.key == pygame.K_RIGHT:
                    right = False
                if event.key == pygame.K_UP:
                    up = False
                if event.key == pygame.K_DOWN:
                    down = False
                if event.key == pygame.K_q:
                    self.q = False
                if event.key == pygame.K_w:
                    self.w = False

            if right:
                self.x = 1
            if left:
                self.x = -1
            if right and left:
                self.x = 0
            if (not right) and (not left):
                self.x = 0

            if down:
                self.y = 1
            if up:
                self.y = -1
            if down and up:
                self.y = 0
            if (not up) and (not down):
                self.y = 0


from config import config

if config.desktop_mode:
    client_input = PygameInput()
else:
    client_input = BoardInput()

# def serialized_input():
#     return joystick.read(), button_left(), button_left()


# if config.desktop_mode:
#     readinput = readdesktopinput
# else:
#     readinput = readinputboard

