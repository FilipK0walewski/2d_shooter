from time import time
from network import Network
from data.game import Game, read_border
from data.characters import Human, Enemy
from data.images import Spritesheet
from data.furnitures import Storage
from data.map import TileMap
from data.camera import Follow, Border, Auto, Camera, CursorBorder
import pygame as pg
import json


class MultiplayerMode(Game):

    def __init__(self, window):
        super().__init__(window, 'multiplayer')

        # server
        self.n = Network()

        # player
        # start_pos = read_pos(self.n.get_pos())
        self.player = Human(self.n.get_player_pos(), self.n.get_player_id())

        # other player
        self.other_players = []

        # load map
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

            border = read_border(level_info['levels']['m_level_' + str(i)]['borders'], level_map.map_w, level_map.map_h)
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
        # if self.current_level['map'].player_spawn is not None:
        #     self.player.position.x = self.current_level['map'].player_spawn.x
        #     self.player.position.y = self.current_level['map'].player_spawn.y
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
    
    def update_users_positions(self):
        self.n.send(self.player.get_data_for_server())
        # received_data = self.n.send(self.player.get_data_for_server())
        # temp_n = 0
        # print(f'received data: {received_data}, {type(received_data)}')

        # if type(received_data) == 'dict':
        #     if received_data['temp_id'] != self.player['temp_id']:
        #         for player in self.other_players:
        #             if player.temp_id == received_data['temp_id']:
        #                 player.update_data(received_data)
        #                 break

    def main_loop(self):
        while self.playing is True:
            self.update_users_positions()
            self.check_input()
            self.limit_framerate()
            self.update()
            self.draw()
            self.reset_buttons()