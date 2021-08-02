import pygame
from abc import ABC, abstractmethod
import math
vec = pygame.math.Vector2


class Camera:
    def __init__(self, player, cursor):
        self.method = None
        self.player = player
        self.cursor = cursor
        self.offset = vec(0, 0)
        self.offset_float = vec(0, 0)
        self.DISPLAY_W, self.DISPLAY_H = pygame.display.get_window_size()
        self.CONST = vec(-self.DISPLAY_W * .5, -self.DISPLAY_H * .5)

    def set_method(self, method):
        self.method = method

    def scroll(self, border, move=True, speed=1):
        self.method.scroll(border, move, speed)


class CamScroll(ABC):
    def __init__(self, camera, player, cursor=None):
        self.camera = camera
        self.player = player
        self.cursor = cursor

    @abstractmethod
    def scroll(self, border, move=True, speed=1):
        pass


class Follow(CamScroll):
    def __init__(self, camera, player):
        CamScroll.__init__(self, camera, player)

    def scroll(self, border, move=True, speed=1):
        self.camera.offset_float.x += (self.player.rect.center[0] - self.camera.offset_float.x + self.camera.CONST.x)
        self.camera.offset_float.y += (self.player.rect.center[1] - self.camera.offset_float.y + self.camera.CONST.y)
        self.camera.offset.x, self.camera.offset.y = int(self.camera.offset_float.x), int(self.camera.offset_float.y)


class Border(CamScroll):
    def __init__(self, camera, player):
        CamScroll.__init__(self, camera, player)

    def scroll(self, border,  move=True, speed=1):

        self.camera.offset_float.x += (self.player.rect.center[0] - self.camera.offset_float.x + self.camera.CONST.x)
        self.camera.offset_float.y += (self.player.rect.center[1] - self.camera.offset_float.y + self.camera.CONST.y)
        self.camera.offset.x, self.camera.offset.y = int(self.camera.offset_float.x), int(self.camera.offset_float.y)

        if border[0] != -1:
            self.camera.offset.y = max(border[0], self.camera.offset.y)
        if border[1] != -1:
            self.camera.offset.y = min(self.camera.offset.y, border[1] - self.camera.DISPLAY_H)
        if border[2] != -1:
            self.camera.offset.x = max(border[2], self.camera.offset.x)
        if border[3] != -1:
            self.camera.offset.x = min(self.camera.offset.x, border[3] - self.camera.DISPLAY_W)


class CursorBorder(CamScroll):
    def __init__(self, camera, player, cursor):
        CamScroll.__init__(self, camera, player, cursor)

    def scroll(self, border,  move=True, speed=1):
        self.camera.offset_float.x += (self.cursor.true_pos[0] - self.camera.offset_float.x + self.camera.CONST.x)
        self.camera.offset_float.y += (self.cursor.true_pos[1] - self.camera.offset_float.y + self.camera.CONST.y)
        self.camera.offset.x, self.camera.offset.y = int(self.camera.offset_float.x), int(self.camera.offset_float.y)

        if border[0] != -1:
            self.camera.offset.y = max(border[0], self.camera.offset.y)
        if border[1] != -1:
            self.camera.offset.y = min(self.camera.offset.y, border[1] - self.camera.DISPLAY_H)
        if border[2] != -1:
            self.camera.offset.x = max(border[2], self.camera.offset.x)
        if border[3] != -1:
            self.camera.offset.x = min(self.camera.offset.x, border[3] - self.camera.DISPLAY_W)


class Auto(CamScroll):
    def __init__(self, camera, player):
        CamScroll.__init__(self, camera, player)

    def scroll(self, border, move=True, speed=1):
        self.camera.offset_float.y += (self.player.rect.center[1] - self.camera.offset_float.y + self.camera.CONST.y)
        self.camera.offset.y = int(self.camera.offset_float.y)
        if move is True:
            self.camera.offset.x += speed

        if border[0] != -1:
            self.camera.offset.y = max(border[0], self.camera.offset.y)
        if border[1] != -1:
            self.camera.offset.y = min(self.camera.offset.y, border[1] - self.camera.DISPLAY_H)
        if border[2] != -1:
            self.camera.offset.x = max(border[2], self.camera.offset.x)
        if border[3] != -1:
            self.camera.offset.x = min(self.camera.offset.x, border[3] - self.camera.DISPLAY_W)


def get_distance(a, b):
    delta_x = a[0] - b[0]
    delta_y = a[1] - b[1]
    r2 = delta_x ** 2 + delta_y ** 2
    r = math.sqrt(r2)
    return r
