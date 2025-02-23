class World:
    def __init__(self):
        self.display_width = 480
        self.display_height = 320
        # where the world is in relation to the viewport
        # top left corner of the screen
        self.viewport_location = (0, 0)
        self.sprites = {}

    def legitimize(self, id):  # means we're network connected...
        self.id = id


world = World()
