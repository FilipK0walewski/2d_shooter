import pygame as pg
import math
import random
import time
from data.particles import BloodShoot, Dust
from data.images import Spritesheet


class Aimer(pg.sprite.Sprite):

    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        self.pos = pg.mouse.get_pos()
        self.true_pos = pg.mouse.get_pos()
        self.color = (248, 227, 196)
        self.radius = 3

    def draw(self, display):
        pg.draw.circle(display, self.color, self.pos, self.radius)

    def update(self, camera=pg.math.Vector2(0, 0)):
        pos = pg.mouse.get_pos()
        self.pos = pos
        self.true_pos = (pos[0] + camera.x, pos[1] + camera.y)


class Fist(pg.sprite.Sprite):

    def __init__(self, img):
        pg.sprite.Sprite.__init__(self)

        self.image = img
        self.rect = self.image.get_rect()
        self.original_img = self.image
        self.name = 'fist'
        self.radians = 0
        self.hit = False
        self.speed = 8
        self.position = pg.math.Vector2(self.rect.center)

        self.shoot = False
        self.last_shoot = time.time()
        self.attack_speed = 2.5
        self.attack_damage = 50
        self.attack_range = 128

    def draw(self, display, camera, dist):
        display.blit(self.image, (self.rect.x - dist - camera.x, self.rect.y - camera.y))

    def update(self, pos, delta_time, target, wall, enemies, particles, magazine=None, character_angle=None, attack=True):

        if self.shoot is True:
            self.hitting()

        if self.hit is False:
            self.position.x = pos[0]
            self.position.y = pos[1]
            self.rotation(target, character_angle)
        else:
            x_move = math.cos(self.radians)
            y_move = math.sin(self.radians)
            self.position.x += x_move * delta_time * self.speed
            self.position.y += y_move * delta_time * self.speed
            if math.sqrt((pos[0] - self.position.x) ** 2 + (pos[1] - self.position.y) ** 2) > 64:
                self.hit = False

            if type(enemies) == list:
                for enemy in enemies:
                    if enemy.dead is False:
                        if enemy.rect.collidepoint(self.rect.midtop):
                            particles.append(BloodShoot(self.rect.midtop, time.time(), self.radians))
                            enemy.take_damage(self.attack_damage, particles, self.radians)
                        elif enemy.rect.collidepoint(self.rect.midtop):
                            particles.append(BloodShoot(self.rect.midbottom, time.time(), self.radians))
                            enemy.take_damage(self.attack_damage, particles, self.radians)
                        elif enemy.rect.collidepoint(self.rect.midleft):
                            particles.append(BloodShoot(self.rect.midleft, time.time(), self.radians))
                            enemy.take_damage(self.attack_damage, particles, self.radians)
                        elif enemy.rect.collidepoint(self.rect.midright):
                            particles.append(BloodShoot(self.rect.midright, time.time(), self.radians))
                            enemy.take_damage(self.attack_damage, particles, self.radians)
            else:
                if enemies.dead is False:
                    if enemies.rect.collidepoint(self.rect.midtop):
                        particles.append(BloodShoot(self.rect.midtop, time.time(), self.radians))
                        enemies.take_damage(self.attack_damage, particles, self.radians)
                    elif enemies.rect.collidepoint(self.rect.midtop):
                        particles.append(BloodShoot(self.rect.midbottom, time.time(), self.radians))
                        enemies.take_damage(self.attack_damage, particles, self.radians)
                    elif enemies.rect.collidepoint(self.rect.midleft):
                        particles.append(BloodShoot(self.rect.midleft, time.time(), self.radians))
                        enemies.take_damage(self.attack_damage, particles, self.radians)
                    elif enemies.rect.collidepoint(self.rect.midright):
                        particles.append(BloodShoot(self.rect.midright, time.time(), self.radians))
                        enemies.take_damage(self.attack_damage, particles, self.radians)

            for tile in wall:
                if tile.rect.collidepoint(self.rect.midtop):
                    particles.append(Dust(self.rect.midtop, time.time()))
                    self.hit = False
                elif tile.rect.collidepoint(self.rect.midtop):
                    particles.append(Dust(self.rect.midbottom, time.time()))
                    self.hit = False
                elif tile.rect.collidepoint(self.rect.midleft):
                    particles.append(Dust(self.rect.midleft, time.time()))
                    self.hit = False
                elif tile.rect.collidepoint(self.rect.midright):
                    particles.append(Dust(self.rect.midright, time.time()))
                    self.hit = False

        self.rect.center = self.position

    def rotation(self, target, character_angle):

        delta_x = target[0] - self.rect.center[0]
        delta_y = target[1] - self.rect.center[1]
        self.radians = math.atan2(delta_y, delta_x)
        angle = -(self.radians * 180) / math.pi - 90

        if character_angle is not None:
            temp = abs(angle - character_angle)
            if temp > 20:
                angle = character_angle

        self.image = pg.transform.rotate(self.original_img, angle)
        x, y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def hitting(self):

        now = time.time()
        if now > self.last_shoot + 1 / self.attack_speed:
            self.last_shoot = now
            self.hit = True


