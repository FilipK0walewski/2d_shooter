import pygame as pg
from data.dialogue import Button, TextLabel
from data.weapons import Aimer


class Menu:

    def __init__(self, window, menager):

        self.menager = menager

        # screen
        self.window = window
        self.clock = pg.time.Clock()
        self.display_menu = True
        self.opacity = 255
        self.camera = pg.math.Vector2(0, 0)
        self.size = pg.display.get_window_size()
        self.canvas = pg.Surface(self.size, pg.SRCALPHA)

        self.bg_color = (25, 26, 27, self.opacity)

        # buttons
        self.buttons = []

        # cursor
        self.camera = pg.math.Vector2(0, 0)
        self.cursor = Aimer()
        self.click = False

    def main_loop(self):

        while self.display_menu:
            self.check_input()
            self.update()
            self.draw()
            self.clock.tick(120)
            self.reset_inputs()

    def draw(self):
        self.canvas.fill(self.bg_color)
        for button in self.buttons:
            button.draw(self.canvas)
        self.cursor.draw(self.canvas)
        self.window.blit(self.canvas, (0, 0))
        pg.display.flip()

    def update(self):
        self.cursor.update()
        for button in self.buttons:
            button.update(self.click)

    def check_input(self):

        for event in pg.event.get():

            if event.type == pg.QUIT:
                self.display_menu = False

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.click = True

    def reset_inputs(self):
        self.click = False


# MAIN MENU#############################################################################################################


class MainMenu(Menu):
    def __init__(self, game, menager):
        Menu.__init__(self, game, menager)

        title = TextLabel('MAIN MENU', (self.size[0] * .5, self.size[1] * .2), 96)
        new_game_button = Button('NORMAL GAME', (self.size[0] * .5, self.size[1] * .38), 48, on_click=self.new_game)
        e_game_button = Button('ENDLESS MODE', (self.size[0] * .5, self.size[1] * .45), 48, on_click=self.endless_game)
        settings_button = Button('SETTINGS', (self.size[0] * .5, self.size[1] * .52), 48, on_click=self.settings)
        credits_button = Button('CREDITS', (self.size[0] * .5, self.size[1] * .59), 48, on_click=self.credits)
        exit_button = Button('EXIT', (self.size[0] * .5, self.size[1] * .8), 48, on_click=self.exit_game)

        self.buttons.extend([title, new_game_button, e_game_button, settings_button, credits_button, exit_button])

    def new_game(self):
        self.menager.game = self.menager.normal_mode
        self.menager.game.playing = True
        self.menager.current_menu = self.menager.pause_menu
        self.display_menu = False

    def endless_game(self):
        self.menager.game = self.menager.endless_mode
        self.menager.game.playing = True
        self.menager.current_menu = self.menager.pause_menu
        self.display_menu = False

    def settings(self):
        self.menager.current_menu = self.menager.settings_menu
        self.display_menu = False

    def credits(self):
        self.menager.current_menu = self.menager.credits_menu
        self.display_menu = False

    def exit_game(self):
        self.menager.running = False
        self.display_menu = False


# PAUSE#################################################################################################################


class PauseMenu(Menu):
    def __init__(self, game, menager):
        Menu.__init__(self, game, menager)

        title = TextLabel('PAUSE', (self.size[0] * .5, self.size[1] * .2), 96)
        resume_button = Button('RESUME', (self.size[0] * .5, self.size[1] * .45), 48, on_click=self.resume_game)
        exit_button = Button('EXIT', (self.size[0] * .5, self.size[1] * .8), 48, on_click=self.back_to_menu)

        self.buttons.extend([title, resume_button, exit_button])

    def resume_game(self):
        self.menager.game.playing = True
        self.display_menu = False

    def back_to_menu(self):
        self.menager.current_menu = self.menager.main_menu
        self.display_menu = False


# SETTINGS##############################################################################################################


