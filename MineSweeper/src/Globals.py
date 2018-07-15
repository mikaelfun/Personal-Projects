
import enum
import sys
boardW = 16
boardH = 8
bombNum = 20
STDTILESIZE = 64
sys.setrecursionlimit(boardW * boardH)




class GameState(enum.Enum):
    waiting = 0
    running = 1
    stopped = 2
