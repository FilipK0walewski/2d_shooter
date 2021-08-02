import pygame as pg
from data.characters import Human, Enemy, NPC
from data.weapons import Aimer
from data.furnitures import Storage
from data.images import Spritesheet
from data.map import TileMap
from data.camera import Camera, Follow, Border, Auto, CursorBorder
import time, json


class Game:

    def __init__(self, window, mode='normal'):

        pg.init()
        self.clock = pg.time.Clock()
        self.previous_time = time.time()
        self.delta_time = 0
        self.FPS = 120

        self.playing = False
        self.game_pause = False

        # colors
        self.background_color = (25, 26, 27)
        self.opacity = 0
        self.transition = False

        # window
        self.window = window
        self.size = pg.display.get_window_size()
        self.display = pg.Surface(self.size)
        # self.display.set_colorkey((0, 0, 0))
        self.transition_canvas = pg.Surface(self.size, pg.SRCALPHA)
        self.transition_canvas.fill(self.background_color)
        self.transition_canvas.set_alpha(0)

        # player

        self.aimer = Aimer()
        self.player = Human((1000, 1900))

        # map ##########################################################################################################
        if mode == 'normal':
            level_number = 4
            with open('data/maps/info.json') as f:
                level_info = json.load(f)
            f.close()
            self.levels = []
            map_sheet = Spritesheet('data/assets/sprites/maps/tileset.png')

            for i in range(level_number):
                level_map = TileMap(i, map_sheet)
                chest_pos = level_map.chest_spawn
                enemies_info = level_map.enemy_spawn
                npc_pos = level_map.npc_spawn
                furnitures = []
                enemies = []
                npc = []
                for chest in chest_pos:
                    storage = Storage(chest.center)
                    furnitures.append(storage)
                for enemy in enemies_info:
                    e = Enemy(enemy['rect'].center, enemy['angle'], enemy['weapon'], i)
                    enemies.append(e)
                for np in npc_pos:
                    n = NPC(np.center)
                    npc.append(n)
                border = read_border(level_info['levels']['level_' + str(i)]['borders'], level_map.map_w, level_map.map_h)
                level = {'map': level_map,
                         'border': border,
                         'camera': level_info['levels']['level_' + str(i)]['camera'],
                         'canvas_0': pg.Surface((level_map.map_w, level_map.map_h), pg.SRCALPHA),
                         'canvas_1': None,
                         'dist': [0, 0],
                         'npc': npc,
                         'enemies': enemies,
                         'furnitures': furnitures,
                         'backpack': self.player.backpack,
                         'completed': False
                         }
                self.levels.append(level)
            self.level_number = 0
            self.current_level = self.levels[self.level_number]
        else:
            self.level_number = 0
            self.levels = []

        self.travel = True
        self.reset = False

        # camera
        self.camera_to_mouse = False
        self.camera = Camera(self.player, self.aimer)
        self.follow = Follow(self.camera, self.player)
        self.border = Border(self.camera, self.player)
        self.cursor_border = CursorBorder(self.camera, self.player, self.aimer)
        self.auto = Auto(self.camera, self.player)
        self.camera.set_method(self.border)
        self.mouse_movement = False

        # mouse
        pg.mouse.set_visible(False)

        # particles
        self.particles = []

        # endless mode
        self.distance_x = 0
        self.laser = False

    def main_loop(self):
        while self.playing is True:
            self.check_input()
            self.limit_framerate()
            self.update()
            self.draw()
            self.reset_buttons()

    def limit_framerate(self):
        self.clock.tick(self.FPS)
        now = time.time()
        self.delta_time = now - self.previous_time
        self.previous_time = now
        self.delta_time *= 60

    def update(self):

        # test

        self.aimer.update(self.camera.offset)

        if self.reset is False:
            temp = pg.sprite.spritecollide(self.player, self.current_level['map'].door, False)
            if len(temp) != 0 and self.travel is True:
                self.travel = False
                self.change_level(temp)
            if self.travel is False and len(temp) == 0:
                self.travel = True
        else:
            self.reset = False

        if self.player.backpack.on is False:
            if self.camera_to_mouse is False:
                self.camera.scroll(self.current_level['border'])
            else:
                if self.mouse_movement is True:
                    border = [0, self.current_level['map'].map_h, 0, self.current_level['map'].map_w]
                    i = 0
                    for b in self.current_level['border']:
                        if b != -1:
                            border[i] = b
                        i += 1
                    self.camera.scroll(border)
        else:
            self.player.change_weapons()

        if self.game_pause is False:
            self.player.update(self.delta_time, self.aimer.true_pos, self.camera.offset, self.current_level['map'].wall,
                               self.current_level['enemies'], self.particles)

            if self.current_level['completed'] is False:
                completed = True
                for enemy in self.current_level['enemies']:
                    if enemy.dead is False:
                        completed = False
                    enemy.update(self.delta_time, self.player.position, self.camera.offset, self.current_level['map'].wall, self.player, self.particles)
                if completed is True:
                    self.current_level['completed'] = True

            for particle in self.particles:
                particle.update(self.delta_time)
                if len(particle.particles) == 0:
                    self.particles.remove(particle)

        self.game_pause = False
        for npc in self.current_level['npc']:
            npc.update(self.delta_time, self.player.position, self.camera.offset, self.current_level['map'].wall, [], self.particles)
            if npc.dialogue.talk is True:
                self.game_pause = True
            if npc.dialogue.show_eq is True:
                self.player.backpack.second_eq = npc.backpack
                self.player.backpack.exchange = True
                self.player.backpack.on = True
                npc.dialogue.show_eq = False

        # transition
        if self.opacity != 0:
            self.opacity -= 3
            self.transition_canvas.set_alpha(self.opacity)
            self.player._move = False
        else:
            self.player._move = True

    def draw(self):

        self.display.fill(self.background_color)
        self.current_level['map'].draw_map_0(self.display, self.camera.offset, self.distance_x)

        self.display.blit(self.current_level['canvas_0'], (self.current_level['dist'][0] - self.camera.offset.x, 0 - self.camera.offset.y))

        if self.current_level['canvas_1'] is not None:
            self.display.blit(self.current_level['canvas_1'], (self.current_level['dist'][1] - self.camera.offset.x, 0 - self.camera.offset.y))

        for furniture in self.current_level['furnitures']:
            furniture.draw(self.display, self.camera.offset)

        self.player.draw(self.display, self.camera.offset)
        self.current_level['map'].draw_map_1(self.display, self.camera.offset, self.distance_x)

        for particle in self.particles:
            if particle.type == 'const':
                particle.draw(self.current_level['canvas_0'], self.current_level['canvas_1'], pg.math.Vector2(0, 0), self.current_level['dist'])
            if particle.type == 'temp':
                particle.draw(self.display, None, self.camera.offset, 0)

        for enemy in self.current_level['enemies']:
            if enemy.dead is False:
                enemy.draw(self.display, self.camera.offset)
            elif enemy.dead is True and enemy.dead_dead is False:
                if self.current_level['canvas_1'] is not None:
                    if self.current_level['canvas_0'].get_width() + self.current_level['dist'][0] >= enemy.rect.x >= self.current_level['dist'][0] or\
                            self.current_level['canvas_0'].get_width() + self.current_level['dist'][0] >= enemy.rect.x + enemy.rect.w >= self.current_level['dist'][0]:
                        enemy.draw(self.current_level['canvas_0'], pg.math.Vector2(0, 0), self.current_level['dist'][0])
                    if self.current_level['canvas_1'].get_width() + self.current_level['dist'][1] >= enemy.rect.x >= self.current_level['dist'][1] or \
                            self.current_level['canvas_1'].get_width() + self.current_level['dist'][1] >= enemy.rect.x + enemy.rect.w >= self.current_level['dist'][1]:
                        enemy.draw(self.current_level['canvas_1'], pg.math.Vector2(0, 0), self.current_level['dist'][1])
                else:
                    enemy.draw(self.current_level['canvas_0'], pg.math.Vector2(0, 0), 0)

        for npc in self.current_level['npc']:
            npc.draw(self.display, self.camera.offset)

        if self.player.backpack.on is True:
            self.player.backpack.draw(self.display, self.camera.offset)

        if self.laser is True:
            pg.draw.line(self.display, (199, 14, 32), (32, 0), (32, self.size[1]), 16)

        self.aimer.draw(self.display)

        self.window.blit(self.display, (0, 0))
        if self.opacity != 0:
            self.window.blit(self.transition_canvas, (0, 0))
        pg.display.flip()

    def change_level(self, level):

        self.opacity = 255
        self.transition_canvas.set_alpha(self.opacity)

        self.level_number = int(level[0].door[1])
        self.current_level = self.levels[self.level_number]

        if level[0].door[0] == 'h':
            doors = self.current_level['map'].door_h
            self.player.position.x = doors.sprites()[0].rect.x
        elif level[0].door[0] == 'v':
            doors = self.current_level['map'].door_v
            self.player.position.y = doors.sprites()[0].rect.y

        self.player.velocity.x = 0
        self.player.velocity.y = 0
        self.player.start_pos = (self.player.position.x, self.player.position.y)
        self.current_level['backpack'] = self.player.backpack

        if self.current_level['camera'] == 'static':
            self.camera.set_method(self.border)
        if self.current_level['camera'] == 'dynamic':
            self.camera.offset.x = 0
            self.camera.set_method(self.auto)

    def reset_level(self):

        self.travel = False
        self.reset = True
        self.particles = []

        self.player.hp = 100
        self.player.dead = False
        self.player.backpack = self.current_level['backpack']
        self.player.velocity.x = 0
        self.player.velocity.y = 0
        self.player.position.x = self.player.start_pos[0]
        self.player.position.y = self.player.start_pos[1]
        self.player.change_weapons()

        self.opacity = 255

        self.player.velocity = pg.math.Vector2(0, 0)

        if self.current_level['completed'] is False:

            self.current_level['canvas_0'].fill((0, 0, 0, 0))

            for enemy in self.current_level['enemies']:
                enemy.original_img = enemy.alive_image
                enemy.target = None
                enemy.weapon_0.shoot = False
                enemy.weapon_1.shoot = False
                enemy.position.x = enemy.start_pos.x
                enemy.position.y = enemy.start_pos.y

                enemy.hp = 100
                enemy.dead = False
                enemy.dead_dead = False

                empty = enemy.backpack.check_if_empty()
                if empty is True:
                    enemy.backpack.add_item(enemy.item)

                if enemy.weapon == 1:
                    enemy.generate_weapons()
                    enemy.change_weapons()
                    enemy.generate_ammo()

            for chest in self.current_level['furnitures']:
                chest.store.empty_backpack()
                chest.store.add_item(chest.items['pistol'])
                chest.store.add_item(chest.items['pistol_ammo'])

    def check_input(self):

        for event in pg.event.get():

            if event.type == pg.QUIT:
                self.playing = False

            if event.type == pg.MOUSEMOTION:
                dx, dy = event.rel
                speed = (dx ** 2 + dy ** 2) ** (1 / 2)  # Pythagoras theorem.
                if speed >= .5:
                    self.mouse_movement = True

            if event.type == pg.MOUSEBUTTONDOWN:

                if self.player.backpack.on is False:

                    if event.button == 1:
                        self.player.weapon_0.shoot = True
                    if event.button == 3:
                        self.player.weapon_1.shoot = True

                if self.game_pause is True:

                    for npc in self.current_level['npc']:
                        npc.dialogue.click = True

                else:

                    if event.button == 1:
                        self.player.backpack.l_click = True
                    if event.button == 1 and pg.key.get_mods() & pg.KMOD_SHIFT:
                        self.player.backpack.l_click_shift = True
                    if event.button == 1 and pg.key.get_mods() & pg.KMOD_CTRL:
                        self.player.backpack.l_click_ctrl = True
                    if event.button == 3:
                        self.player.backpack.r_click = True
                    if event.button == 3 and pg.key.get_mods() & pg.KMOD_SHIFT:
                        self.player.backpack.r_click_shift = True
                    if event.button == 3 and pg.key.get_mods() & pg.KMOD_CTRL:
                        self.player.backpack.r_click_ctrl = True

            if event.type == pg.MOUSEBUTTONUP:
                if self.player.backpack.on is False:
                    if event.button == 1:
                        self.player.weapon_0.shoot = False
                    if event.button == 3:
                        self.player.weapon_1.shoot = False

            if event.type == pg.KEYDOWN:
                # ESCAPE ###############################################################################################
                if event.key == pg.K_ESCAPE:
                    if self.playing is True:
                        self.player.velocity.x = 0
                        self.player.velocity.y = 0
                        self.game_pause = True
                        self.playing = False
                    else:
                        self.playing = True

                # test
                if event.key == pg.K_z:
                    self.camera.set_method(self.cursor_border)
                    self.camera_to_mouse = True

                if event.key == pg.K_r:
                    self.reset_level()

                if event.key == pg.K_p:
                    self.current_level['canvas_0'].fill((0, 0, 0, 0))
                    for particle in self.particles:
                        print(particle, ' ', len(particle.particles))

                if event.key == pg.K_i:
                    if self.player.backpack.second_eq is None:
                        self.game_pause = not self.game_pause
                        temp = self.player.backpack.on
                        self.player.backpack.on = not temp

                if event.key == pg.K_l:
                    """
                    print(' ')
                    for item in self.player.backpack.items:
                        if item.item is None:
                            print('number: ', item.number, ' ', item.item)
                        else:
                            print('number: ', item.number, ' name: ', item.item.name, ' quantity: ', item.item.quantity)
                    if self.player.backpack.temp_item.item is None:
                        print('temp item: ', self.player.backpack.temp_item.item)
                    else:
                        print('temp item : -1 name: ', self.player.backpack.temp_item.item.name, 'quantity: ', self.player.backpack.temp_item.item.quantity)
                    """
                    for enemy in self.current_level['enemies']:
                        for item in enemy.backpack.equipped_items:
                            print('slot', item.number, ':   ', item.item)

                if event.key == pg.K_e:
                    for enemy in self.current_level['enemies']:
                        if enemy.dead is True:
                            if abs(enemy.rect.x - self.player.rect.x) < 128 and enemy.rect.collidepoint(self.aimer.true_pos):
                                enemy.change_weapons()
                                temp = self.player.backpack.on
                                self.player.backpack.on = not temp
                                self.player.backpack.exchange = not temp
                                if temp is False:
                                    self.player.backpack.second_eq = enemy.backpack
                                else:
                                    self.player.backpack.second_eq = None
                                break

                    for npc in self.current_level['npc']:
                        if abs(npc.rect.x - self.player.rect.x) < 128 and npc.rect.collidepoint(self.aimer.true_pos):
                            temp = npc.dialogue.talk
                            npc.dialogue.talk = not temp

                    for furniture in self.current_level['furnitures']:
                        if furniture.rect.collidepoint(self.aimer.true_pos):
                            if abs(furniture.rect.y - self.player.rect.y) < 128 and abs(furniture.rect.x - self.player.rect.x) < 128:
                                temp = self.player.backpack.on
                                self.player.backpack.on = not temp
                                self.player.backpack.exchange = not temp
                                if temp is False:
                                    self.player.backpack.second_eq = furniture.store
                                else:
                                    self.player.backpack.second_eq = None
                                break

                if event.key == pg.K_d:
                    self.player.right_key = True
                if event.key == pg.K_a:
                    self.player.left_key = True
                if event.key == pg.K_w:
                    self.player.up_key = True
                if event.key == pg.K_s:
                    self.player.down_key = True

            if event.type == pg.KEYUP:
                if event.key == pg.K_z:
                    self.camera_to_mouse = False
                    if self.current_level['camera'] == 'static':
                        self.camera.set_method(self.border)
                    if self.current_level['camera'] == 'dynamic':
                        self.camera.set_method(self.auto)

                if event.key == pg.K_d:
                    self.player.right_key = False
                if event.key == pg.K_a:
                    self.player.left_key = False
                if event.key == pg.K_w:
                    self.player.up_key = False
                if event.key == pg.K_s:
                    self.player.down_key = False

    def reset_buttons(self):
        self.player.backpack.l_click = False
        self.player.backpack.l_click_shift = False
        self.player.backpack.l_click_ctrl = False
        self.player.backpack.r_click = False
        self.player.backpack.r_click_shift = False
        self.player.backpack.r_click_ctrl = False
        self.mouse_movement = False

        for npc in self.current_level['npc']:
            npc.dialogue.click = False


def read_border(border, map_w, map_h):
    new_border = []
    if border[0] == 0:
        new_border.append(-1)
    elif border[0] == 1:
        new_border.append(192)

    if border[1] == 0:
        new_border.append(-1)
    elif border[1] == 1:
        new_border.append(map_h - 192)

    if border[2] == 0:
        new_border.append(-1)
    elif border[2] == 1:
        new_border.append(192)

    if border[3] == 0:
        new_border.append(-1)
    elif border[3] == 1:
        new_border.append(map_w - 192)

    return new_border
