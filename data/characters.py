import pygame as pg
import math, time, json, random
from data.equipment import Equipment, NPCEquipment, Item
from data.weapons import Fist, Pistol, Shotgun, Uzi
from data.images import Spritesheet
from data.dialogue import DialogueWindow
from data.particles import Pool


with open('data/assets/sprites/items.json') as f:
    items = json.load(f)
f.close()


class Human(pg.sprite.Sprite):

    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self)

        spritesheet = Spritesheet('data/assets/sprites/characters.png')

        self.image = spritesheet.parse_sprite('player_head')
        self.alive_image = spritesheet.parse_sprite('artur_head')
        self.dead_image = spritesheet.parse_sprite('player_head')
        fist_0_image = spritesheet.parse_sprite('player_left_fist')
        self.fist_0 = Fist(fist_0_image)
        fist_1_image = spritesheet.parse_sprite('player_left_fist')
        self.fist_1 = Fist(fist_1_image)

        self.rect = self.image.get_rect()
        self.original_img = self.image
        self.original_rect = self.original_img.get_rect()
        self.true_position = pg.math.Vector2(pg.display.get_window_size())
        self.true_position *= .5

        # circe?
        self.start_pos = pos
        self.radius = self.rect.w * .5
        self.rect.center = pos
        self.left_key, self.right_key, self.up_key, self.down_key = False, False, False, False

        self.friction = -.08
        self.speed = 1
        self.position = pg.math.Vector2(self.rect.center[0], self.rect.center[1])
        self.velocity = pg.math.Vector2(0, 0)
        self.acceleration = pg.math.Vector2(0, 0)

        # weapons
        self.weapon_0 = self.fist_0
        self.weapon_0_pos = (0, 0)
        self.weapon_1 = self.fist_1
        self.weapon_1_pos = (0, 0)

        # eq
        self.backpack = Equipment(8)

        # stats
        self._move = True
        self.dead = False
        self.dead_dead = False
        self.last_angle = None
        self.death_time = 0
        self.hp = 100

    def draw(self, display, camera, dist=0):

        if self.weapon_0 is not None:
            self.weapon_0.draw(display, camera, dist)
        if self.weapon_1 is not None:
            self.weapon_1.draw(display, camera, dist)

        display.blit(self.image, (self.rect.x - dist - camera.x, self.rect.y - camera.y))

        """
        pg.draw.rect(display, (248, 227, 196), self.rect, 2)
        pg.draw.circle(display, (248, 227, 196), self.rect.center, self.radius, 2)
        pg.draw.line(display, (0, 0, 255), self.rect.center, self.weapon_0_pos)
        pg.draw.line(display, (0, 255, 255), self.rect.center, self.weapon_1_pos)
        """

    def update(self, delta_time, target, camera, wall, enemies, particles):

        if self.dead is True:
            self.image = self.dead_image
        else:
            if self.backpack.on is True:
                self.backpack.update()
            else:
                if self._move is True:
                    self.horizontal_movement(delta_time)
                    self.horizontal_collision(wall)
                    self.vertical_movement(delta_time)
                    self.vertical_collision(wall)
                self.rotation(target)

                if self.weapon_0 is not None:
                    self.weapon_0.update(self.weapon_0_pos, delta_time, target, wall, enemies, particles, self.backpack.equipped_items[6])
                if self.weapon_1 is not None:
                    self.weapon_1.update(self.weapon_1_pos, delta_time, target, wall, enemies, particles, self.backpack.equipped_items[8])

    def horizontal_movement(self, delta_time):
        self.acceleration.x = 0
        if self.right_key is True:
            self.acceleration.x += self.speed * delta_time
        elif self.left_key is True:
            self.acceleration.x -= self.speed * delta_time

        self.acceleration.x += self.velocity.x * self.friction
        if abs(self.velocity.x) < 10:
            self.velocity.x += self.acceleration.x * delta_time
            if abs(self.velocity.x) < .25:
                self.velocity.x = 0

        self.position.x += self.velocity.x * delta_time
        self.rect.center = self.position

    def vertical_movement(self, delta_time):
        self.acceleration.y = 0
        if self.up_key is True:
            self.acceleration.y -= self.speed * delta_time
        elif self.down_key is True:
            self.acceleration.y += self.speed * delta_time

        self.acceleration.y += self.velocity.y * self.friction
        if abs(self.velocity.y) < 10:
            self.velocity.y += self.acceleration.y * delta_time
            if abs(self.velocity.y) < .25:
                self.velocity.y = 0

        self.position.y += self.velocity.y * delta_time + (self.acceleration.y * .5) * (delta_time * delta_time)
        self.rect.center = self.position

    def horizontal_collision(self, wall):
        self.original_rect.center = self.position
        hit_list = []

        for tile in wall:
            if tile.rect.colliderect(self.original_rect):
                hit_list.append(tile)

        for tile in hit_list:
            if self.velocity.x > 0:
                self.position.x = tile.rect.left - self.radius
                self.rect.center = self.position
            if self.velocity.x < 0:
                self.position.x = tile.rect.right + self.radius
                self.rect.center = self.position

    def vertical_collision(self, wall):
        self.original_rect.center = self.position
        hit_list = []

        for tile in wall:
            if tile.rect.colliderect(self.original_rect):
                hit_list.append(tile)

        for tile in hit_list:
            if self.velocity.y > 0:
                self.position.y = tile.rect.top - self.radius
                self.rect.center = self.position
            if self.velocity.y < 0:
                self.position.y = tile.rect.bottom + self.radius
                self.rect.center = self.position

    def rotation(self, point):
        delta_x = point[0] - self.rect.center[0]
        delta_y = point[1] - self.rect.center[1]
        radians = math.atan2(delta_y, delta_x)
        angle = -(radians * 180) / math.pi - 90

        x_0 = self.rect.center[0] + math.cos(radians - math.pi * .5) * 32
        y_0 = self.rect.center[1] + math.sin(radians - math.pi * .5) * 32
        x_1 = self.rect.center[0] + math.cos(radians + math.pi * .5) * 32
        y_1 = self.rect.center[1] + math.sin(radians + math.pi * .5) * 32

        self.weapon_0_pos = (x_0, y_0)
        self.weapon_1_pos = (x_1, y_1)

        self.image = pg.transform.rotate(self.original_img, angle)
        x, y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def change_weapons(self):

        if self.backpack.equipped_items[3].item is not None:
            self.weapon_0 = self.backpack.equipped_items[3].item
        else:
            self.weapon_0 = self.fist_0

        if self.backpack.equipped_items[5].item is not None:
            self.weapon_1 = self.backpack.equipped_items[5].item
        else:
            self.weapon_1 = self.fist_1

    def take_damage(self, damage, particles, angle):
        self.hp -= damage
        if self.hp <= 0:
            self.dead = True
            self.last_angle = angle
            particles.append(Pool(self.rect))


