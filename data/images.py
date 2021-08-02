import pygame as pg
import json


class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pg.image.load(filename).convert()
        self.meta_data = self.filename.replace('png', 'json')
        with open(self.meta_data) as f:
            self.data = json.load(f)
        f.close()

    def get_sprite(self, x, y, w, h):
        sprite = pg.Surface((w, h))
        sprite.set_colorkey((0, 0, 0))
        temp_rect = pg.Rect(x, y, w, h)
        sprite.blit(self.sprite_sheet, (0, 0), temp_rect)
        return sprite

    def parse_sprite(self, name):
        sprite = self.data['frames'][name]['frame']
        x, y, w, h = sprite["x"], sprite["y"], sprite["w"], sprite["h"]
        image = self.get_sprite(x, y, w, h)
        return image

    def get_image(self, type, item, image_name):
        sprite = self.data[type][item][image_name]
        x, y, w, h = sprite["x"], sprite["y"], sprite["w"], sprite["h"]
        image = self.get_sprite(x, y, w, h)
        return image
