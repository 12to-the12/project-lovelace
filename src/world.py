from sprite import Entity


class World:
    def __init__(self, world_id=None):
        self.world_id = world_id
        assert (
            world_id != None
        ), f"world instantiated without id {world_id} isn't valid?"
        self.display_width = 480
        self.display_height = 320
        # where the world is in relation to the viewport
        # top left corner of the screen
        self.sprites = {}
        self.viewport_entity = Entity()

    # def update_from_packet(self,name,worldstate:str):
    #     self.sprites[packet]