########################################################################################################################


class Enemy(Human):

    def __init__(self, pos, angle, weapon, level):
        Human.__init__(self, pos)
        pg.sprite.Sprite.__init__(self)

        spritesheet = Spritesheet('data/assets/sprites/characters.png')
        self.image = spritesheet.parse_sprite('enemy_0_head')
        self.alive_image = spritesheet.parse_sprite('enemy_0_head')
        self.dead_image = spritesheet.parse_sprite('enemy_0_dead')
        fist_0_image = spritesheet.parse_sprite('enemy_0_left_fist')
        fist_1_image = spritesheet.parse_sprite('enemy_0_right_fist')
        self.fist_0 = Fist(fist_0_image)
        self.fist_1 = Fist(fist_1_image)
        self.rect = self.image.get_rect()
        self.original_img = self.image

        # positioning ##############################################################################################

        self.start_pos = pg.math.Vector2(pos)
        self.start_angle = angle
        self.angle = angle
        if angle == 90 or angle == 270:
            self.pi = math.pi
        else:
            self.pi = math.pi * .5

        ############################################################################################################

        self.rect.center = pos

        # eq
        self.backpack = NPCEquipment()
        self.weapon = weapon
        self.level = level

        if weapon == 0:
            self.weapon_0 = self.fist_0
            self.weapon_1 = self.fist_1
        else:
            self.generate_weapons()
            self.change_weapons()
            self.generate_ammo()

        # items
        self.item = Item(items['item']['meat'], random.randint(0, 5))
        self.backpack.add_item(self.item)

        # behaviour
        self.speed = .2
        self.target = None
        self.true_target = pg.math.Vector2(self.position.x, 0)

    def generate_ammo(self):

        if self.weapon_0.name != 'fist':
            ammo = self.weapon_0.name + '_ammo'
            self.backpack.equip_ammo(Item(items['item'][ammo], random.randint(11, 19)), 'left')
        if self.weapon_1.name != 'fist':
            ammo = self.weapon_1.name + '_ammo'
            self.backpack.equip_ammo(Item(items['item'][ammo], random.randint(11, 19)), 'right')

    def generate_weapons(self):

        if self.level == 0:
            weapon0 = Pistol(items['weapon']['pistol'])
            weapon1 = Pistol(items['weapon']['pistol'])
        elif self.level == 1:
            a = random.randint(0, 1)
            if a == 0:
                weapon0 = Pistol(items['weapon']['pistol'])
            else:
                weapon0 = Shotgun(items['weapon']['shotgun'])
            a = random.randint(0, 1)
            if a == 0:
                weapon1 = Pistol(items['weapon']['pistol'])
            else:
                weapon1 = Shotgun(items['weapon']['shotgun'])
        else:
            a = random.randint(0, 2)
            if a == 0:
                weapon0 = Pistol(items['weapon']['pistol'])
            elif a == 1:
                weapon0 = Shotgun(items['weapon']['shotgun'])
            else:
                weapon0 = Uzi(items['weapon']['uzi'])
            a = random.randint(0, 2)
            if a == 0:
                weapon1 = Pistol(items['weapon']['pistol'])
            elif a == 1:
                weapon1 = Shotgun(items['weapon']['shotgun'])
            else:
                weapon1 = Uzi(items['weapon']['uzi'])

        a = random.randint(0, 2)

        if a == 0:
            self.backpack.equip_weapon(weapon0, 'left')
        elif a == 1:
            self.backpack.equip_weapon(weapon1, 'right')
        elif a == 2:
            self.backpack.equip_weapon(weapon0, 'left')
            self.backpack.equip_weapon(weapon1, 'right')

