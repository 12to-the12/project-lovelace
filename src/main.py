import game
import profile
from buzzer import buzzer
from time import sleep

from hud import Menu

if __name__ == "__main__":
    menu = Menu()
    game.game_init()
    game.intro()
    game.start_loop()
    # profile.profile()

