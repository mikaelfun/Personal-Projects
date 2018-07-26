import enum

class GameState(enum.Enum):
    waiting = 0
    running = 1
    win = 3
    lose = 4
    option = 5