# UPDATE ###############################################################################################################

    def update(self, delta_time, target, camera, wall, player, particles):

        if self.dead_dead is True:
            pass
        elif self.dead is True and self.dead_dead is False:
            now = time.time()
            self.image = self.dead_image
            self.original_img = self.image
            angle = -(self.last_angle * 180) / math.pi - 90
            self.image = pg.transform.rotate(self.original_img, angle)
            x, y = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)
            if now - self.death_time >= 2:
                self.dead_dead = True
        else:
            self.death_time = time.time()

            distance_from_start = get_distance(self.rect.center, self.start_pos)
            distance = get_distance(self.rect.center, target)

            if player.dead is True:
                pass
            else:
                if self.target is None:
                    self.angle_rotation(self.angle)
                    if distance < 1024:
                        self.find_target(target, distance, wall)
                    if distance_from_start > 32:
                        self.target = self.start_pos
                    self.move_weapons(self.pi)
                    self.weapon_0.update(self.weapon_0_pos, delta_time, target, wall, [], particles, self.backpack.equipped_items[6], self.angle, False)
                    self.weapon_1.update(self.weapon_1_pos, delta_time, target, wall, [], particles, self.backpack.equipped_items[8], self.angle, False)
                else:
                    radians = get_angle(self.target, self.position, 'radians')
                    angle = get_angle(self.target, self.position) - 90
                    self.angle_rotation(angle)
                    self.move_weapons(radians)
                    self.move(delta_time, radians)
                    self.check_collision(wall)
                    if self.target == target:
                        self.attack(target)
                    else:
                        self.weapon_0.shoot = False
                        self.weapon_1.shoot = False
                    dist = get_distance(self.rect.center, self.target)
                    if self.target == self.start_pos and dist < 32:
                        self.target = None
                    if self.target == target and dist > 1024:
                        self.target = None

                    self.weapon_0.update(self.weapon_0_pos, delta_time, target, wall, [player], particles, self.backpack.equipped_items[6], angle)
                    self.weapon_1.update(self.weapon_1_pos, delta_time, target, wall, [player], particles, self.backpack.equipped_items[8], angle)

    def find_target(self, target, distance, wall):

        angle = get_angle(self.rect.center, target)
        enemy_angle = temp_function(self.angle)
        if distance <= 32:
            self.target = target

        if enemy_angle > 0 and angle > 0 or enemy_angle < 0 and angle < 0:
            if abs(enemy_angle - angle) <= 60:
                self.check_walls(target, distance, wall)

        elif enemy_angle >= 0 >= angle or angle >= 0 >= enemy_angle:
            if abs(abs(angle) - enemy_angle) <= 60:
                self.check_walls(target, distance, wall)

    def check_walls(self, target, distance, wall):
        temp_bool = False
        for wall in wall.sprites():
            if get_distance(wall.rect.center, self.rect.center) < distance:
                if wall.rect.clipline(self.rect.center, target):
                    temp_bool = True
                    break
        if temp_bool is False:
            self.target = target

    def angle_rotation(self, angle):

        self.image = pg.transform.rotate(self.original_img, angle)
        x, y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, delta_time, true_radians):
        self.acceleration.x = 0
        self.acceleration.y = 0
        x_move = math.cos(true_radians)
        y_move = math.sin(true_radians)
        self.acceleration.x += x_move * self.speed
        self.acceleration.y += y_move * self.speed

        self.acceleration += self.velocity * self.friction
        self.velocity += self.acceleration * delta_time
        self.position += self.velocity * delta_time

        self.rect.center = (self.position.x, self.position.y)

    def check_collision(self, wall):
        if pg.sprite.spritecollideany(self, wall):
            self.target = self.start_pos

    def move_weapons(self, radians):

        x_0 = self.position.x + math.cos(radians - math.pi * .5) * 32
        y_0 = self.position.y + math.sin(radians - math.pi * .5) * 32
        x_1 = self.position.x + math.cos(radians + math.pi * .5) * 32
        y_1 = self.position.y + math.sin(radians + math.pi * .5) * 32

        self.weapon_0_pos = (x_0, y_0)
        self.weapon_1_pos = (x_1, y_1)

    def attack(self, target):

        if get_distance(self.weapon_0.rect.center, target) <= self.weapon_0.attack_range:
            self.weapon_0.shoot = True
        else:
            self.weapon_0.shoot = False

        if get_distance(self.weapon_1.rect.center, target) <= self.weapon_1.attack_range:
            self.weapon_1.shoot = True
        else:
            self.weapon_1.shoot = False

    def take_damage(self, damage, particles, angle):
        self.hp -= damage
        if self.hp <= 0:
            self.dead = True
            self.last_angle = angle
            particles.append(Pool(self.rect))
        self.start_angle = angle