class Pistol:

    def __init__(self, info, quantity=1):

        # info
        self.name = info['name']
        self.type = info['type']
        self.code = info['code']
        self.description = info['description']
        self.quantity = quantity
        self.klasa = info['klasa']

        # images
        self.spritesheet = Spritesheet('data/assets/sprites/items.png')
        self.image = self.spritesheet.get_image('weapon', self.name, 'image')
        self.icon = self.spritesheet.get_image('weapon', self.name, 'icon')
        self.icon_rect = self.icon.get_rect()

        self.rect = self.image.get_rect()
        self.original_img = self.image
        self.bullets = []

        # stats
        self.attack_damage = 34
        self.attack_speed = 2
        self.attack_range = 1024
        self.magazine_size = 11

        self.shoot = False
        self.last_shoot = 0
        self.now = time.time()

    def draw(self, display, camera, dist):
        display.blit(self.image, (self.rect.x - dist - camera.x, self.rect.y - camera.y))
        for bullet in self.bullets:
            bullet.draw(display, camera)

    def update(self, pos, delta_time, target, wall, enemies, particles, magazine, character_angle=None, attack=True):

        self.rect.center = pos
        self.rotation(target, character_angle)
        if attack is True:
            if self.shoot is True:
                if magazine.item is not None and self.name in magazine.item.name:
                    self.shooting(target, magazine)
        for bullet in self.bullets:
            bullet.update(delta_time)
            for tile in wall:
                if bullet.rect.colliderect(tile.rect):
                    particles.append(Dust(bullet.rect.center, time.time()))
                    try:
                        self.bullets.remove(bullet)
                    except:
                        print('huj')
                    bullet.image.fill((255, 0, 0))
                    break
            for enemy in enemies:
                if enemy.dead is False:
                    if bullet.rect.colliderect(enemy.rect):
                        particles.append(BloodShoot(bullet.rect.center, time.time(), bullet.angle))
                        enemy.take_damage(self.attack_damage, particles, bullet.angle)
                        try:
                            self.bullets.remove(bullet)
                        except:
                            print('huj')
                        bullet.image.fill((255, 0, 0))
                        break

    def rotation(self, target, character_angle):

        delta_x = target[0] - self.rect.center[0]
        delta_y = target[1] - self.rect.center[1]
        radians = math.atan2(delta_y, delta_x)
        angle = -(radians * 180) / math.pi - 90

        if character_angle is not None:
            temp = abs(angle - character_angle)
            if temp > 20:
                angle = character_angle

        self.image = pg.transform.rotate(self.original_img, angle)
        x, y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def shooting(self, target, magazine):
        self.now = time.time()
        if self.now > self.last_shoot + 1 / self.attack_speed:
            if magazine.item.quantity > 0:
                magazine.item.quantity -= 1
                self.last_shoot = self.now
                bullet = Projectile(self.rect.center, target)
                self.bullets.append(bullet)


class Shotgun(Pistol):

    def __init__(self, info, quantity=1):
        Pistol.__init__(self, info, quantity)

        # stats
        self.attack_range = 1024
        self.attack_speed = .75

    def shooting(self, target, magazine):
        self.now = time.time()
        if magazine.item.quantity > 0:
            if self.now > self.last_shoot + 1 / self.attack_speed:
                magazine.item.quantity -= 1
                self.last_shoot = self.now
                r = (target[0] - self.rect.x) ** 2 + (target[1] - self.rect.y) ** 2
                r = math.sqrt(r)
                r = int(r * .25)
                for i in range(4):
                    pos_x = random.randint(int(target[0]) - r, int(target[0]) + r)
                    pos_y = random.randint(int(target[1]) - r, int(target[1]) + r)
                    bullet = Projectile(self.rect.center, (pos_x, pos_y))
                    self.bullets.append(bullet)


class Uzi(Pistol):

    def __init__(self, info, quantity=1):
        Pistol.__init__(self, info, quantity)

        # stats
        self.attack_speed = 8
        self.attack_damage = 25

    def shooting(self, target, magazine):

        now = time.time()
        if magazine.item.quantity > 0:
            if now > self.last_shoot + 1 / self.attack_speed:
                magazine.item.quantity -= 1
                self.last_shoot = time.time()
                bullet = Projectile(self.rect.center, target)
                self.bullets.append(bullet)


class Projectile(pg.sprite.Sprite):

    def __init__(self, start_pos, target):
        pg.sprite.Sprite.__init__(self)

        self.image = pg.Surface((6, 6))
        self.image.fill((0, 0, 255))
        self.pos = start_pos
        self.target = target
        self.color = (248, 227, 196)
        self.radius = 3
        self.rect = self.image.get_rect()

        self.speed = 5
        self.friction = -.0001
        self.acceleration = pg.math.Vector2(0, 0)
        self.velocity = pg.math.Vector2(0, 0)
        self.position = pg.math.Vector2(start_pos)

        delta_x = target[0] - start_pos[0]
        delta_y = target[1] - start_pos[1]
        self.angle = math.atan2(delta_y, delta_x)

    def update(self, delta_time):

        if self.friction > -.9:
            self.friction -= .0002
            self.speed *= .95

        self.acceleration.x = 0
        self.acceleration.y = 0
        x_move = math.cos(self.angle)
        y_move = math.sin(self.angle)
        self.acceleration.x += x_move * self.speed
        self.acceleration.y += y_move * self.speed

        self.acceleration += self.velocity * self.friction
        self.velocity += self.acceleration * delta_time
        self.position += self.velocity * delta_time

        self.rect.x = self.position.x
        self.rect.y = self.position.y

    def draw(self, display, camera):
        display.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
