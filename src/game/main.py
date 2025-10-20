import pygame
from mainloop.environment import Environment
from mainloop.screens import Screens
from mainloop.mainloop import MainLoop


def create_digger_screens(env: Environment) -> Screens:
    screens = Screens(env)
    return screens


def main() -> int:
    pygame.init()
    display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    env = Environment(display)
    screens = create_digger_screens(env)
    loop = MainLoop(env, screens)
    loop.run()
    return 0
