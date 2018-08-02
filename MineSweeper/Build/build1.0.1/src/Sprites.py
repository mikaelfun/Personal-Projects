import pygame,sys
import random
import enum

class TileState(enum.Enum):
    hidden = 0
    flagged = 1     # flagged as bomb
    revealed = 2
    marked = 3      # means ?

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, img, tileSize, bw, bh, num = 0):
        pygame.font.init()
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x * tileSize + bw
        self.rect.y = y * tileSize + bh
        self.num = num
        self.state = TileState.hidden
        self.flag = False