class NPC(Human):

    def __init__(self, pos):
        Human.__init__(self, pos)

        spritesheet = Spritesheet('data/assets/sprites/characters.png')
        self.image = spritesheet.parse_sprite('artur_head')
        self.fist_0 = spritesheet.parse_sprite('artur_left_fist')
        self.fist_1 = spritesheet.parse_sprite('artur_right_fist')
        self.rect = self.image.get_rect()
        self.original_img = self.image

        self.start_pos = pg.math.Vector2(pos)
        self.rect.center = pos
        self.weapon_0 = Fist(self.fist_0)
        self.weapon_1 = Fist(self.fist_1)

        self.backpack = NPCEquipment()
        self.backpack_visible = False

        s_0 = pg.mixer.Sound('data/sounds/artur/jestem_artur.mp3')
        s_1 = pg.mixer.Sound('data/sounds/artur/artur_opis_0.mp3')
        s_2 = pg.mixer.Sound('data/sounds/artur/artur_opis_1.mp3')
        narazie = pg.mixer.Sound('data/sounds/artur/narazie.mp3')
        dobra = pg.mixer.Sound('data/sounds/artur/dobra.mp3')

        s_0.set_volume(.5)

        # talk
        self.quotes = {'Who are you?': {'quote': ['My name is Arthur', 'I am an elder man, 180cm height, 85kg of body weight', '15cm dick, small, weak'],
                                        'key': 'text',
                                        'sound': [s_0, s_1, s_2]},

                       'Show me your wares': {'quote': ['Take a quick look'],
                                              'key': 'shop',
                                              'sound': [dobra]},
                       'Goodbye': {'quote': ['See ya'],
                                   'key': 'exit',
                                   'sound': [narazie]}
                       }
        self.dialogue = DialogueWindow(self.quotes)

    def update(self, delta_time, target, camera, wall, player, particles):

        self.rotation(target)
        self.weapon_0.update(self.weapon_0_pos, delta_time, target, wall, player, particles)
        self.weapon_1.update(self.weapon_1_pos, delta_time, target, wall, player, particles)
        if self.dialogue.talk is True:
            self.dialogue.update(delta_time)

    def draw(self, display, camera, dist=0):

        if self.weapon_0 is not None:
            self.weapon_0.draw(display, camera, dist)
        if self.weapon_1 is not None:
            self.weapon_1.draw(display, camera, dist)

        display.blit(self.image, (self.rect.x - dist - camera.x, self.rect.y - camera.y))
        if self.dialogue.talk is True:
            self.dialogue.draw(display)


def get_distance(a, b):
    delta_x = a[0] - b[0]
    delta_y = a[1] - b[1]
    r2 = delta_x ** 2 + delta_y ** 2
    r = math.sqrt(r2)
    return r


def get_angle(a, b, type='angle'):
    delta_x = a[0] - b[0]
    delta_y = a[1] - b[1]
    radians = math.atan2(-delta_y, delta_x)
    angle = (radians * 180) / math.pi

    if type == 'angle':
        return angle
    elif type == 'radians':
        radians = math.atan2(delta_y, delta_x)
        return radians


def angle_to_rads(angle):
    rads = angle * math.pi / 180
    return rads


def rads_to_angle(rads):
    angle = rads * 180 / math.pi
    return angle


def temp_function(angle):

    angle -= 90

    if angle > 180:
        angle -= 360

    return angle
