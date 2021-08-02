import pygame as pg
import random
import time, math


class BloodShoot:

    def __init__(self, pos, start_time, angle):

        self.type = 'const'
        self.particles = []
        self.color = (209, 0, 28)
        temp = random.randint(2, 5)
        for i in range(temp):
            speed = random.randint(3, 12)
            angle = random.uniform(angle - math.pi * .05, angle + math.pi * .05)
            size = random.randint(3, 5)
            self.particles.append(Particle(pos, start_time, self.color, size, 'decrease', angle, speed))

    def update(self, delta_time):
        for particle in self.particles:
            particle.update(delta_time)
            if particle.remove is True:
                self.particles.remove(particle)

    def draw(self, display_0, display_1, camera, dist):
        if display_1 is not None:
            for particle in self.particles:
                if display_0.get_width() + dist[0] >= particle.pos.x >= dist[0]:
                    particle.draw(display_0, camera, dist[0])
                if display_1.get_width() + dist[1] >= particle.pos.x >= dist[1]:
                    particle.draw(display_1, camera, dist[1])
        else:
            for particle in self.particles:
                particle.draw(display_0, camera, 0)


class Dust(BloodShoot):

    def __init__(self, pos, start_time):
        BloodShoot.__init__(self, pos, start_time, 0)
        self.type = 'temp'
        self.particles = []
        self.color = (69, 69, 69)
        temp = 1
        for i in range(temp):
            self.particles.append(Particle(pos, start_time, self.color, 5))


class Pool:

    def __init__(self, rect):

        n = random.randint(3, 5)
        self.particles = []
        self.type = 'const'
        color = (209, 0, 28)

        for i in range(n):
            pos = (random.randint(rect.x, rect.x + rect.w), random.randint(rect.y, rect.y + rect.h))
            r = random.randint(32, 64)
            self.particles.append(Particle(pos, time.time(), color, r, 'increase'))

    def update(self, delta_time):
        for particle in self.particles:
            particle.update(delta_time)
            if particle.remove is True:
                self.particles.remove(particle)

    def draw(self, display_0, display_1, camera, dist):
        if display_1 is not None:
            for particle in self.particles:
                if display_0.get_width() + dist[0] >= particle.get_left_border() >= dist[0] or\
                        display_0.get_width() + dist[0] >= particle.get_right_border() >= dist[0]:
                    particle.draw(display_0, camera, dist[0])
                if display_1.get_width() + dist[1] >= particle.get_left_border() >= dist[1] or\
                        display_1.get_width() + dist[1] >= particle.get_right_border() >= dist[1]:
                    particle.draw(display_1, camera, dist[1])
        else:
            for particle in self.particles:
                particle.draw(display_0, camera, 0)


class Particle:

    def __init__(self, pos, start_time, color, radius, type='decrease', angle=0.0, speed=0.0):

        self.pos = pg.math.Vector2(pos[0], pos[1])
        self.start_time = start_time
        self.angle = angle
        self.speed = speed
        self.remove = False

        self.type = type
        if type == 'decrease':
            self.radius = radius
        elif type == 'increase':
            self.radius = .1
            self.max_radius = radius

        self.color_0 = (138, 3, 3)
        self.color_1 = color

    def draw(self, display, camera, dist):

        pg.draw.circle(display, self.color_1, (self.pos.x - dist - camera.x, self.pos.y - camera.y), self.radius)

    def update(self, delta_time):
        now = time.time()

        x_move = math.cos(self.angle)
        y_move = math.sin(self.angle)
        self.pos.x += x_move * delta_time * self.speed
        self.pos.y += y_move * delta_time * self.speed

        if self.type == 'decrease':
            self.radius -= .05
            if now - 2 > self.start_time:
                self.remove = True
        elif self.type == 'increase':
            if self.radius < self.max_radius:
                self.radius += .5
            else:
                self.remove = True

    def get_left_border(self):
        return self.pos.x - self.max_radius

    def get_right_border(self):
        return self.pos.x + self.max_radius
