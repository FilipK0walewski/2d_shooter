import pygame as pg
import csv, os


class Tile(pg.sprite.Sprite):

    def __init__(self, image, x, y, spritesheet, door=0, rotation=0):
        pg.sprite.Sprite.__init__(self)
        self.image = spritesheet.parse_sprite(image)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x + 16, y + 16
        self.door = door
        self.rotation = rotation


def read_csv(filename, container):
    with open(os.path.join(filename)) as data:
        data = csv.reader(data, delimiter=',')
        for row in data:
            container.append(list(row))


class TileMap:

    def __init__(self, level, spritesheet, mode='normal'):

        if mode == 'normal':
            floor_path = 'data/maps/floor_' + str(level) + '.csv'
            wall_path = 'data/maps/wall_' + str(level) + '.csv'
        else:
            floor_path = 'data/maps/e_floor_' + str(level) + '.csv'
            wall_path = 'data/maps/e_wall_' + str(level) + '.csv'

        self.tile_size = 64
        self.start_x, self.start_y = 0, 0
        self.background_color = (25, 26, 27)
        self.spritesheet = spritesheet
        self.floor = pg.sprite.Group()
        self.wall = pg.sprite.Group()
        self.door = pg.sprite.Group()
        self.door_h = pg.sprite.Group()
        self.door_v = pg.sprite.Group()

        self.player_spawn = None
        self.chest_spawn = []
        self.enemy_spawn = []
        self.npc_spawn = []
        self.camera_change = pg.sprite.Group()

        self.map_h, self.map_w = 0, 0

        self.floor_csv = []
        self.wall_csv = []

        read_csv(floor_path, self.floor_csv)
        read_csv(wall_path, self.wall_csv)
        self.load_floor()
        self.load_wall()
        self.map_surface_0 = pg.Surface((self.map_w, self.map_h))
        self.map_surface_0.fill(self.background_color)
        self.map_surface_1 = pg.Surface((self.map_w, self.map_h))
        self.map_surface_1.set_colorkey((0, 0, 0))
        self.load_map()

    def draw_map_0(self, display, camera, distance=0):
        display.blit(self.map_surface_0, (distance - camera[0], 0 - camera[1]))

    def draw_map_1(self, display, camera, distance=0):
        display.blit(self.map_surface_1, (distance - camera[0], 0 - camera[1]))

    def load_map(self):
        self.floor.draw(self.map_surface_0)
        self.door_h.draw(self.map_surface_0)
        self.door_v.draw(self.map_surface_0)
        self.wall.draw(self.map_surface_1)

    def load_floor(self):
        x, y = 0, 0
        for row in self.floor_csv:
            x = 0
            for tile in row:
                if tile == '0':
                    self.floor.add(Tile('floor_0', x * self.tile_size, y * self.tile_size, self.spritesheet))
                elif tile == '1':
                    self.floor.add(Tile('floor_2', x * self.tile_size, y * self.tile_size, self.spritesheet))
                elif tile == '2':
                    self.floor.add(Tile('floor_1', x * self.tile_size, y * self.tile_size, self.spritesheet))
                elif tile[0] == '4':
                    temp_name = 'floor_' + str(row[x - 1])
                    info_list = []
                    info = ''
                    for n in tile:
                        if n == '_':
                            info_list.append(info)
                            info = ''
                        else:
                            info += n
                    info_list.append(info)
                    rect = pg.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                    self.floor.add(Tile(temp_name, x * self.tile_size, y * self.tile_size, self.spritesheet))
                    enemy_dict = {
                        "rect": rect,
                        "angle": int(info_list[2]),
                        "weapon": int(info_list[1])
                    }
                    self.enemy_spawn.append(enemy_dict)
                elif tile == '5':
                    temp_name = 'floor_' + str(row[x - 1])
                    self.floor.add(Tile(temp_name, x * self.tile_size, y * self.tile_size, self.spritesheet))
                    self.chest_spawn.append(pg.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size))
                elif tile == '6':
                    self.floor.add(Tile('floor_0', x * self.tile_size, y * self.tile_size, self.spritesheet))
                    self.npc_spawn.append(pg.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size))
                elif tile == '10':
                    temp_name = 'floor_' + str(row[x - 1])
                    self.floor.add(Tile(temp_name, x * self.tile_size, y * self.tile_size, self.spritesheet))
                    self.player_spawn = pg.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                elif tile == '23':
                    temp_name = 'floor_' + str(row[x - 1])
                    self.floor.add(Tile(temp_name, x * self.tile_size, y * self.tile_size, self.spritesheet))
                    self.camera_change.add(Tile(temp_name, x * self.tile_size, y * self.tile_size, self.spritesheet))

                elif tile[0] == 'v' or tile[0] == 'h':
                    self.door.add(Tile('floor_0', x * self.tile_size, y * self.tile_size, self.spritesheet, tile))
                    if tile[0] == 'v':
                        self.door_v.add(Tile('floor_0', x * self.tile_size, y * self.tile_size, self.spritesheet, tile))
                    if tile[0] == 'h':
                        self.door_h.add(Tile('floor_0', x * self.tile_size, y * self.tile_size, self.spritesheet, tile))
                elif tile == '29':
                    self.floor.add(Tile('stairs_0', x * self.tile_size, y * self.tile_size, self.spritesheet, 0, 90))
                x += 1
            y += 1

        self.map_w, self.map_h = x * self.tile_size, y * self.tile_size

    def load_wall(self):

        x, y = 0, 0
        for row in self.wall_csv:
            x = 0
            for tile in row:
                if tile == '6':
                    self.wall.add(Tile('wall_h', x * self.tile_size, y * self.tile_size - 11, self.spritesheet))
                elif tile == '7':
                    self.wall.add(Tile('wall_v', x * self.tile_size - 11, y * self.tile_size, self.spritesheet))
                elif tile == '8':
                    self.wall.add(Tile('wall_h', x * self.tile_size, y * self.tile_size + 53, self.spritesheet))
                elif tile == '9':
                    self.wall.add(Tile('wall_v', x * self.tile_size + 53, y * self.tile_size, self.spritesheet))

                elif tile == '11':
                    self.wall.add(Tile('corner', x * self.tile_size - 11, y * self.tile_size - 11, self.spritesheet))
                elif tile == '12':
                    self.wall.add(Tile('wall_v', x * self.tile_size - 11, y * self.tile_size, self.spritesheet))
                    self.wall.add(Tile('wall_h', x * self.tile_size, y * self.tile_size - 11, self.spritesheet))
                    self.wall.add(Tile('corner', x * self.tile_size - 11, y * self.tile_size - 11, self.spritesheet))
                elif tile == '13':
                    self.wall.add(Tile('wall_v', x * self.tile_size + 53, y * self.tile_size, self.spritesheet))
                    self.wall.add(Tile('wall_h', x * self.tile_size, y * self.tile_size - 11, self.spritesheet))
                    self.wall.add(Tile('corner', x * self.tile_size + 53, y * self.tile_size - 11, self.spritesheet))
                elif tile == '15':
                    self.wall.add(Tile('wall_v', x * self.tile_size - 11, y * self.tile_size, self.spritesheet))
                    self.wall.add(Tile('wall_h', x * self.tile_size, y * self.tile_size + 53, self.spritesheet))
                    self.wall.add(Tile('corner', x * self.tile_size - 11, y * self.tile_size + 53, self.spritesheet))
                elif tile == '14':
                    self.wall.add(Tile('wall_v', x * self.tile_size + 53, y * self.tile_size, self.spritesheet))
                    self.wall.add(Tile('wall_h', x * self.tile_size, y * self.tile_size + 53, self.spritesheet))
                    self.wall.add(Tile('corner', x * self.tile_size + 53, y * self.tile_size + 53, self.spritesheet))

                elif tile == '18':
                    self.wall.add(Tile('wall_h', x * self.tile_size, y * self.tile_size - 11, self.spritesheet))
                    self.wall.add(Tile('corner', x * self.tile_size + 53, y * self.tile_size - 11, self.spritesheet))
                elif tile == '19':
                    self.wall.add(Tile('wall_v', x * self.tile_size - 11, y * self.tile_size, self.spritesheet))
                    self.wall.add(Tile('corner', x * self.tile_size - 11, y * self.tile_size - 11, self.spritesheet))
                elif tile == '21':
                    self.wall.add(Tile('wall_v', x * self.tile_size + 53, y * self.tile_size, self.spritesheet))
                    self.wall.add(Tile('corner', x * self.tile_size + 53, y * self.tile_size - 11, self.spritesheet))
                elif tile == '24':
                    self.wall.add(Tile('wall_h', x * self.tile_size, y * self.tile_size - 11, self.spritesheet))
                    self.wall.add(Tile('corner', x * self.tile_size - 11, y * self.tile_size - 11, self.spritesheet))
                elif tile == '25':
                    self.wall.add(Tile('wall_v', x * self.tile_size - 11, y * self.tile_size, self.spritesheet))
                    self.wall.add(Tile('corner', x * self.tile_size - 11, y * self.tile_size + 53, self.spritesheet))
                x += 1
            y += 1
        self.map_w, self.map_h = x * self.tile_size + 32, y * self.tile_size + 32
