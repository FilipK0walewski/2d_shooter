import pygame as pg
from data.equipment import Chest, Item
from data.images import Spritesheet
from data.weapons import Pistol, Shotgun, Uzi
import json, random

with open('data/assets/sprites/items.json') as f:
    items = json.load(f)
f.close()


class Storage(pg.sprite.Sprite):

    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self)
        items_spritesheet = Spritesheet('data/assets/sprites/items.png')
        self.img = items_spritesheet.get_image('furniture', 'chest', 'image')
        self.rect = self.img.get_rect()
        self.rect.center = pos

        self.store = Chest()
        self.items = {
            'pistol': Pistol(items['weapon']['pistol'], 2),
            'shotgun': Shotgun(items['weapon']['shotgun'], 1),
            'uzi': Uzi(items['weapon']['uzi'], 2),
            'pistol_ammo': Item(items['item']['pistol_ammo'], random.randint(11, 19)),
            'shotgun_ammo': Item(items['item']['shotgun_ammo'], random.randint(11, 19)),
            'uzi_ammo': Item(items['item']['uzi_ammo'], 1024)
        }

        self.store.add_item(self.items['uzi'])
        self.store.add_item(self.items['uzi_ammo'])

    def draw(self, display, camera):
        display.blit(self.img, (self.rect.x - camera.x, self.rect.y - camera.y))
