import pygame
from mainloop.environment import Environment
from mainloop.screens import Screens
from mainloop.mainloop import MainLoop
from game.playscreen import PlayScreen


def create_digger_screens(env: Environment) -> Screens:
    screens = Screens(env)

    # Create game screen
    play_screen = PlayScreen(env, interval=60)  # 60 FPS

    # Add screen and make it active
    screens.add_screen("play", play_screen, make_active=True)

    return screens


def main() -> int:
    pygame.init()
    display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    env = Environment(display)
    screens = create_digger_screens(env)
    loop = MainLoop(env, screens)
    loop.run()
    return 0
