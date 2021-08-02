import pygame as pg


class Button:

    def __init__(self, text, pos, f_size=32, on_click=None, positioning='center', color_0=(61, 110, 112), color_1=(255, 0, 255)):

        self.text_color_0 = color_0
        self.text_color_1 = color_1
        self.font = 'data/fonts/text_font.ttf'
        font = pg.font.Font(self.font, f_size)
        text_surface = font.render(text, True, self.text_color_0)
        size = text_surface.get_size()

        if positioning == 'topleft':
            self.rect = pg.Rect(pos, size)
        elif positioning == 'center':
            self.rect = pg.Rect((0, 0), size)
            self.rect.center = pos
        elif positioning == 'midbottom':
            self.rect = pg.Rect((0, 0), size)
            self.rect.midbottom = pos

        self.button_canvas = pg.Surface(size)
        self.button_canvas.fill((25, 26, 27, 255))
        self.button_canvas.blit(text_surface, (0, 0))

        text_surface = font.render(text, True, self.text_color_1)
        self.hoover_canvas = pg.Surface(size)
        self.hoover_canvas.fill((25, 26, 27, 255))
        self.hoover_canvas.blit(text_surface, (0, 0))

        self.output = self.button_canvas

        self.on_click = on_click

    def draw(self, display):
        display.blit(self.output, self.rect.topleft)

    def update(self, click=False):
        mx, my = pg.mouse.get_pos()
        if self.rect.collidepoint(mx, my):
            self.output = self.hoover_canvas
            if click is True:
                if self.on_click is not None:
                    self.on_click()
        else:
            self.output = self.button_canvas


class TextLabel(Button):
    def __init__(self, text, pos, f_size=32, color=(61, 110, 112), positioning='center'):
        Button.__init__(self, text, pos, f_size, None, positioning)
        self.color = color

    def update(self, click=False):
        pass


class DialogueWindow:

    def __init__(self, quotes):
        window_size = pg.display.get_window_size()
        self.quotes = quotes
        self.canvas = pg.Surface((window_size[0], window_size[1] * .3))
        self.rect = pg.Rect(0, 0, window_size[0], window_size[1] * .3)
        self.color = (50, 41, 71)
        self.font = 'data/fonts/text_font.ttf'
        self.quotes = quotes
        self.quote_number = 0
        self.quotation_counter = 0

        self.buttons = []
        self.click = False
        self.display_text = None
        self.talk = False
        self.show_eq = False
        self.button_key = ''
        self.button_sounds = None

        x, y = 32, 32

        for q in quotes:
            self.buttons.append(Button(q, (x, y)))
            y += 32

    def draw(self, display):
        self.canvas.fill(self.color)
        if self.display_text is not None:
            text = self.display_text[self.quote_number]
            n = int(self.quotation_counter)
            self.draw_text(self.canvas.get_rect().center, text[0:n], self.canvas, (0, 128, 128))
        else:
            for button in self.buttons:
                button.draw(self.canvas)
        display.blit(self.canvas, (0, 0))

    def update(self, delta_time):
        if self.display_text is not None:
            # sound
            if self.quotation_counter == 0:
                if self.button_sounds is not None:
                    self.button_sounds[self.quote_number].play()

            quote_len = len(self.display_text[self.quote_number])
            if self.quotation_counter < quote_len:
                self.quotation_counter += .25 * delta_time

            if self.click is True:
                if self.quotation_counter < quote_len:
                    self.quotation_counter = quote_len - 1

                else:
                    self.button_sounds[self.quote_number].fadeout(250)
                    self.quotation_counter = 0
                    self.quote_number += 1
                    if self.quote_number == len(self.display_text):
                        self.quote_number = 0
                        if self.button_key == 'exit':
                            self.talk = False
                        elif self.button_key == 'shop':
                            self.talk = False
                            self.show_eq = True
                        self.display_text = None

        else:
            for button in self.buttons:
                button.update()
                if button.output == button.hoover_canvas and self.click is True:
                    try:
                        self.button_sounds = self.quotes[button.text]['sound']
                    except:
                        print('no sound')
                    self.button_key = self.quotes[button.text]['key']
                    self.display_text = self.quotes[button.text]['quote']

    def draw_text(self, pos, text, display, color):
        font = pg.font.Font(self.font, 24)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = pos
        display.blit(text_surface, text_rect)