class SettingsMenu(Menu):
    def __init__(self, game, menager):
        Menu.__init__(self, game, menager)

        title = TextLabel('SETTINGS', (self.size[0] * .5, self.size[1] * .2), 96)
        graphics_button = Button('GRAPHICS', (self.size[0] * .5, self.size[1] * .38), 48, on_click=self.go_to_graphics)
        audio_button = Button('AUDIO', (self.size[0] * .5, self.size[1] * .45), 48, on_click=self.go_to_audio)
        controls_menu = Button('CONTROLS', (self.size[0] * .5, self.size[1] * .52), 48, on_click=self.go_to_controls)

        exit_button = Button('BACK', (self.size[0] * .5, self.size[1] * .8), 48, on_click=self.back_to_menu)

        self.buttons.extend([title, graphics_button, audio_button, controls_menu, exit_button])

    def go_to_graphics(self):
        self.menager.current_menu = self.menager.graphics_menu
        self.display_menu = False

    def go_to_audio(self):
        self.menager.current_menu = self.menager.audio_menu
        self.display_menu = False

    def go_to_controls(self):
        self.menager.current_menu = self.menager.controls_menu
        self.display_menu = False

    def back_to_menu(self):
        self.menager.current_menu = self.menager.main_menu
        self.display_menu = False


# GRAPHICS##############################################################################################################


class GraphicsMenu(Menu):
    def __init__(self, game, menager):
        Menu.__init__(self, game, menager)

        title = TextLabel('GRAPHICS', (self.size[0] * .5, self.size[1] * .2), 96)
        brightness = TextLabel('BRIGHTNESS', (self.size[0] * .5, self.size[1] * .38), 48)

        exit_button = Button('BACK', (self.size[0] * .5, self.size[1] * .8), 48, on_click=self.back_to_menu)

        self.buttons.extend([title, brightness, exit_button])

    def back_to_menu(self):
        self.menager.current_menu = self.menager.settings_menu
        self.display_menu = False


# AUDIO#################################################################################################################


class AudioMenu(Menu):
    def __init__(self, game, menager):
        Menu.__init__(self, game, menager)

        title = TextLabel('AUDIO', (self.size[0] * .5, self.size[1] * .2), 96)
        brightness = TextLabel('MUSIC', (self.size[0] * .5, self.size[1] * .38), 48)

        exit_button = Button('BACK', (self.size[0] * .5, self.size[1] * .8), 48, on_click=self.back_to_menu)

        self.buttons.extend([title, brightness, exit_button])

    def back_to_menu(self):
        self.menager.current_menu = self.menager.settings_menu
        self.display_menu = False


# CONTROLS##############################################################################################################


class ControlsMenu(Menu):
    def __init__(self, game, menager):
        Menu.__init__(self, game, menager)

        title = TextLabel('CONTROLS', (self.size[0] * .5, self.size[1] * .2), 96)
        brightness = TextLabel('MOVEMENT', (self.size[0] * .5, self.size[1] * .38), 48)

        exit_button = Button('BACK', (self.size[0] * .5, self.size[1] * .8), 48, on_click=self.back_to_menu)

        self.buttons.extend([title, brightness, exit_button])

    def back_to_menu(self):
        self.menager.current_menu = self.menager.settings_menu
        self.display_menu = False


# CREDITS###############################################################################################################


class CreditsMenu(Menu):
    def __init__(self, game, menager):
        Menu.__init__(self, game, menager)

        text = TextLabel('CREATED BY', (self.size[0] * .5, self.size[1] * .35), 24)
        author = TextLabel('FILIP KOWALEWSKI', (self.size[0] * .5, self.size[1] * .45), 96)
        exit_button = Button('BACK', (self.size[0] * .5, self.size[1] * .8), 48, on_click=self.back_to_menu)

        self.buttons.extend([text, author, exit_button])

    def back_to_menu(self):
        self.menager.current_menu = self.menager.main_menu
        self.display_menu = False
