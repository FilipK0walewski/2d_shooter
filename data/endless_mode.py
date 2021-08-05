from data.game import Game, read_border
from data.characters import Human, Enemy
from data.images import Spritesheet
from data.furnitures import Storage
from data.map import TileMap
from data.camera import Follow, Border, Auto, Camera, CursorBorder
import pygame as pg
import json
import random


class EndlessMode(Game):

    def __init__(self, window):
        Game.__init__(self, window, 'endless')

        self.size = pg.display.get_window_size()
        self.player = Human((0, 0))
        level_number = 1
        with open('data/maps/info.json') as f:
            level_info = json.load(f)
        f.close()

        self.canvas_w = self.size[1] + 512
        self.levels = []
        map_sheet = Spritesheet('data/assets/sprites/maps/tileset.png')

        for i in range(level_number):
            level_map = TileMap(i, map_sheet, 'endless')
            chest_pos = level_map.chest_spawn
            furnitures = []
            for chest in chest_pos:
                storage = Storage(chest.center)
                furnitures.append(storage)

            border = read_border(level_info['levels']['e_level_' + str(i)]['borders'], level_map.map_w, level_map.map_h)
            level = {'map': level_map,
                     'border': border,
                     'camera': level_info['levels']['e_level_' + str(i)]['camera'],
                     'canvas_0': pg.Surface((self.canvas_w, level_map.map_h), pg.SRCALPHA),
                     'canvas_1': pg.Surface((self.canvas_w, level_map.map_h), pg.SRCALPHA),
                     'dist': [0, self.canvas_w],
                     'npc': [],
                     'enemies': [],
                     'furnitures': furnitures,
                     'backpack': self.player.backpack,
                     'completed': False
                     }
            self.levels.append(level)

        self.current_level = self.levels[self.level_number]
        if self.current_level['map'].player_spawn is not None:
            self.player.position.x = self.current_level['map'].player_spawn.x
            self.player.position.y = self.current_level['map'].player_spawn.y
        self.player.start_pos = (self.player.position.x, self.player.position.y)

        # camera
        self.camera = Camera(self.player, self.aimer)
        self.follow = Follow(self.camera, self.player)
        self.border = Border(self.camera, self.player)
        self.cursor_border = CursorBorder(self.camera, self.player, self.aimer)
        self.auto = Auto(self.camera, self.player)
        self.camera.set_method(self.border)
        self.mouse_movement = False
        self.move = False

        # time
        self.tick = pg.time.get_ticks()

        # skip
        self.skip_counter = 0
        distance = self.current_level['map'].map_w - self.size[0]
        temp = distance / 64
        self.check_dist = int(temp) * 64 - 256
        self.constant_dist = self.check_dist - 256 - 64
        self.distance_x = 0

        # test
        # print(self.canvas_w)

        # laser
        self.laser = False

    def spawn_enemy(self):
        y = random.randint(64, self.size[1] - 64)
        x = self.camera.offset.x + self.size[0] + 64
        enemy = Enemy((x, y), 90, 0, 3)
        self.current_level['enemies'].append(enemy)

    def skip_method(self):
        self.skip_counter += 1
        if self.skip_counter == 20:
            self.camera.set_method(self.border)
            self.current_level['camera'] = 'static'
        else:
            self.distance_x += self.constant_dist
            self.check_dist += self.constant_dist
            for wall in self.current_level['map'].wall.sprites():
                wall.rect.x += self.constant_dist

            # self.canvas_n = (self.canvas_n + 1) % 2
            # self.current_level['dist']

    def update(self):

        self.aimer.update(self.camera.offset)

        self.player.update(self.delta_time, self.aimer.true_pos, self.camera.offset, self.current_level['map'].wall,
                           self.current_level['enemies'], self.particles)

        # ENDLESS MODE #################################################################################################

        if self.current_level['camera'] == 'dynamic':

            now = pg.time.get_ticks()
            if now - self.tick >= 2500:
                self.spawn_enemy()
                self.tick = now
            if self.camera.offset.x >= self.check_dist:
                self.skip_method()
            if self.camera.offset.x > self.current_level['dist'][0] + self.current_level['canvas_0'].get_width():
                self.current_level['canvas_0'].fill((0, 0, 0, 0))
                self.current_level['dist'][0] += 2 * self.canvas_w
            if self.camera.offset.x > self.current_level['dist'][1] + self.current_level['canvas_1'].get_width():
                self.current_level['canvas_1'].fill((0, 0, 0, 0))
                self.current_level['dist'][1] += 2 * self.canvas_w

            for enemy in self.current_level['enemies']:
                if enemy.position.x <= self.camera.offset.x + 92:
                    if enemy.dead is False:
                        enemy.take_damage(100, self.particles, enemy.angle)
                    if enemy.position.x < self.camera.offset.x + 256:
                        del enemy

            if self.player.position.x <= self.camera.offset.x + 92:
                self.player.take_damage(100, self.particles, 90)
        else:
            temp = pg.sprite.spritecollide(self.player, self.current_level['map'].camera_change, False)
            if len(temp) != 0:
                self.laser = True
                self.current_level['camera'] = 'dynamic'
                self.camera.set_method(self.auto)

        ################################################################################################################

        if self.player.backpack.on is False:
            self.camera.scroll(self.current_level['border'], True, 2)

            for enemy in self.current_level['enemies']:
                enemy.update(self.delta_time, self.player.position, self.camera.offset, self.current_level['map'].wall,
                             self.player, self.particles)

            for particle in self.particles:
                particle.update(self.delta_time)
                if len(particle.particles) == 0:
                    self.particles.remove(particle)
        else:
            self.player.change_weapons()

        # transition
        if self.opacity != 0:
            self.opacity -= 3
            self.transition_canvas.set_alpha(self.opacity)
            self.player._move = False
        else:
            self.player._move = True

    def reset_level(self):

        self.particles = []

        self.player.hp = 100
        self.player.dead = False
        self.player.backpack.empty_backpack()
        self.player.velocity.x = 0
        self.player.velocity.y = 0
        self.player.position.x = self.player.start_pos[0]
        self.player.position.y = self.player.start_pos[1]
        self.player.change_weapons()

        self.opacity = 255

        self.current_level['enemies'] = []
        self.current_level['canvas_0'].fill((0, 0, 0, 0))
        self.current_level['canvas_1'].fill((0, 0, 0, 0))

        self.camera.set_method(self.border)
        self.current_level['camera'] = 'static'
        self.distance_x = 0

        self.check_dist = self.constant_dist + 64
        for wall in self.current_level['map'].wall.sprites():
            wall.rect.x -= self.constant_dist * self.skip_counter
        self.skip_counter = 0

        self.current_level['dist'] = [0, self.canvas_w]
        self.laser = False
