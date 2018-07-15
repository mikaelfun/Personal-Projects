import pygame, sys
from Sprites import *
import random
from Globals import *


class MineField:
    def __init__(self, all_sprites, surface, x, y, n, boarderWidth, boarderHeight, screenWidth, screenHeight, size):
        self.x = x
        self.y = y
        self.n = n
        self.TileSize = size
        self.boarderWidth = boarderWidth
        self.boarderHeight = boarderHeight
        self.surface = surface
        self.tileArray = []
        self.mineLocation = []
        # self.bg = Background(x, y)
        self.all_sprites = all_sprites
        # self.all_sprites.add(self.bg)
        self.smilyFace = Smily(x, y, screenWidth)
        self.all_sprites.add(self.smilyFace)
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.windowHeight =  100


        while len(self.mineLocation) != n:
            tempx = random.randint(0, x-1)
            tempy = random.randint(0, y-1)
            if (tempx, tempy) not in self.mineLocation:
                self.mineLocation.append((tempx,tempy))
        # print (self.mineLocation)

        for a in range(self.x):
            tempArr = []
            for b in range(self.y):
                if (a,b) in self.mineLocation:
                    posx, posy = self.computeTileCenter(a, b)
                    tile = Tile(posx, posy, self.TileSize, flag = True)
                else:
                    posx, posy = self.computeTileCenter(a, b)
                    tile = Tile(posx, posy, self.TileSize,flag = False, num = self.getNum(a,b))
                self.all_sprites.add(tile)
                tempArr.append(tile)
            self.tileArray.append(tempArr)

    def computeTileCenter(self, a,b):
        return ( self.boarderWidth + a * self.TileSize + self.TileSize/2, self.windowHeight +  self.boarderHeight + b * self.TileSize+ self.TileSize/2)

    def getNum(self, x, y):
        num = 0
        for i in range(max(x-1, 0), min(x+2,self.x)):
            for j in range(max(y-1, 0), min(y+2, self.y)):
                if (i,j) in self.mineLocation:
                    num+=1
        return num


    def display(self):
        self.all_sprites.update()
        self.all_sprites.draw(self.surface)
        # pygame.display.update()


    def checkGameWin(self, gameOver):
        if gameOver:
            return False
        for i in range(0, self.x):
            for j in range(0, self.y):
                if self.tileArray[i][j].state == TileState.hidden:
                    return False
        return True

    def restart(self, surface,boardW,boardH,bombNum):
        pygame.sprite.Group().empty()
        self.__init__(surface,boardW,boardH,bombNum)

    def __del__(self):
        self.all_sprites.empty()
        del self.tileArray
        del self.x
        del self.y
        del self.n
        del self.surface
        del self.mineLocation
        del self.all_sprites
        del self.smilyFace
