import pygame as pg
from data.dialogue import Button
from data.images import Spritesheet
from data.weapons import Pistol, Uzi, Shotgun
import json

with open('data/assets/sprites/items.json') as f:
    items = json.load(f)
f.close()


def copy_item(item, quantity):

    return_item = 0
    if item.type == 'weapon':
        if item.name == 'pistol':
            return_item = Pistol(items['weapon']['pistol'])
            return_item.quantity = quantity
        elif item.name == 'shotgun':
            return_item = Shotgun(items['weapon']['shotgun'])
            return_item.quantity = quantity
        elif item.name == 'uzi':
            return_item = Uzi(items['weapon']['uzi'])
            return_item.quantity = quantity
    else:
        return_item = Item(items['item'][item.name], quantity)

    return return_item


class Item:

    def __init__(self, info, quantity=1):
        spritesheet = Spritesheet('data/assets/sprites/items.png')
        self.name = info['name']
        self.type = info['type']
        self.code = info['code']
        self.description = info['description']
        self.icon = spritesheet.get_image('item', self.name, 'icon')
        self.icon_rect = self.icon.get_rect()
        self.quantity = quantity


class ItemSlot:

    def __init__(self, number, pos, size, type=None, item=None):
        self.number = number  # id
        self.image = pg.Surface((size, size))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.item = item

        self.color = (61, 110, 112)
        self.normal_color = (61, 110, 112)
        self.hover_color = (50, 62, 79)
        self.text_color = (255, 0, 255)
        self.font = 'data/fonts/text_font.ttf'

        self.display_info = False
        self.rect_info = pg.Rect(self.rect.bottomright[0], self.rect.bottomright[1], 48, 48)
        self.type = type

    def draw(self, display):
        if self.number != -1:
            pg.draw.rect(display, self.color, self.rect, border_radius=10)
        if self.item is not None:
            display.blit(self.item.icon, self.item.icon_rect)
            self.draw_text(self.item.icon_rect.center, str(self.item.quantity), display, self.text_color)

    def draw_info(self, display):
        if self.display_info is True:
            if self.item is None:
                pass
            else:
                pos_x = self.rect.bottomright[0] + 16
                pos_y = self.rect.bottomright[1] + 16
                pg.draw.rect(display, (0, 255, 0, 128), self.rect_info, border_radius=10)
                self.rect_info.w = 48
                self.rect_info.h = 48
                self.draw_text((pos_x, pos_y), 'name: ' + self.item.name, display, (0, 255, 0), True)
                pos_y += 32
                self.draw_text((pos_x, pos_y), 'type: ' + self.item.type, display, (0, 255, 0), True)
                pos_y += 32
                self.draw_text((pos_x, pos_y), 'quantity: ' + str(self.item.quantity), display, (0, 255, 0), True)
                pos_y += 32
                self.draw_text((pos_x, pos_y), self.item.description, display, (0, 255, 0), True)
                pos_y += 32
                self.draw_text((pos_x, pos_y), str(self.item.klasa), display, (0, 255, 0), True)

    def update(self, eq, cursor):

        if self.rect.collidepoint(cursor):
            self.color = self.hover_color
            self.display_info = True
        else:
            self.color = self.normal_color
            self.display_info = False

        if eq.l_click_shift or eq.l_click_ctrl:
            eq.l_click = False

        if eq.r_click_shift or eq.r_click_ctrl is True:
            eq.r_click = False

        if eq.l_click_shift:
            if self.item is not None and eq.temp_item.item is None and eq.exchange is True:
                if self.rect.collidepoint(cursor):
                    if eq.second_eq is not None:
                        temp_item = copy_item(self.item, self.item.quantity)
                        if cursor[0] > pg.display.get_window_size()[0] * .5:
                            eq.add_item(temp_item)
                            self.item = None
                        else:
                            eq.second_eq.add_item(temp_item)
                            self.item = None

        if eq.r_click_shift:
            if self.item is not None:
                if self.rect.collidepoint(cursor):
                    if eq.temp_item.item is None:
                        temp_q = int(self.item.quantity * .5)
                        temp = copy_item(self.item, temp_q)
                        self.item.quantity -= temp_q
                        eq.temp_item.item = temp
                    else:
                        if self.item.quantity == 1:
                            temp_q = 1
                        else:
                            temp_q = int(self.item.quantity * .5)
                        self.item.quantity -= temp_q
                        eq.temp_item.item.quantity += temp_q

        if eq.l_click_ctrl is True:
            if self.item is not None and eq.temp_item.item is None and self.type is None:
                if self.rect.collidepoint(cursor):
                    if self.item.type == 'weapon':
                        self.item.quantity -= 1
                        temp_item = copy_item(self.item, 1)
                        if self.item.quantity == 0:
                            self.item = None
                        if eq.equipped_items[3].item is not None:
                            eq.add_item(eq.equipped_items[3].item)
                        eq.equipped_items[3].item = temp_item
                    elif self.item.type == 'ammo':
                        temp_item = copy_item(self.item, self.item.quantity)
                        self.item = None
                        if eq.equipped_items[6].item is not None:
                            eq.add_item(eq.equipped_items[6].item)
                        eq.equipped_items[6].item = temp_item

        if eq.r_click_ctrl is True:
            if self.item is not None and eq.temp_item.item is None:
                if self.rect.collidepoint(cursor):
                    if self.item.type == 'weapon':
                        self.item.quantity -= 1
                        temp_item = copy_item(self.item, 1)
                        if self.item.quantity == 0:
                            self.item = None
                        if eq.equipped_items[5].item is not None:
                            eq.add_item(eq.equipped_items[5].item)
                        eq.equipped_items[5].item = temp_item
                    elif self.item.type == 'ammo':
                        temp_item = copy_item(self.item, self.item.quantity)
                        self.item = None
                        if eq.equipped_items[8].item is not None:
                            eq.add_item(eq.equipped_items[8].item)
                        eq.equipped_items[8].item = temp_item

        if eq.l_click is True:
            if self.rect.collidepoint(cursor):
                if eq.temp_item.item is None:
                    eq.temp_item.item = self.item
                    self.item = None
                else:
                    if self.type is None or self.type == eq.temp_item.item.type:
                        if self.item is None:
                            self.item = eq.temp_item.item
                            eq.temp_item.item = None
                        else:
                            if eq.temp_item.item.code == self.item.code:
                                self.item.quantity += eq.temp_item.item.quantity
                                eq.temp_item.item = None
                            else:
                                temp = self.item
                                self.item = eq.temp_item.item
                                eq.temp_item.item = temp
                    else:
                        print('wrong item type', ' ', self.type, eq.temp_item.item.type)

        if eq.r_click is True:
            if self.rect.collidepoint(cursor):
                if self.item is None:
                    pass
                else:
                    if self.type == 'weapon':
                        eq.add_item(self.item)
                        self.item = None
                    else:
                        if eq.temp_item.item is None:
                            temp = copy_item(self.item, 1)
                            self.item.quantity -= 1
                            eq.temp_item.item = temp
                        else:
                            if eq.temp_item.item.code == self.item.code:
                                self.item.quantity -= 1
                                eq.temp_item.item.quantity += 1
                            else:
                                print('not the same item')

        if self.item is not None:
            self.item.icon_rect.center = self.rect.center
            if self.item.quantity == 0:
                self.item = None

    def draw_text(self, pos, text, display, color, info=False):
        font = pg.font.Font(self.font, 24)
        text_surface = font.render(text, True, color)
        if info is True:
            if text_surface.get_size()[0] > self.rect_info.w:
                self.rect_info.w += text_surface.get_size()[0]
            self.rect_info.h += 32
        display.blit(text_surface, pos)


