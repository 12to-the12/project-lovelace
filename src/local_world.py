


class Local_World:
    def __init__(self):
        self.sprites = {}

    # refeshes client world to be in sync with server
    def update_state_from_packet(self, packet):
        for sprite_name, sprite_dict in packet["sprites"].values():
            if sprite_name not in self.sprites.keys():
                pass
                # self.sprites[sprite_name] = build_sprite_from_packet(name, sprite_dict)
