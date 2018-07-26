import pygame, sys
from pygame.locals import *
from Color import *
import enum
import ctypes

user32 = ctypes.windll.user32
screenWidth, screenHeight = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1) - 100

tileWidth = 64
boarderWidth = 40
boarderHeight = 10

WindowHeight = screenHeight // 8


class TileState(enum.Enum):
    hidden = 0
    revealed = 1
    marked = 2
    flagged = 3

class Tile(pygame.sprite.Sprite):
    def __init__(self, xPos, yPos, size, flag = False, num = 0):
        pygame.sprite.Sprite.__init__(self)
        self.num = num
        self.flag = flag
        self.state = TileState.hidden
        self.size = size
        # print (self.size)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (xPos, yPos)


class Background(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((screenWidth, screenHeight))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        # self.rect.x = (x * 32+5)
        # self.rect.y = 12
        # self.rect.center = (x * 32+5, y*32+25)

class Smily(pygame.sprite.Sprite):
    def __init__(self, x, y, screenWidth):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((64, 64))
        self.rect = self.image.get_rect()
        self.rect.center = (screenWidth/2, 34)
