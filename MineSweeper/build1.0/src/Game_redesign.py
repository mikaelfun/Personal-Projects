'''
Dev log:
1. Generating minefield
    generate random positions of bombs, generate numbers for each tile based on num of bombs around it
    tile has state [hidden, revealed, flagged, marked(?)]
2. Binding mouse event to reveal current tile, or explode
    left mouse but to reveal, right to flag, todo: right but to alternate between flag, marked, hidden
3. Expand if the current tile has no number using recursion
4. Check winning state after each loop
5. Adding smiley face button to restart game without mem leak!
6. Modify to make the board scalable    done
7. Adding timmer to time current game time played
8. Adding resize interface
9. Replace pygame.display.update() with more efficient way to update only changed dirty sprites
10. showing correct flag and wrong flag after gameover
'''

import pygame,sys
from Color import *
from Sprites import *
from MineField import *
from Globals import *
from InputBox import *

import ctypes
user32 = ctypes.windll.user32
REAL_SCREENWIDTH,REAL_SCREENHEIGHT = int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1)) - 80
class MineSweeper:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.x = boardW
        self.y = boardH
        self.n = bombNum
        self.boarderWidth = 40
        self.boarderHeight = 20

        self.screenWidth = self.x * STDTILESIZE + 2*self.boarderWidth
        self.screenHeight  = int((self.y * STDTILESIZE + 2*self.boarderHeight) *  32/27)
        self.windowHeight  = int(self.screenHeight * 5/ 32)
        self.surface = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        pygame.display.set_caption('Minesweeper')


        self.all_sprites = pygame.sprite.Group()
        # image
        self.image = {}
        self.image_init()
        self.smiley = ["smile", "hit", "win", "lose"]
        if (self.screenWidth - self.boarderWidth * 2) // self.x < (self.screenHeight - self.windowHeight - self.boarderHeight * 2) // self.y: # means more space vertically
            self.tileSize = int((self.screenWidth - self.boarderWidth * 2) // self.x)
            #self.boarderHeight = (screenHeight - self.tileSize * self.y - self.windowHeight)/2
            #self.boarderWidth = (screenWidth - self.tileSize  * self.x) / 2
        else:
            self.tileSize = int((self.screenHeight - self.windowHeight - self.boarderHeight * 2) // self.y)
            #self.boarderWidth = (self.screenWidth - self.tileSize  * self.x) / 2
            #self.boarderHeight = (self.screenHeight - self.tileSize * self.y - self.windowHeight)/2

        # print (screenWidth, screenHeight, windowHeight, self.boarderWidth, self.boarderHeight, self.tileSize)
        self.board = None

        self.myfont1 = pygame.font.SysFont('Comic Sans MS', 36)
        self.resize_box1 = InputBox(self.boarderWidth + (self.x/2 - 2) * self.tileSize , self.windowHeight / 2 + self.boarderHeight, 50, 50, str(self.x))
        self.resize_box2 = InputBox(self.boarderWidth + (self.x/2 ) * self.tileSize, self.windowHeight / 2+ self.boarderHeight , 50, 50,  str(self.y))
        self.resize_box3 = InputBox(self.boarderWidth + (self.x/2 + 2) * self.tileSize, self.windowHeight / 2+ self.boarderHeight, 50, 50, str(self.n))
        self.xMark = InputBox(self.boarderWidth + (self.x/2 - 1) * self.tileSize , self.windowHeight / 2+ self.boarderHeight, 50, 50, "X", False)


        self.input_boxes = [self.resize_box1, self.resize_box2, self.resize_box3, self.xMark]
        self.goMark = pygame.sprite.Sprite()
        self.goMark.image = self.image['GO']
        self.goMark.rect = self.goMark.image.get_rect()
        self.goMark.rect.x, self.goMark.rect.y = self.boarderWidth + (self.x/2 + 3) * self.tileSize , self.windowHeight / 2 + self.boarderHeight #self.windowHeight + self.boarderHeight - self.tileSize
        # self.all_sprites.add(self.goMark)

    def image_init(self):
        if len(self.image) != 0:
            del self.image
            self.image = {}
        self.image["Hidden"] = pygame.image.load('Img\\Tile64x64.png').convert_alpha()
        self.image["BombTile"] = pygame.image.load('Img\\Mine64z64.png').convert_alpha()
        self.image["flag"] = pygame.image.load('Img\\flag.png').convert_alpha()
        self.image["num1"] = pygame.image.load('Img\\num1.png').convert_alpha()
        self.image["num2"] = pygame.image.load('Img\\num2.png').convert_alpha()
        self.image["num3"] = pygame.image.load('Img\\num3.png').convert_alpha()
        self.image["num4"] = pygame.image.load('Img\\num4.png').convert_alpha()
        self.image["num5"] = pygame.image.load('Img\\num5.png').convert_alpha()
        self.image["num6"] = pygame.image.load('Img\\num6.png').convert_alpha()
        self.image["num7"] = pygame.image.load('Img\\num7.png').convert_alpha()
        self.image["num8"] = pygame.image.load('Img\\num8.png').convert_alpha()
        self.image["empty"] = pygame.image.load('Img\\emptyTile.png').convert_alpha()
        self.image["wrongflag"] = pygame.image.load('Img\\wrongflag.png').convert_alpha()
        self.image["correctflag"] = pygame.image.load('Img\\Mine3_256x256_32.png').convert_alpha()
        self.image["marked"] = pygame.image.load('Img\\Tile2.png').convert_alpha()
        self.image['GO'] = pygame.image.load('Img\\GO.png').convert_alpha()

        self.image["smile"] = pygame.image.load('Img\\smile1.png').convert_alpha()
        self.image["hit"] = pygame.image.load('Img\\hit1.png').convert_alpha()
        self.image["win"] = pygame.image.load('Img\\win.png').convert_alpha()
        self.image["lose"] = pygame.image.load('Img\\lose.png').convert_alpha()


    def updatebyPos(self,x,y, isHidden = False):
        # if self.board == None or self.board.tileArray == None or len(self.board.tileArray) <= x or len(self.board.tileArray[0]) <= y:
        #     return None
        if isHidden:
            self.board.tileArray[x][y].state = TileState.hidden
            self.board.tileArray[x][y].image = self.image["Hidden"]
        else:
            if self.board.tileArray[x][y].num == 0:
                if self.board.tileArray[x][y].flag and self.board.tileArray[x][y].state == TileState.hidden:
                    self.board.tileArray[x][y].image = self.image["BombTile"]
                elif self.board.tileArray[x][y].flag and self.board.tileArray[x][y].state == TileState.marked:
                    self.board.tileArray[x][y].image = self.image["BombTile"]
                elif self.board.tileArray[x][y].flag and self.board.tileArray[x][y].state == TileState.flagged:
                    self.board.tileArray[x][y].image = self.image["correctflag"]
                else:
                    self.board.tileArray[x][y].image = self.image["empty"]
            else:
                if self.board.tileArray[x][y].state == TileState.flagged:
                    self.board.tileArray[x][y].image = self.image["wrongflag"]
                else:
                    if self.board.tileArray[x][y].num == 1:
                        self.board.tileArray[x][y].image = self.image["num1"]
                    elif self.board.tileArray[x][y].num == 2:
                        self.board.tileArray[x][y].image = self.image["num2"]
                    elif self.board.tileArray[x][y].num == 3:
                        self.board.tileArray[x][y].image = self.image["num3"]
                    elif self.board.tileArray[x][y].num == 4:
                        self.board.tileArray[x][y].image = self.image["num4"]
                    elif self.board.tileArray[x][y].num == 5:
                        self.board.tileArray[x][y].image = self.image["num5"]
                    elif self.board.tileArray[x][y].num == 6:
                        self.board.tileArray[x][y].image = self.image["num6"]
                    elif self.board.tileArray[x][y].num == 7:
                        self.board.tileArray[x][y].image = self.image["num7"]
                    else:
                        self.board.tileArray[x][y].image = self.image["num8"]
            self.board.tileArray[x][y].state = TileState.revealed


    def expandbyPos(self, x, y):
        if self.board == None or self.board.tileArray == None or len(self.board.tileArray) <= x or len(self.board.tileArray[0]) <= y:
            return None
        if self.board.tileArray[x][y].flag or self.board.tileArray[x][y].state == TileState.revealed:
            return None
        if self.board.tileArray[x][y].num != 0:
            self.updatebyPos(x, y)
        else:
            # here 0 means all 8 tiles around it should not be bombs
            self.updatebyPos(x, y)
            # print ("HH ",x+2,self.x)
            for i in range(max(x-1, 0), min(x+2,self.x )):
                for j in range(max(y-1, 0), min(y+2, self.y)):
                    if (i,j) != (x,y) and self.board.tileArray[i][j].state != TileState.flagged and self.board.tileArray[i][j].state != TileState.revealed:
                        # print (i,j)
                        self.expandbyPos(i, j)

    def update_board(self):
        if self.board == None or self.board.smilyFace == None or self.board.tileArray == None or len(self.board.tileArray) < self.x or len(self.board.tileArray[0]) < self.y:
            return None
        self.image_init()
        for all in self.image:
            if all not in self.smiley:
                self.image[all] = pygame.transform.scale(self.image[all], (self.tileSize, self.tileSize))
            #print ("size after: ", self.image[all].get_rect.x)
        self.board.smilyFace.image = self.image["smile"]
        self.goMark.image = self.image['GO']
        # self.goMark.rect = self.goMark.image.get_rect()
        # self.goMark.rect.x, self.goMark.rect.y = self.boarderWidth + (self.x/2 + 3) * self.tileSize , self.windowHeight / 2 + self.boarderHeight #self.windowHeight + self.boarderHeight - self.tileSize)
        self.resize_box1.rect.x, self.resize_box1.rect.y = self.boarderWidth + (self.x/2 - 2) * self.tileSize , self.windowHeight / 2 + self.boarderHeight
        self.resize_box2.rect.x, self.resize_box2.rect.y = self.boarderWidth + (self.x/2 ) * self.tileSize, self.windowHeight / 2+ self.boarderHeight
        self.resize_box3.rect.x, self.resize_box3.rect.y = self.boarderWidth + (self.x/2 + 2) * self.tileSize, self.windowHeight / 2+ self.boarderHeight
        self.xMark.rect.x, self.xMark.rect.y = self.boarderWidth + (self.x/2 - 1) * self.tileSize , self.windowHeight / 2+ self.boarderHeight
        self.goMark.rect.x, self.goMark.rect.y = (self.boarderWidth + (self.x/2 + 3) * self.tileSize , self.windowHeight + self.boarderHeight - self.tileSize)

        for i in range(self.x):
            for j in range(self.y):
                self.updatebyPos(i,j, True)
        # pygame.display.update()

    def revealAll(self):
        if self.board == None or self.board.tileArray == None or len(self.board.tileArray) < self.x or len(self.board.tileArray[0]) < self.y:
            return None
        for i in range(0, self.x):
            for j in range(0, self.y):
                self.updatebyPos(i,j)

    def updateTileSize(self):
        if self.x * STDTILESIZE + 2 * self.boarderWidth <= REAL_SCREENWIDTH:
            if self.y * STDTILESIZE + 2 * self.boarderHeight <= REAL_SCREENHEIGHT - 100:
                # use std size
                self.tileSize = int(STDTILESIZE)
                self.screenWidth = int(self.x * self.tileSize + 2 * self.boarderWidth)
                self.screenHeight = int((self.y * self.tileSize + 2 * self.boarderHeight) + 100)
                self.windowHeight = 100
            else:
                # y is too big for screen size
                self.tileSize = int((REAL_SCREENHEIGHT -100 - self.boarderHeight * 2) // self.y)
                self.screenHeight = REAL_SCREENHEIGHT
                self.screenWidth = int(self.x * self.tileSize + 2 * self.boarderWidth)
                self.windowHeight = 100
        else:
            # x is too big for screen size
            self.tileSize = int((REAL_SCREENWIDTH - self.boarderWidth * 2) // self.x)
            self.screenWidth = REAL_SCREENWIDTH
            self.screenHeight = int((self.y * self.tileSize + 2 * self.boarderHeight) + 100)
            if self.screenHeight > REAL_SCREENHEIGHT:
                # need to go even smaller
                self.tileSize = int((REAL_SCREENHEIGHT - 100 - self.boarderHeight * 2) // self.y)
                self.screenHeight = REAL_SCREENHEIGHT
                self.screenWidth = int(self.x * self.tileSize + 2 * self.boarderWidth)
            self.windowHeight = 100

        sys.setrecursionlimit(self.x * self.y)

    def getBombsNear(self, i, j):
        count = 0
        wrong = False
        for x in range(max(i-1, 0), min(i+2,self.x)):
            for y in range(max(j-1, 0), min(j+2, self.y)):
                if self.board.tileArray[x][y].state == TileState.flagged:
                    count+=1
                    # print ("flagged at,",x," ", y)
                    if not self.board.tileArray[x][y].flag:
                        wrong = True
        return count, wrong

    def handleMiddleButton(self, i, j):
        if self.board.tileArray[i][j].state != TileState.revealed:
            return False
        bombsNearBy = self.board.tileArray[i][j].num
        actualNearBy, wrong = self.getBombsNear(i, j)
        # print (bombsNearBy, actualNearBy, wrong)
        if bombsNearBy == actualNearBy and not wrong:
            for x in range(max(i-1, 0), min(i+2,self.x)):
                for y in range(max(j-1, 0), min(j+2, self.y)):
                    if self.board.tileArray[x][y].state == TileState.hidden:
                        self.expandbyPos(x, y)
        elif bombsNearBy == actualNearBy and wrong:
            return True
        elif bombsNearBy > actualNearBy:
            print ("not enough info")
            return False
        else:
            print ("too much info")
            return True

        # print ("middel pressed")
    def display(self):
        self.board.display()
        self.goMark.update()
        self.all_sprites.add(self.goMark)
        self.all_sprites.draw(self.surface)

    def run(self):
        # self.updateTileSize()
        if self.board != None:
            pygame.sprite.Group().empty()
            del self.board
            self.board = MineField(self.all_sprites, self.surface, self.x, self.y, self.n, self.boarderWidth, self.boarderHeight, self.screenWidth, self.screenHeight ,self.tileSize)
        else:
            self.board = MineField(self.all_sprites, self.surface, self.x, self.y, self.n, self.boarderWidth, self.boarderHeight, self.screenWidth, self.screenHeight, self.tileSize)

        self.update_board()
        # self.board.display()
        game_state = GameState.waiting
        clock = pygame.time.Clock()
        timer = 0
        dt = 0
        bombLeft = self.n
        # print (self.tileSize)


        gameOver = False
        while True: # main game loop
            mouse_pressed = pygame.mouse.get_pressed()

            # display resize box
            for event in pygame.event.get():
                for box in self.input_boxes:
                    box.handle_event(event)

                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return self.run()
                elif mouse_pressed[1]:
                    # print("left and right clicked")
                    r = pygame.rect.Rect(pygame.mouse.get_pos(), (1,1))
                    for i in range(0, self.x):
                        for j in range(0, self.y):
                            if r.colliderect(self.board.tileArray[i][j].rect):
                                if self.handleMiddleButton(i, j):
                                    self.board.tileArray[i][j].image = self.image["BombTile"]
                                    self.revealAll()
                                    self.board.smilyFace.image = self.image["lose"]
                                    if game_state == GameState.running:
                                        game_state = GameState.stopped
                                break
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    r = pygame.rect.Rect(pygame.mouse.get_pos(), (1,1))
                    if (r.colliderect(self.goMark.rect)):
                        if (int(self.resize_box1.text) > 50 or int(self.resize_box1.text) < 10 or int(self.resize_box2.text) < 5 or int(self.resize_box3.text) > int(self.resize_box1.text) * int(self.resize_box2.text) or int(self.resize_box2.text) > 24):
                            print ("Invalid Input")
                            break
                        self.x = int(self.resize_box1.text)
                        self.y = int(self.resize_box2.text)
                        self.n = int(self.resize_box3.text)
                        self.updateTileSize()
                        #print (self.screenWidth, self.screenHeight, self.windowHeight)
                        #print (self.boarderWidth, self.boarderHeight)
                        self.surface = pygame.display.set_mode((self.screenWidth, self.screenHeight))
                        return self.run()
                    if gameOver:
                        break
                    for i in range(0, self.x):
                        for j in range(0, self.y):
                            if r.colliderect(self.board.tileArray[i][j].rect):
                                self.board.smilyFace.image = self.image["hit"]

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    r = pygame.rect.Rect(pygame.mouse.get_pos(), (1,1))
                    if r.colliderect(self.board.smilyFace.rect):
                        return self.run()
                    if gameOver:
                        break
                    self.board.smilyFace.image = self.image["smile"]
                    for i in range(0, self.x):
                        for j in range(0, self.y):
                            if r.colliderect(self.board.tileArray[i][j].rect):
                                if self.board.tileArray[i][j].state == TileState.revealed:
                                    break
                                elif self.board.tileArray[i][j].state != TileState.flagged and self.board.tileArray[i][j].flag == True:
                                    self.board.tileArray[i][j].image = self.image["BombTile"]
                                    self.revealAll()
                                    self.board.smilyFace.image = self.image["lose"]
                                    if game_state == GameState.running:
                                        game_state = GameState.stopped
                                    gameOver = True
                                elif self.board.tileArray[i][j].state != TileState.flagged:
                                    if game_state == GameState.waiting:
                                        game_state = GameState.running
                                    self.expandbyPos(i, j)
                                else:
                                    break
                                if self.board.checkGameWin(gameOver):
                                    self.board.smilyFace.image = self.image["win"]
                                    if game_state == GameState.running:
                                        game_state = GameState.stopped
                                    gameOver = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    if gameOver:
                        break
                    r = pygame.rect.Rect(pygame.mouse.get_pos(), (1,1))

                    for i in range(0, self.x):
                        for j in range(0, self.y):
                            if r.colliderect(self.board.tileArray[i][j].rect):
                                if self.board.tileArray[i][j].state == TileState.revealed:
                                    break
                                elif self.board.tileArray[i][j].state == TileState.flagged:
                                    self.board.tileArray[i][j].state = TileState.marked
                                    self.board.tileArray[i][j].image = self.image["marked"]
                                    bombLeft+=1
                                elif self.board.tileArray[i][j].state == TileState.marked:
                                    self.board.tileArray[i][j].state = TileState.hidden
                                    self.board.tileArray[i][j].image = self.image["Hidden"]
                                elif self.board.tileArray[i][j].state == TileState.hidden:
                                    self.board.tileArray[i][j].state = TileState.flagged
                                    self.board.tileArray[i][j].image = self.image["flag"]
                                    bombLeft-=1
                                else:
                                    break

                                if game_state == GameState.waiting:
                                    game_state = GameState.running
                                if self.board.checkGameWin(gameOver):
                                    self.board.smilyFace.image = self.image["win"]
                                    gameOver = True
                                    if game_state == GameState.running:
                                        game_state = GameState.stopped



            self.surface.fill(WHITE)
            # display board
            self.display()

            # diplay timer

            if game_state == GameState.running:
                timer += dt
            if timer > 999:
                timer = 999
            timerDis = self.myfont1.render(str(round(timer, 2)), False, (0, 0, 0))
            self.surface.blit(timerDis,(self.screenWidth - self.boarderWidth - 100, 10))

            # display Bombs left
            BombLeftDis = self.myfont1.render("Bombs left: "+str(bombLeft), False, (0, 0, 0))
            self.surface.blit(BombLeftDis,(self.boarderWidth, 10))
            # print (self.boarderWidth, self.boarderHeight)

            for box in self.input_boxes:
                box.update()
            for box in self.input_boxes:
                box.draw(self.surface)

            pygame.display.update()
            dt = clock.tick(30) / 1000

if __name__ == "__main__":
    myGame = MineSweeper()
    myGame.run()




