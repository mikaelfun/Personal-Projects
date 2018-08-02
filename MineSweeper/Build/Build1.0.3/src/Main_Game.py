import pygame,sys
import pygame.time
from pygame.locals import *
from Sprites import *
import random
from Globals import *
from InputBox import *
import os
os.environ['SDL_VIDEO_CENTERED'] = '1'
from win32api import GetSystemMetrics

SystemWidth = GetSystemMetrics(0)
SystemHeight = GetSystemMetrics(1)
print (SystemWidth,SystemHeight )
WHITE = 255,255,255

'''
Objectives:
1. create a white board     done
2. create a grid of tiles   done
3. create minefield         done
4. playable                 done
5. reset, restart function withou mem leak  done
6. background and tile skins    done
7. option menu and resize control   done
8. mousemotion effects      done
9. middle button auto expand    done
10. smile face button       done
11. auto readjust screen size and tilesize      done
12. 
'''
class MyMineSweeper:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        # Init all fields
        self.tileArray = []     # 2d array
        self.all_sprites = pygame.sprite.Group()
        self.tileImgGroup = []
        # 50 >= width >= 10
        self.width = 20
        # 24>= height >= 6
        self.height = 12

        self.mine = 30
        self.tileSize = 64
        self.boarderWidth = SystemWidth//15
        self.boarderHeight = 96
        self.controlboarderHeight = 74
        self.myfont = pygame.font.SysFont('cambria', 48)
        self.gameState = GameState.waiting
        self.prevState = GameState.waiting
        self.mineField = []
        self.image = {}
        self.windowW = (self.width * self.tileSize + 2 * self.boarderWidth)
        self.windowH = (self.height * self.tileSize + self.boarderHeight + self.controlboarderHeight)
        self.optionIconPos = (self.windowW / 2 - 32, self.windowH - self.controlboarderHeight + 5)
        # print (self.optionIconPos)
        self.optionIconRect = pygame.rect.Rect(self.optionIconPos, (SystemWidth // 30,SystemWidth // 30))
        self.optionWindowW = 440
        self.optionWindowH = 320
        self.optionYESPos = (self.windowW / 2 - 74, self.windowH - (self.windowH - self.optionWindowH)/2 - 74)
        self.optionNOPos = (self.windowW / 2 + 10, self.windowH - (self.windowH - self.optionWindowH)/2 - 74)
        self.optionYESRect = pygame.rect.Rect(self.optionYESPos, (64, 64))
        self.optionNORect = pygame.rect.Rect(self.optionNOPos, (64, 64))
        self.optionGridPos = (self.windowW / 2 - 160, self.windowH /2 - 114)
        self.optionBombCountPos = (self.windowW / 2 - 160, self.windowH /2 - 20 )
        self.onOptionIcon = False
        self.onSmileIcon = False

        self.surface = pygame.display.set_mode((self.windowW, self.windowH))

        self.resize_box1 = InputBox(self.optionGridPos[0] + 124 + 5 , self.optionGridPos[1] + 5, 54, 54, str(self.width))
        self.resize_box2 = InputBox(self.optionGridPos[0] + 252 + 5 , self.optionGridPos[1] + 5, 54, 54, str(self.height))
        self.resize_box3 = InputBox(self.optionBombCountPos[0] + 124 + 2, self.optionBombCountPos[1] + 5, 54, 54, str(self.mine))
        self.input_boxes = [self.resize_box1, self.resize_box2, self.resize_box3]

        self.leftmouseDownPos = (-1, -1)
        self.midmouseDownPos = (-1, -1)
        self.rightmouseDownPos = (-1, -1)

        self.leftMouseDown = False
        self.midMouseDown = False

        self.curIndex = (-1, -1)
        self.prevTile = (-1, -1)
        # used for timer progression and bombleft tracking
        self.clock = pygame.time.Clock()
        self.timer = 0
        self.dt = 0
        self.bombLeft = self.mine
        self.leftMousetimer = 0


        self.image_init()

        # initialize Smile Icon
        self.smile = pygame.sprite.Sprite()
        self.smile.image = self.image["normal"]
        self.smile.rect = self.smile.image.get_rect()
        self.smile.rect.center = self.windowW / 2, self.boarderHeight / 2
        self.all_sprites.add(self.smile)


        self.update_window()

        self.init_minefield()
        self.init_tilearray()


        sys.setrecursionlimit(self.width * self.height)
        # print (self.mineField)

    def init_minefield(self):
        if self.mineField:
            del self.mineField
            self.mineField = []
        while len(self.mineField) != self.mine:
            a, b = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (a, b) not in self.mineField:
                self.mineField.append((a,b))

    def init_tilearray(self):
        if self.tileArray:
            for each in self.tileArray:
                for x in each:
                    x.kill()
                    del x
            self.tileArray = []
        for i in range(self.width):
            tmpArray = []
            for j in range(self.height):
                tile = Tile(i, j, self.image["Hidden"], self.tileSize, self.boarderWidth, self.boarderHeight, self.getNum(i, j))
                if (i,j) in self.mineField:
                    tile.flag = True
                self.all_sprites.add(tile)
                tmpArray.append(tile)  # passing in index to draw on corresponding postion on the suface
            self.tileArray.append(tmpArray)

    def image_init(self):
        if len(self.image) != 0:
            del self.image
            self.image = {}
        self.image["Hidden"] = pygame.image.load('Img\\Tile1.png').convert_alpha()
        self.image["Hidden1"] = pygame.image.load('Img\\Tile2.png').convert_alpha()
        self.image["Bomb"] = pygame.image.load('Img\\bomb.png').convert_alpha()
        self.image["flag"] = pygame.image.load('Img\\flag1.png').convert_alpha()
        self.image["num1"] = pygame.image.load('Img\\1.png').convert_alpha()
        self.image["num2"] = pygame.image.load('Img\\2.png').convert_alpha()
        self.image["num3"] = pygame.image.load('Img\\3.png').convert_alpha()
        self.image["num4"] = pygame.image.load('Img\\4.png').convert_alpha()
        self.image["num5"] = pygame.image.load('Img\\5.png').convert_alpha()
        self.image["num6"] = pygame.image.load('Img\\6.png').convert_alpha()
        self.image["num7"] = pygame.image.load('Img\\7.png').convert_alpha()
        self.image["num8"] = pygame.image.load('Img\\8.png').convert_alpha()
        self.image["empty"] = pygame.image.load('Img\\emptyTile.png').convert_alpha()
        self.image["wrongflag"] = pygame.image.load('Img\\wrongflag1.png').convert_alpha()
        self.image["correctflag"] = pygame.image.load('Img\\flaggedbomb.png').convert_alpha()
        self.image["marked"] = pygame.image.load('Img\\Q1.png').convert_alpha()
        self.image["tileDown"] = pygame.image.load('Img\\tileDown.png').convert_alpha()

        self.tileImgGroup = ["num1","num2","num3","num4","num5","num6","num7","num8",
                             "Hidden", "Bomb", "flag", "empty", "wrongflag",
                             "correctflag", "marked","tileDown", ]
        self.image["timer"] = pygame.image.load('Img\\timer.png').convert_alpha()
        self.image["timer"] = pygame.transform.scale(self.image["timer"], (64, 64))
        self.image["bombCount"] = pygame.image.load('Img\\bombcount.png').convert_alpha()
        self.image["bombCount"] = pygame.transform.scale(self.image["bombCount"], (64,64))
        self.image["option"] = pygame.image.load('Img\\option.png').convert_alpha()
        self.image["option"] = pygame.transform.scale(self.image["option"], (64, 64))
        self.image["optionBig"] = pygame.image.load('Img\\option.png').convert_alpha()
        self.image["optionBig"] = pygame.transform.scale(self.image["optionBig"], (64 + 4, 64 + 4))
        self.image["YES"] = pygame.image.load('Img\\OK.png').convert_alpha()
        self.image["YES"] = pygame.transform.scale(self.image["YES"], (64, 64))
        self.image["NO"] = pygame.image.load('Img\\NO.png').convert_alpha()
        self.image["NO"] = pygame.transform.scale(self.image["NO"], (64, 64))
        self.image["optionBG"] = pygame.image.load("Img\\OPBG.jpg")
        self.image["optionBG"] = pygame.transform.scale(self.image["optionBG"], (self.optionWindowW, self.optionWindowH))
        self.image["bg"] = pygame.image.load("Img\\bg.jpg")
        self.image["bg"] = pygame.transform.scale(self.image["bg"], (self.windowW, self.windowH))
        self.image["grid"] = pygame.image.load("Img\\grid.png")
        self.image["grid"] = pygame.transform.scale(self.image["grid"], (64, 64))
        self.image["input"] = pygame.image.load("Img\\inputbox.png")
        self.image["input"] = pygame.transform.scale(self.image["input"], (64, 64))
        self.image["X"] = pygame.image.load("Img\\X.png")
        self.image["X"] = pygame.transform.scale(self.image["X"], (64, 64))
        self.image["normal"] = pygame.image.load("Img\\normal.png")
        self.image["normal"] = pygame.transform.scale(self.image["normal"], (64, 64))
        self.image["normalBig"] = pygame.image.load("Img\\normal.png")
        self.image["normalBig"] = pygame.transform.scale(self.image["normalBig"], (64 + 4, 64 + 4))
        self.image["hit"] = pygame.image.load("Img\\hit.png")
        self.image["hit"] = pygame.transform.scale(self.image["hit"], (64, 64))
        self.image["hit1"] = pygame.image.load("Img\\hit1.png")
        self.image["hit1"] = pygame.transform.scale(self.image["hit1"], (64, 64))
        self.image["win"] = pygame.image.load("Img\\win.png")
        self.image["win"] = pygame.transform.scale(self.image["win"], (64, 64))
        self.image["lose"] = pygame.image.load("Img\\lose.png")
        self.image["lose"] = pygame.transform.scale(self.image["lose"], (64, 64))
        self.image["winBig"] = pygame.image.load("Img\\win.png")
        self.image["winBig"] = pygame.transform.scale(self.image["winBig"], (64 + 4, 64 + 4))
        self.image["loseBig"] = pygame.image.load("Img\\lose.png")
        self.image["loseBig"] = pygame.transform.scale(self.image["loseBig"], (64 + 4, 64 + 4))

        # print (self.tileSize)
        if self.tileSize < 64:
            for all in self.tileImgGroup:
                self.image[all] = pygame.transform.scale(self.image[all], (self.tileSize, self.tileSize))

        self.image["Hidden1"] = pygame.transform.scale(self.image["Hidden1"], (self.tileSize + 2, self.tileSize + 2))
        # self.image["tileDown"] = pygame.transform.scale(self.image["tileDown"], (self.tileSize - 1, self.tileSize - 1))

    def getNum(self,i ,j):
        num = 0
        if (i, j) in self.mineField:
            return -1
        for x in range(max(i-1, 0), min(i+2,self.width)):
            for y in range(max(j-1, 0), min(j+2, self.height)):
                if (x,y) in self.mineField:
                    num+=1
        return num

    def adjustTileSize(self):
        if self.windowW > SystemWidth and self.windowH < SystemHeight - SystemHeight * 0.08:
            # only shrink width
            if SystemWidth - self.tileSize * self.width >= SystemWidth // 20:
                # boardwidth >= SystemWidth // 40 is acceptable
                self.boarderWidth = (SystemWidth - self.tileSize * self.width) // 2
                self.windowW = self.tileSize * self.width + self.boarderWidth*2
                #print (".1")
            else:
                self.boarderWidth = SystemWidth // 40
                self.windowW = SystemWidth
                self.tileSize = (self.windowW - self.boarderWidth*2) // self.width
                self.windowW = self.tileSize * self.width + self.boarderWidth*2
                self.windowH = self.tileSize * self.height + self.boarderHeight+ self.controlboarderHeight
                #print (".5")

        elif self.windowW <= SystemWidth and self.windowH > SystemHeight - SystemHeight * 0.08:
            # only shrink height
            self.windowH = int(SystemHeight - SystemHeight * 0.08)
            self.tileSize = (self.windowH - self.boarderHeight - self.controlboarderHeight) // self.height
            self.windowH = self.tileSize * self.height + self.boarderHeight+ self.controlboarderHeight
            self.windowW = self.tileSize * self.width + self.boarderWidth*2
            #print ("1")
        else:
            if SystemWidth - self.tileSize * self.width >= SystemWidth // 20:
                # boardwidth >=50 is acceptable
                self.boarderWidth = (SystemWidth - self.tileSize * self.width) // 2
                self.windowW = self.tileSize * self.width + self.boarderWidth*2
                self.windowH = self.tileSize * self.height + self.boarderHeight+ self.controlboarderHeight
                if self.windowH > SystemHeight - SystemHeight * 0.08:
                    self.adjustTileSize()
                    #print ("2")
                #print ("2.1")
            else:
                self.boarderWidth = SystemWidth // 40
                self.windowW = SystemWidth
                self.tileSize = (self.windowW - self.boarderWidth*2) // self.width
                self.windowW = self.tileSize * self.width + self.boarderWidth*2
                self.windowH = self.tileSize * self.height + self.boarderHeight+ self.controlboarderHeight
                if self.windowH > SystemHeight - SystemHeight * 0.08:
                    self.adjustTileSize()
                    if self.boarderWidth * 2 + self.tileSize * self.width < SystemWidth:
                        self.boarderWidth = min(SystemWidth // 15, (SystemWidth - self.tileSize * self.width) // 2)
                        self.windowW = self.tileSize * self.width + self.boarderWidth*2
                        #print ("3.0")
                    #print ("3.1")
                #print ("3.2")
        # print ("new tile size:", self.tileSize)

    def update_window(self):
        prevSize = self.tileSize
        self.tileSize = 64
        self.boarderWidth = SystemWidth // 15
        self.windowW = (self.width * self.tileSize + 2 * self.boarderWidth)
        self.windowH = (self.height * self.tileSize + self.boarderHeight + self.controlboarderHeight)
        if self.windowW > SystemWidth or self.windowH > SystemHeight - SystemHeight * 0.08:
            self.adjustTileSize()
            self.image_init()
        else:
            if self.tileSize > prevSize:
                self.image_init()

        self.optionIconPos = (self.windowW / 2 - 32, self.windowH - self.controlboarderHeight + 5)
        self.optionIconRect = pygame.rect.Rect(self.optionIconPos, (64,64))
        self.image["bg"] = pygame.image.load("Img\\bg.jpg")
        self.image["bg"] = pygame.transform.scale(self.image["bg"], (self.windowW, self.windowH))

        self.optionYESPos = (self.windowW / 2 - 74, self.windowH - (self.windowH - self.optionWindowH)/2 - 74)
        self.optionNOPos = (self.windowW / 2 + 10, self.windowH - (self.windowH - self.optionWindowH)/2 - 74)
        self.optionYESRect = pygame.rect.Rect(self.optionYESPos, (64, 64))
        self.optionNORect = pygame.rect.Rect(self.optionNOPos, (64, 64))
        self.optionGridPos = (self.windowW / 2 - 160, self.windowH /2  - 114)
        self.optionBombCountPos = (self.windowW / 2 - 160, self.windowH /2  - 20 )
        self.resize_box1.rect.x, self.resize_box1.rect.y = self.optionGridPos[0] + 124 + 5 , self.optionGridPos[1]+ 5
        self.resize_box2.rect.x, self.resize_box2.rect.y = self.optionGridPos[0] + 252 + 5, self.optionGridPos[1]+ 5
        self.resize_box3.rect.x, self.resize_box3.rect.y = self.optionBombCountPos[0] + 124 + 5, self.optionBombCountPos[1]+ 5
        self.smile.rect.center = self.windowW / 2, self.boarderHeight / 2

        self.surface = pygame.display.set_mode((self.windowW, self.windowH))
        self.draw_background()
        sys.setrecursionlimit(self.width * self.height)

    def draw_background(self):
        # bg image
        self.surface.blit(self.image["bg"], (0,0))

        # timer image
        self.surface.blit(self.image["timer"], (self.windowW - 64, self.windowH - self.controlboarderHeight + 5))
        # self.windowW - self.boarderWidth - SystemWidth // 30

        # bombCount image
        self.surface.blit(self.image["bombCount"], (0, self.windowH - self.controlboarderHeight + 5))
        # self.boarderWidth

        # option image
        # print (self.boarderWidth, self.boarderWidth / 2)
        if self.onOptionIcon:
            self.surface.blit(self.image["optionBig"], (self.optionIconPos[0]-2, self.optionIconPos[1]-2))
        else:
            self.surface.blit(self.image["option"], self.optionIconPos)


    '''
    update those tiles that is mouse left clicked on
    '''
    def update_tile(self, i, j):
        if self.tileArray[i][j].state == TileState.revealed:
            # do nothing when hit a revealed tile or flagged tile
            return None
        elif self.tileArray[i][j].state == TileState.flagged:
            if self.tileArray[i][j].flag:
                # correctly flagged and should change img
                self.tileArray[i][j].image = self.image["correctflag"]
            else:
                # wrong flagged and should change img
                self.tileArray[i][j].image = self.image["wrongflag"]
        elif self.tileArray[i][j].flag:
            # change tile img when hit a bomb, and update gamestate
            self.tileArray[i][j].image = self.image["Bomb"]
            # change gamestate onlyu if this is caused by player input, not by automatic full update when game is finished
            if self.gameState ==  GameState.running:
                self.prevState = self.gameState
                self.gameState = GameState.lose
        elif self.tileArray[i][j].state == TileState.hidden or self.tileArray[i][j].state == TileState.marked:
            self.tileArray[i][j].state = TileState.revealed
            if self.tileArray[i][j].num > 0:
                self.tileArray[i][j].image = self.image["num"+ str(self.tileArray[i][j].num)]
            else:
                self.tileArray[i][j].image = self.image["empty"]
                for x in range(max(i-1, 0), min(i+2,self.width)):
                    for y in range(max(j-1, 0), min(j+2, self.height)):
                        condition = self.tileArray[x][y].state != TileState.revealed \
                                    and self.tileArray[x][y].state != TileState.flagged \
                                    and not self.tileArray[x][y].flag \
                                    and (x,y) != (i, j)
                        if condition:
                            self.update_tile(x, y)
            if self.tileArray[i][j].rect.x != self.tileSize * i + self.boarderWidth:
                self.updateTilePostion(i, j)

    def updateTilePostion(self, i, j):
        self.tileArray[i][j].rect = self.tileArray[i][j].image.get_rect()
        self.tileArray[i][j].rect.x = self.tileSize * i + self.boarderWidth - (self.tileArray[i][j].rect.width - self.tileSize)/2
        self.tileArray[i][j].rect.y = self.tileSize * j + self.boarderHeight - (self.tileArray[i][j].rect.height - self.tileSize)/2

    def handleRightButton(self, i, j):
        if i >= self.width or j >= self.height:
            # print ("Are u serious")
            return None
        if self.gameState != GameState.running and self.gameState != GameState.waiting:
            return None
        if self.gameState == GameState.waiting:
            self.gameState = GameState.running
        if self.tileArray[i][j].state == TileState.hidden:
            self.tileArray[i][j].state = TileState.flagged
            self.tileArray[i][j].image = self.image["flag"]
            self.bombLeft-=1
        elif self.tileArray[i][j].state == TileState.marked:
            self.tileArray[i][j].state = TileState.hidden
            self.tileArray[i][j].image = self.image["Hidden"]
        elif self.tileArray[i][j].state == TileState.flagged:
            self.tileArray[i][j].state = TileState.marked
            self.tileArray[i][j].image = self.image["marked"]
            self.bombLeft+=1
        self.updateTilePostion(i, j)

    def updateArrayWhenFinish(self):
        for i in range(self.width):
            for j in range(self.height):
                self.update_tile(i,j)

    def game_over(self):
        if self.gameState == GameState.lose:
            print ("You lose")
        elif self.gameState == GameState.win:
            print ("You win")
        self.updateArrayWhenFinish()

    # restarting current game, without changing minefield
    def restart(self):
        for i in range(self.width):
            for j in range(self.height):
                self.tileArray[i][j].state = TileState.hidden
                self.tileArray[i][j].image = self.image["Hidden"]
        self.clock = pygame.time.Clock()
        self.timer = 0
        self.dt = 0
        self.bombLeft = self.mine
        self.smile.image = self.image["normal"]

    # reset current game, changing minefield
    def reset(self):
        self.init_minefield()
        self.init_tilearray()
        self.clock = pygame.time.Clock()
        self.timer = 0
        self.dt = 0
        self.bombLeft = self.mine
        self.smile.image = self.image["normal"]

    def getBombsNear(self, i, j):
        count = 0
        wrong = False
        for x in range(max(i-1, 0), min(i+2,self.width)):
            for y in range(max(j-1, 0), min(j+2, self.height)):
                if self.tileArray[x][y].state == TileState.flagged:
                    count+=1
                    # print ("flagged at,",x," ", y)
                    if not self.tileArray[x][y].flag:
                        wrong = True
        return count, wrong

    def handleMiddleButton(self, i, j):
        if self.tileArray[i][j].state != TileState.revealed:
            return None
        # print ("here")
        bombsNearBy = self.tileArray[i][j].num
        markedNearBy, wrong = self.getBombsNear(i, j)
        # print (bombsNearBy, markedNearBy, wrong)
        if bombsNearBy == markedNearBy and not wrong:
            # print ("here1")
            for x in range(max(i-1, 0), min(i+2,self.width)):
                for y in range(max(j-1, 0), min(j+2, self.height)):
                    if self.tileArray[x][y].state == TileState.hidden or self.tileArray[x][y].state == TileState.marked:
                        self.update_tile(x, y)
        elif wrong:
            # print ("wrong info")
            self.prevState = self.gameState
            self.gameState = GameState.lose
            self.smile.image = self.image["lose"]
            self.game_over()
        else:
            self.updateSurroundingTileImage(i, j)
            # print ("not enough info")

    def checkGameFinished(self):
        for i in range(0, self.width):
            for j in range(0, self.height):
                if not self.tileArray[i][j].flag and self.tileArray[i][j].state != TileState.revealed:
                    return False
        return True

    def handleKeyDown(self, key):
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif key == pygame.K_r:
            # print ("r pressed")
            self.restart()
            self.prevState = self.gameState
            self.gameState = GameState.waiting
        elif key == pygame.K_g:
            self.reset()
            self.prevState = self.gameState
            self.gameState = GameState.waiting
        elif key == pygame.K_o:
            self.prevState = self.gameState
            self.gameState = GameState.option


    def getMouseIndexOnArray(self, mousePos):
        r = pygame.rect.Rect(mousePos, (1,1))
        posX, posY = -1, -1     # representing invalid index
        if self.gameState != GameState.option and r.colliderect(self.optionIconRect):
             # representing option menu icon clicked
            # print ("Click on option")
            posX, posY = -2, -2
        elif self.gameState == GameState.running or self.gameState == GameState.waiting:
            if r.colliderect(self.smile.rect):
                # restart through smile icon
                posX, posY = -5, -5
                return tuple((posX, posY))
            else:
                for i in range(0, self.width):
                    for j in range(0, self.height):
                        if r.colliderect(self.tileArray[i][j].rect):
                            posX, posY = i,j
                            return tuple((posX, posY))
        elif self.gameState == GameState.option:
            if r.colliderect(self.optionYESRect):
                posX, posY = -3, -3        # representing option menu YES icon clicked
            elif r.colliderect(self.optionNORect):
                posX, posY = -4, -4        # representing option menu NO icon clicked
        elif self.gameState == GameState.win or self.gameState == GameState.lose:
            if r.colliderect(self.smile.rect):
                # restart through smile icon
                posX, posY = -5, -5

        return tuple((posX, posY))

    def drawOption(self):
        # option window bg
        self.surface.blit(self.image["optionBG"], ((self.windowW - self.optionWindowW)/2, (self.windowH - self.optionWindowH)/2))
        # yes icon
        self.surface.blit(self.image["YES"], self.optionYESPos)
        # no icon
        self.surface.blit(self.image["NO"], self.optionNOPos)
        # grid adjustment
        self.surface.blit(self.image["grid"], self.optionGridPos)
        # input box
        self.surface.blit(self.image["input"], (self.optionGridPos[0] + 124, self.optionGridPos[1]))
        self.surface.blit(self.image["input"], (self.optionGridPos[0] + 252, self.optionGridPos[1]))
        # Xmark
        self.surface.blit(self.image["X"], (self.optionGridPos[0] + 188, self.optionGridPos[1]))
        # bomb number
        self.surface.blit(self.image["bombCount"], self.optionBombCountPos)
        # input box
        self.surface.blit(self.image["input"], (self.optionBombCountPos[0] + 124, self.optionBombCountPos[1]))
        for box in self.input_boxes:
            box.update()
        for box in self.input_boxes:
            box.draw(self.surface)

    def handleOption(self, event):
        for box in self.input_boxes:
            box.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.leftmouseDownPos = self.getMouseIndexOnArray(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                # print (self.leftmouseDownPos)
                if self.leftmouseDownPos == (-1, -1) or self.leftmouseDownPos == (-2, -2) or self.leftmouseDownPos != self.getMouseIndexOnArray(pygame.mouse.get_pos()):
                    pass
                    # print ("leftMouse moved")
                else:
                    if self.leftmouseDownPos == (-3, -3):
                        # clicked on YES button
                        # print ("YES", self.prevState)
                        self.prevState = self.gameState
                        self.gameState = GameState.waiting
                        if (int(self.resize_box1.text) > 50 or int(self.resize_box1.text) < 10 or int(self.resize_box2.text) < 6 or int(self.resize_box3.text) > int(self.resize_box1.text) * int(self.resize_box2.text) or int(self.resize_box2.text) > 24):
                            pass
                            # print ("Invalid Input")
                        else:
                            # check if screen width > maximum
                            self.width = int(self.resize_box1.text)
                            self.height = int(self.resize_box2.text)
                            self.mine = int(self.resize_box3.text)
                            self.update_window()
                            self.reset()
                    elif self.leftmouseDownPos == (-4, -4):
                        # clicked on NO button
                        # print ("no", self.prevState)
                        self.gameState = self.prevState
    # update surrounding hidden tiles as pressed down
    def updateSurroundingTileImage(self, i, j):
        if self.tileArray[i][j].state != TileState.revealed or self.tileArray[i][j].num <= 0:
            return None
        for x in range(max(i-1, 0), min(i+2,self.width)):
            for y in range(max(j-1, 0), min(j+2, self.height)):
                if self.tileArray[x][y].state == TileState.hidden:
                    if self.tileArray[x][y].image == self.image["Hidden"]:
                        self.tileArray[x][y].image = self.image["tileDown"]
                    elif self.tileArray[x][y].image == self.image["tileDown"]:
                        self.tileArray[x][y].image = self.image["Hidden"]
    def handleMouse(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN and event.type != pygame.MOUSEBUTTONUP:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.leftmouseDownPos = self.getMouseIndexOnArray(pygame.mouse.get_pos())
                self.leftMouseDown = True
                #print (self.midmouseDownPos)
                if self.leftmouseDownPos[0] >= 0 and (self.gameState == GameState.running or self.gameState == GameState.waiting):
                    #print (self.midmouseDownPos[0] >= 0)
                    self.smile.image = self.image["hit1"]
                    if self.tileArray[self.leftmouseDownPos[0]][self.leftmouseDownPos[1]].state == TileState.hidden:
                        self.tileArray[self.leftmouseDownPos[0]][self.leftmouseDownPos[1]].image = self.image["tileDown"]
                        self.updateTilePostion(self.leftmouseDownPos[0], self.leftmouseDownPos[1])
                    if self.tileArray[self.leftmouseDownPos[0]][self.leftmouseDownPos[1]].state == TileState.revealed and\
                            self.tileArray[self.leftmouseDownPos[0]][self.leftmouseDownPos[1]].num > 0 and\
                            self.leftMousetimer == 0:
                        self.leftMousetimer = 0.001
                    elif self.tileArray[self.leftmouseDownPos[0]][self.leftmouseDownPos[1]].state == TileState.revealed and\
                                    self.tileArray[self.leftmouseDownPos[0]][self.leftmouseDownPos[1]].num > 0 and\
                                    self.leftMousetimer>0 and self.leftMousetimer < 0.3:
                        # print (self.leftMousetimer)
                        self.handleMiddleButton(self.leftmouseDownPos[0], self.leftmouseDownPos[1])
                        self.leftMousetimer = 0
            elif event.button == 2:
                self.midmouseDownPos = self.getMouseIndexOnArray(pygame.mouse.get_pos())
                self.midMouseDown = True
                # print (self.midmouseDownPos)
                if self.midmouseDownPos[0] >= 0 and self.tileArray[self.midmouseDownPos[0]][self.midmouseDownPos[1]].state == TileState.revealed:
                    # print (self.midmouseDownPos[0] >= 0)
                    if self.gameState == GameState.running:
                        self.smile.image = self.image["hit"]
                        self.updateSurroundingTileImage(self.midmouseDownPos[0], self.midmouseDownPos[1])
            elif event.button == 3:
                self.rightmouseDownPos = self.getMouseIndexOnArray(pygame.mouse.get_pos())
                if self.tileArray[self.rightmouseDownPos[0]][self.rightmouseDownPos[1]].state == TileState.revealed and\
                            self.tileArray[self.rightmouseDownPos[0]][self.rightmouseDownPos[1]].num > 0 and\
                            self.leftMousetimer == 0:
                    self.leftMousetimer = 0.001
                elif self.tileArray[self.rightmouseDownPos[0]][self.rightmouseDownPos[1]].state == TileState.revealed and\
                                self.tileArray[self.rightmouseDownPos[0]][self.rightmouseDownPos[1]].num > 0 and\
                                self.leftMousetimer>0 and self.leftMousetimer < 0.3:
                    # print (self.leftMousetimer)
                    self.handleMiddleButton(self.rightmouseDownPos[0], self.rightmouseDownPos[1])
                    self.leftMousetimer = 0
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                # print (self.leftmouseDownPos, self.getMouseIndexOnArray(pygame.mouse.get_pos()))
                curPos = self.getMouseIndexOnArray(pygame.mouse.get_pos())
                if curPos == (-1, -1):
                    if self.gameState == GameState.running or self.gameState == GameState.waiting:
                        self.smile.image = self.image["normal"]
                    # print ("leftMouse moved")
                else:
                    if self.leftmouseDownPos == (-2, -2) and self.leftmouseDownPos == self.getMouseIndexOnArray(pygame.mouse.get_pos()):
                        # clicked on option
                        self.onOptionIcon = False
                        self.prevState = self.gameState
                        self.gameState = GameState.option
                        if self.leftmouseDownPos[0] >= 0:
                            if self.tileArray[self.leftmouseDownPos[0]][self.leftmouseDownPos[1]].state == TileState.hidden:
                                self.tileArray[self.leftmouseDownPos[0]][self.leftmouseDownPos[1]].image = self.image["Hidden"]
                    elif self.leftmouseDownPos == (-5, -5) and self.leftmouseDownPos == self.getMouseIndexOnArray(pygame.mouse.get_pos()):
                        # clicked on smile icon
                        if self.leftmouseDownPos[0] >= 0:
                            if self.tileArray[self.leftmouseDownPos[0]][self.leftmouseDownPos[1]].state == TileState.hidden:
                                self.tileArray[self.leftmouseDownPos[0]][self.leftmouseDownPos[1]].image = self.image["Hidden"]
                        self.reset()
                        self.prevState = self.gameState
                        self.gameState = GameState.waiting
                    else:
                        # update current index
                        curPos = self.getMouseIndexOnArray(pygame.mouse.get_pos())
                        if curPos[0] >= 0:
                            # clicked on tile while waiting or running
                            if self.gameState == GameState.waiting:
                                self.prevState = self.gameState
                                self.gameState = GameState.running
                            if self.gameState == GameState.running:
                                self.smile.image = self.image["normal"]
                                if self.tileArray[curPos[0]][curPos[1]].state == TileState.hidden or\
                                                self.tileArray[curPos[0]][curPos[1]].state == TileState.marked:
                                    self.update_tile(curPos[0], curPos[1])

                                if self.gameState == GameState.lose:
                                    self.smile.image = self.image["lose"]
                                    self.game_over()
                self.leftMouseDown = False
            elif event.button == 2:
                self.midMouseDown = False
                if self.gameState == GameState.running:
                    self.smile.image = self.image["normal"]
                    # update current index
                    curPos = self.getMouseIndexOnArray(pygame.mouse.get_pos())
                    self.handleMiddleButton(curPos[0],curPos[1])
            elif event.button == 3:
                curPos = self.getMouseIndexOnArray(pygame.mouse.get_pos())
                if curPos[0] >= 0:
                    self.handleRightButton(curPos[0], curPos[1])
                    # print ("rightMouse moved")
                else:
                    # print ("in handle")
                    pass
            if self.checkGameFinished():
                if self.gameState == GameState.running:
                    self.prevState = self.gameState
                    self.gameState = GameState.win
                    self.smile.image = self.image["win"]
                    self.game_over()

    def handleMotion(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.curIndex = self.getMouseIndexOnArray(pygame.mouse.get_pos())
        else:
            return None
        if self.curIndex != self.prevTile:
            # left mouse hold
            if self.leftMouseDown and (self.gameState == GameState.waiting or self.gameState == GameState.running):
                if self.prevTile[0] >= 0 and self.tileArray[self.prevTile[0]][self.prevTile[1]].state == TileState.hidden:
                    self.tileArray[self.prevTile[0]][self.prevTile[1]].image = self.image["Hidden"]
                    self.updateTilePostion(self.prevTile[0], self.prevTile[1])
                if self.curIndex[0] >= 0 and self.tileArray[self.curIndex[0]][self.curIndex[1]].state == TileState.hidden:
                    self.tileArray[self.curIndex[0]][self.curIndex[1]].image = self.image["tileDown"]
                    self.updateTilePostion(self.curIndex[0], self.curIndex[1])
            # mid mouse hold
            elif self.midMouseDown and (self.gameState == GameState.running):
                if self.prevTile[0] >= 0 and self.tileArray[self.prevTile[0]][self.prevTile[1]].state == TileState.revealed \
                        and self.tileArray[self.prevTile[0]][self.prevTile[1]].num > 0:
                    self.updateSurroundingTileImage(self.prevTile[0], self.prevTile[1])
                if self.curIndex[0] >= 0 and self.tileArray[self.curIndex[0]][self.curIndex[1]].state == TileState.revealed \
                        and self.tileArray[self.curIndex[0]][self.curIndex[1]].num > 0:
                    self.updateSurroundingTileImage(self.curIndex[0], self.curIndex[1])
            # no mouse button hold
            else:
                if self.prevTile[0] >= 0 and self.tileArray[self.prevTile[0]][self.prevTile[1]].state == TileState.hidden\
                        and (self.gameState == GameState.waiting or self.gameState == GameState.running):
                    self.tileArray[self.prevTile[0]][self.prevTile[1]].image = self.image["Hidden"]
                    self.updateTilePostion(self.prevTile[0], self.prevTile[1])
                if self.curIndex[0] >= 0 and self.tileArray[self.curIndex[0]][self.curIndex[1]].state == TileState.hidden\
                        and (self.gameState == GameState.waiting or self.gameState == GameState.running):
                    self.tileArray[self.curIndex[0]][self.curIndex[1]].image = self.image["Hidden1"]
                    self.updateTilePostion(self.curIndex[0], self.curIndex[1])
                # option button effect
                if self.curIndex == tuple((-2,-2)):
                    self.onOptionIcon = True
                else:
                    self.onOptionIcon = False
                if self.curIndex == tuple((-5, -5)):
                    self.onSmileIcon = True
                else:
                    self.onSmileIcon = False
            self.prevTile = self.curIndex
        elif self.curIndex == self.prevTile:
            pass

    # resolve middle mouse button tap and move between tiles cause desynchronized tile image
    def refreshBoard(self):
        if self.gameState != GameState.running or self.leftMouseDown:
            return None
        if self.midMouseDown and self.curIndex[0]>= 0 and self.tileArray[self.curIndex[0]][self.curIndex[1]].num > 0:
            return None
        for i in range(self.width):
            for j in range(self.height):
                if self.tileArray[i][j].state == TileState.hidden and tuple((i,j)) != self.curIndex:
                    self.tileArray[i][j].image = self.image["Hidden"]
                    self.updateTilePostion(i,j)

    def updateSmileIcon(self):
        if self.onSmileIcon:
            if self.gameState == GameState.win:
                self.smile.image = self.image["winBig"]
                self.smile.rect = self.smile.image.get_rect()
                self.smile.rect.center = self.windowW / 2, self.boarderHeight / 2
            elif self.gameState == GameState.lose:
                self.smile.image = self.image["loseBig"]
                self.smile.rect = self.smile.image.get_rect()
                self.smile.rect.center = self.windowW / 2, self.boarderHeight / 2
            elif self.gameState == GameState.running or self.gameState == GameState.waiting:
                self.smile.image = self.image["normalBig"]
                self.smile.rect = self.smile.image.get_rect()
                self.smile.rect.center = self.windowW / 2, self.boarderHeight / 2
        else:
            if self.smile.rect.x == self.windowW / 2 - 32:
                pass
            else:
                if self.gameState == GameState.win:
                    self.smile.image = self.image["win"]
                    self.smile.rect = self.smile.image.get_rect()
                    self.smile.rect.center = self.windowW / 2, self.boarderHeight / 2
                elif self.gameState == GameState.lose:
                    self.smile.image = self.image["lose"]
                    self.smile.rect = self.smile.image.get_rect()
                    self.smile.rect.center = self.windowW / 2, self.boarderHeight / 2
                elif self.gameState == GameState.running or self.gameState == GameState.waiting:
                    self.smile.image = self.image["normal"]
                    self.smile.rect = self.smile.image.get_rect()
                    self.smile.rect.center = self.windowW / 2, self.boarderHeight / 2

    def run(self):
        self.leftmouseDownPos = (-1,-1)
        self.rightmouseDownPos = (-1,-1)
        self.clock = pygame.time.Clock()
        self.timer = 0
        self.dt = 0
        # self.update_window()
        while True:
            # mouse_pressed = pygame.mouse.get_pressed()
            # print (self.prevState, self.gameState)
            # print (self.tileSize, self.boarderWidth)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if self.gameState == GameState.waiting:
                    # when the game has not started, only available operation is to
                    # 1. click on tiles(left, right), 2. click on option, 3. press key r, g
                    if event.type == pygame.KEYDOWN:
                        self.handleKeyDown(event.key)
                        break
                    self.handleMotion(event)
                    self.handleMouse(event)

                elif self.gameState == GameState.running:
                    # when the game has started, only available operation is to
                    # 1. click on tiles(left, right middle), 2. click on option, 3. press key r, g
                    if event.type == pygame.KEYDOWN:
                        self.handleKeyDown(event.key)
                        break
                    self.handleMotion(event)
                    self.handleMouse(event)
                elif self.gameState == GameState.option:
                    # when the game has paused at option, only available operation is to
                    # 1. click on option rectangles, 2. click on confirm or cancel rectangle
                    self.handleOption(event)
                elif self.gameState == GameState.win or self.gameState == GameState.lose:
                    # when the game has finished by winning or losing, only available operation is to
                    # 1. click on option, 2. press key r, g
                    if event.type == pygame.KEYDOWN:
                        self.handleKeyDown(event.key)
                        break

                    self.handleMotion(event)
                    self.handleMouse(event)
                else:
                    pass
            self.updateSmileIcon()

            self.refreshBoard()
            self.surface.fill(WHITE)
            self.draw_background()
            self.all_sprites.update()
            self.all_sprites.draw(self.surface)

            # timer and bombleft tracking
            if self.gameState == GameState.running:
                self.timer += self.dt
            if self.timer > 999:
                self.timer = 999

            # internal timer for double mouse click
            if self.leftMousetimer != 0:
                self.leftMousetimer += self.dt
                # print (self.leftMousetimer)
                # Reset after 0.3 seconds.
                if self.leftMousetimer >= 0.3:
                    # print('too late')
                    self.leftMousetimer = 0

            # display Bombs left
            BombLeftDis = self.myfont.render(str(self.bombLeft), False, (0, 0, 0))
            self.surface.blit(BombLeftDis,(70, self.windowH - self.controlboarderHeight + 5))
            # self.boarderWidth + 70

            # display timer
            timerDis = self.myfont.render(str(int(self.timer)), False, (0, 0, 0))
            self.surface.blit(timerDis,(self.windowW - 150, self.windowH - self.controlboarderHeight + 5))
            # self.windowW - self.boarderWidth - 160

            if self.gameState == GameState.option:
                self.drawOption()

            pygame.display.update()
            self.dt = self.clock.tick(30) / 1000
            # print (pygame.time.Clock.get_fps())

if __name__ == "__main__":
    ms = MyMineSweeper()
    ms.run()