class Equipment:

    def __init__(self, slots):

        self.pos = (0, 0)
        self.slots = slots
        self.max_slots = 40
        self.items = []
        self.equipped_items = []
        self.temp_item = ItemSlot(-1, (-256, -256), 0)
        self.l_click = False
        self.l_click_shift = False
        self.l_click_ctrl = False
        self.r_click = False
        self.r_click_shift = False
        self.r_click_ctrl = False

        self.on = False
        self.exchange = False
        self.second_eq = None
        self.second_eq_items = None

        self.bg_color = (50, 41, 71)

        spacing = 16
        size = 48
        x, y = spacing, spacing

        width = 8 * size + 9 * spacing
        height = 5 * size + 6 * spacing

        self.background_rect_0 = pg.Rect(self.pos[0], self.pos[1], width, height)
        self.opacity = 0
        s_size = pg.display.get_window_size()
        self.canvas = pg.Surface(s_size, pg.SRCALPHA)

        # exit button
        self.exit_button = Button('EXIT', self.canvas.get_rect().midbottom, 64, None, 'midbottom')

        number = 0
        for slot in range(self.slots):
            item = ItemSlot(number, (x, y), size)
            self.items.append(item)
            x += size + spacing
            if x >= width:
                x = spacing
                y += size + spacing
            number += 1

        width, height = 3 * size + 4 * spacing, 3 * size + 4 * spacing
        pos = self.background_rect_0.bottomleft
        self.background_rect_1 = pg.Rect(pos[0], pos[1] + spacing, width, height)
        x, y = self.background_rect_1.topleft
        x += spacing
        y += spacing

        for i in range(9):
            item = ItemSlot(number, (x, y), size, 'chuj')
            self.equipped_items.append(item)
            x += size + spacing
            if x >= width:
                x = spacing
                y += size + spacing
            number += 1

        self.equipped_items[3].type = 'weapon'
        self.equipped_items[5].type = 'weapon'
        self.equipped_items[6].type = 'ammo'
        self.equipped_items[8].type = 'ammo'

    def draw(self, display, camera):
        self.canvas.fill((0, 255, 0, self.opacity))
        pg.draw.rect(self.canvas, self.bg_color, self.background_rect_0, border_radius=10)
        pg.draw.rect(self.canvas, self.bg_color, self.background_rect_1, border_radius=10)

        # self.items.draw(self.canvas)

        for item in self.items:
            item.draw(self.canvas)

        for item in self.equipped_items:
            item.draw(self.canvas)

        if self.temp_item.item is not None:
            self.temp_item.draw(self.canvas)

        if self.exchange is True:
            self.second_eq.draw(display, camera)

        self.exit_button.draw(self.canvas)

        display.blit(self.canvas, (0, 0))

    def update(self):
        cursor = pg.mouse.get_pos()

        for item in self.items:
            item.update(self, cursor)

        for item in self.equipped_items:
            item.update(self, cursor)

        if self.temp_item.item is not None:
            self.temp_item.item.icon_rect.center = cursor

        if self.slots > self.max_slots:
            self.slots = self.max_slots

        if self.exchange is True:
            for item in self.second_eq.items:
                item.update(self, cursor)

            for item in self.second_eq.equipped_items:
                item.update(self, cursor)

        self.exit_button.update()
        if self.l_click is True:
            if self.exit_button.output == self.exit_button.hoover_canvas:
                self.on = False
                self.exchange = False
                self.second_eq = None

    def add_item(self, new_item, eq=False):

        found = False
        if eq is False:
            for item in self.items:
                if item.item is not None:
                    if item.item.code == new_item.code:
                        item.item.quantity += new_item.quantity
                        found = True
                        item.item.icon_rect.center = item.rect.center
                        break
            if found is False:
                for item in self.items:
                    if item.item is None:
                        item.item = new_item
                        item.item.icon_rect.center = item.rect.center
                        break
        else:
            for item in self.equipped_items:
                if item.item is not None:
                    if item.item.code == new_item.code:
                        item.item.quantity += new_item.quantity
                        item.item.icon_rect.center = item.rect.center
                        break

    def equip_weapon(self, weapon, hand):
        if hand == 'left':
            self.equipped_items[3].item = weapon
        elif hand == 'right':
            self.equipped_items[5].item = weapon

    def equip_ammo(self, ammo, hand):
        if hand == 'left':
            self.equipped_items[6].item = ammo
        elif hand == 'right':
            self.equipped_items[8].item = ammo

    def empty_backpack(self):
        for item in self.items:
            item.item = None
        for item in self.equipped_items:
            item.item = None

    def check_if_empty(self):
        empty = True
        for item in self.items:
            if item.item is not None:
                empty = False
                break
        return empty


class NPCEquipment(Equipment):

    def __init__(self):
        Equipment.__init__(self, 40)

        self.background_rect_0.topright = (pg.display.get_window_size()[0], 0)
        self.opacity = 0
        temp = pg.display.get_window_size()[0] - self.background_rect_1.w
        self.background_rect_1.x += temp
        for item in self.items:
            item.rect.x += pg.display.get_window_size()[0] - self.background_rect_0.w
            item.number += 40
            item.rect_info.x += 748
        for item in self.equipped_items:
            item.rect.x += temp
            item.number += 40
            item.rect_info.x += 748


class Chest(NPCEquipment):

    def __init__(self):
        NPCEquipment.__init__(self)
        self.equipped_items = []
        self.background_rect_1 = None

    def draw(self, display, camera):
        self.canvas.fill((0, 255, 0, self.opacity))
        pg.draw.rect(self.canvas, self.bg_color, self.background_rect_0, border_radius=10)

        for item in self.items:
            item.draw(self.canvas)

        if self.temp_item.item is not None:
            self.temp_item.draw(self.canvas)

        display.blit(self.canvas, (0, 0))
