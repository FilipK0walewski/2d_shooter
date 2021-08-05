from data.game import Game
from data.menu import MainMenu, PauseMenu, SettingsMenu, CreditsMenu, GraphicsMenu, AudioMenu, ControlsMenu
from data.launcher import GameLauncher
from data.endless_mode import EndlessMode
from data.multiplayer_mode import MultiplayerMode
import pygame as pg
import json


def get_screen_info(info):
    resolution = info['game']['screen']['resolution']
    fullscreen = info['game']['screen']['fullscreen']
    x, y = '', ''
    temp = False
    for n in resolution:
        if n == 'x':
            temp = True
        else:
            if temp is False:
                x += n
            else:
                y += n

    window_width = int(x)
    window_height = int(y)

    return (window_width, window_height), fullscreen


class Menager:

    def __init__(self, info):

        self.running = True

        size, fullscreen = get_screen_info(info)

        if fullscreen == 1:
            window = pg.display.set_mode(size, pg.FULLSCREEN)
        else:
            window = pg.display.set_mode(size)

        # game modes
        self.normal_mode = Game(window)
        self.endless_mode = EndlessMode(window)
        self.multiplayer_mode = MultiplayerMode(window)
        self.game = self.normal_mode
        # menus
        self.main_menu = MainMenu(window, self)
        self.pause_menu = PauseMenu(window, self)
        self.settings_menu = SettingsMenu(window, self)
        self.credits_menu = CreditsMenu(window, self)

        self.graphics_menu = GraphicsMenu(window, self)
        self.audio_menu = AudioMenu(window, self)
        self.controls_menu = ControlsMenu(window, self)

        self.current_menu = self.main_menu


def start_game():

    with open('startup.json') as f:
        game_info = json.load(f)
    f.close()

    launcher = GameLauncher(game_info)
    launcher.root.mainloop()
    temp = launcher.temp()

    if temp is True:
        menager = Menager(game_info)
        while menager.running is True:
            menager.current_menu.display_menu = True
            menager.current_menu.main_loop()
            menager.game.main_loop()


if __name__ == '__main__':
    start_game()
