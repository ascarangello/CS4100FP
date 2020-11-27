import copy
import sys
import numpy as np

#Board
NUM_COLS = 6
WHITE = 1
EMPTY = 0
BLACK = -1
WHITE_TO_PLAY = True

#Tiles
DUKE = 0
FOOTMAN = 1

#Directions for units
MOVE = 0
JUMP = 1
SLIDE = 2
DUKEUP = [(-1, 0, SLIDE), (1, 0, SLIDE)]
DUKEDOWN = [(0, 1, SLIDE), (0, -1, SLIDE)]

FOOTMANUP = [(1, 0, MOVE), (-1, 0, MOVE), (0, 1, MOVE), (0, -1, MOVE)]
FOOTMANDOWN = [(1, 1, MOVE), (1, -1, MOVE), (-1, -1, MOVE), (-1, 1, MOVE), (0, 2, MOVE)]



class Tile:
    def __init__(self, type, team, upMoves, downMoves):
        self.type = type
        self.team = team
        self.upMoves = upMoves
        self.downMoves = downMoves
        self.isUp = True

class Board:
    def __init__(self, size):
        self.board = np.zeros((size, size))

    def print_board(self):
        printable = {
            0: "-",
            1: "W",
            -1: "B"
        }
        for row in range(NUM_COLS):
            line = ""
            for col in range(NUM_COLS):
                line += printable[self.board[row][col]]
            print(line)

#Example tiles
testDuke = Tile(DUKE, WHITE, DUKEUP, DUKEDOWN)
testFootman = Tile(FOOTMAN, BLACK, FOOTMANUP, FOOTMANDOWN)
