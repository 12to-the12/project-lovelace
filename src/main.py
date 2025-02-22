from game import game
from profile import profile,joystick_demo
from time import sleep
from lcd import lcd_start_tone, lcd_stop_tone

# def clock_wait(fps):
#     global stampb
#     frame_time = 1 / fps
#     now = epoch()
#     elapsed = now - stampb
#     if elapsed < frame_time:
#         sleep(frame_time - elapsed)
#     stampb = now


if __name__ == "__main__":
    # joystick_demo()
    game()
