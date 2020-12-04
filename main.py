import copy
import sys
import numpy as np

# Board
NUM_COLS = 6
WHITEDUKE = 1
WHITEFOOTMAN = 2
EMPTY = 0
BLACKDUKE = -1
BLACKFOOTMAN = -2

printable = {
    EMPTY: "[-]",
    WHITEDUKE: "[WD]",
    WHITEFOOTMAN: "[WF]",
    BLACKDUKE: "[BD]",
    BLACKFOOTMAN: "[BF]"
}

WHITE_TO_PLAY = True

SQUAREPLACEMENT = [(1, 0), (-1, 0), (0, 1), (0, -1)]

# Directions for units
MOVE = 0
JUMP = 1
SLIDE = 2
DUKEUP = [(-1, 0, SLIDE), (1, 0, SLIDE)]
DUKEDOWN = [(0, 1, SLIDE), (0, -1, SLIDE)]

FOOTMANUP = [(1, 0, MOVE), (-1, 0, MOVE), (0, 1, MOVE), (0, -1, MOVE)]
FOOTMANDOWN = [(1, 1, MOVE), (1, -1, MOVE), (-1, -1, MOVE), (-1, 1, MOVE), (0, -2, MOVE)]


class Tile:
    def __init__(self, type, upMoves, downMoves):
        self.type = type
        self.upMoves = upMoves
        self.downMoves = downMoves
        self.isUp = True


# Example tiles
EMPTYTILE = Tile(EMPTY, 0, 0)
WHITEDUKETILE = Tile(WHITEDUKE, DUKEUP, DUKEDOWN)
WHITEFOOTMANTILE = Tile(WHITEFOOTMAN, FOOTMANUP, FOOTMANDOWN)
BLACKFOOTMANTILE = Tile(BLACKFOOTMAN, FOOTMANUP, FOOTMANDOWN)

BLACKDUKETILE = Tile(BLACKDUKE, DUKEUP, DUKEDOWN)


def gen_legal_moves(board, row, col):
    tile = board.board[row][col]
    legal_moves = []
    validDirs = []
    if tile.isUp:
        validDirs = tile.upMoves
    else:
        validDirs = tile.downMoves
    for x_delta, y_delta, moveType in validDirs:
        if tile.type < 0:
            y_delta *= -1
        if (col + x_delta < 0) or (col + x_delta >= NUM_COLS):
            continue
        if (row + y_delta < 0) or (row + y_delta >= NUM_COLS):
            continue
        if moveType == MOVE:
            x_index = 0
            y_index = 0
            validMove = True
            x_factor = 1
            if x_delta < 0:
                x_factor = -1
            y_factor = 1
            if y_delta < 0:
                y_factor = -1
            while x_index < abs(x_delta) or y_index < abs(y_delta):
                if board.board[row + (y_index * y_factor)][col + (x_index * x_factor)] != EMPTYTILE and (
                        x_index != 0 and y_index != 0):
                    validMove = False
                if x_index != abs(x_delta):
                    x_index += 1
                if y_index != abs(y_delta):
                    y_index += 1
            if validMove == True:
                targetType = board.board[row + y_delta][col + x_delta].type
                if targetType == EMPTY or (targetType < EMPTY and tile.type > EMPTY) or (
                        targetType > EMPTY and tile.type < EMPTY):
                    legal_moves.append((row + y_delta, col + x_delta))
        if moveType == JUMP:
            targetType = board.board[row + y_delta][col + x_delta].type
            if targetType == EMPTY or (targetType < EMPTY and tile.type > EMPTY) or (
                    targetType > EMPTY and tile.type < EMPTY):
                legal_moves.append((row + y_delta, col + x_delta))
        if moveType == SLIDE:
            x_index = x_delta
            y_index = y_delta
            stop = False
            while not stop:
                x_pos = col + x_index
                y_pos = row + y_index
                if (x_pos < 0) or (x_pos >= NUM_COLS):
                    stop = True
                    continue
                if (y_pos < 0) or (y_pos >= NUM_COLS):
                    stop = True
                    continue
                targetType = board.board[y_pos][x_pos].type
                if targetType == EMPTY:
                    legal_moves.append(((y_pos, x_pos)))
                    x_index += x_delta
                    y_index += y_delta
                elif (targetType < EMPTY and tile.type > EMPTY) or (targetType > EMPTY and tile.type < EMPTY):
                    legal_moves.append(((y_pos, x_pos)))
                    stop = True
                    continue
                else:
                    stop = True
    return legal_moves


class Board:
    def __init__(self, size):
        self.board = [[EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE],
                      [EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE],
                      [EMPTYTILE, EMPTYTILE, BLACKFOOTMANTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE],
                      [EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE],
                      [EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE],
                      [EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE]]

    def print_board(self):
        for row in range(NUM_COLS):
            line = ""
            for col in range(NUM_COLS):
                line += printable[self.board[row][col].type]
            print(line)
        print("\n")


def showPotentialMoves(board, moves):
    for row in range(NUM_COLS):
        line = ""
        for col in range(NUM_COLS):
            if (row, col) in moves:
                line += "[" + str(moves.index((row, col))) + "]"
            else:
                line += printable[board.board[row][col].type]
        print(line)
    print("\n")


# Will move the unit to the move position based on the assumption it is a legal move and return the new board
def moveUnit(board, move, row, col):
    newState = copy.deepcopy(board)
    toMove = newState.board[row][col]
    newState.board[move[0]][move[1]] = toMove
    newState.board[row][col] = EMPTYTILE
    toMove.isUp = not toMove.isUp
    return newState

def placeUnit(board, placement, Tile):
    newState = copy.deepcopy(board)
    newState.board[placement[0]][placement[1]] = Tile
    return newState

# Will give a list of valid placements based on whos turn it is and where the duke is
def gen_legal_placements(board):
    target = (0, 0)
    for row in range(NUM_COLS):
        for col in range(NUM_COLS):
            if WHITE_TO_PLAY:
                if board.board[row][col].type == WHITEDUKE:
                    target = (row, col)
            else:
                if board.board[row][col].type == BLACKDUKE:
                    target = (row, col)
    legal_placements = []
    for x_delta, y_delta in SQUAREPLACEMENT:
        if (target[1] + x_delta < 0) or (target[1] + x_delta >= NUM_COLS):
            continue
        if (target[0] + y_delta < 0) or (target[0] + y_delta >= NUM_COLS):
            continue
        if board.board[target[0] + y_delta][target[1] + x_delta].type == EMPTY:
            legal_placements.append((target[0] + y_delta, target[1] + x_delta))
    return legal_placements


def play():
    GAMEBOARD = Board(NUM_COLS)
    startingCol = int(input("Enter the column of your Duke (0 - 5): "))
    GAMEBOARD = placeUnit(GAMEBOARD, (5, startingCol), WHITEDUKETILE)
    GAMEBOARD.print_board()
    footman1Options = gen_legal_placements(GAMEBOARD)
    showPotentialMoves(GAMEBOARD, footman1Options)
    moveIndex = int(input("Select where you would like to place your first footman (0 - " + str(len(footman1Options) - 1) + "): "))
    GAMEBOARD = placeUnit(GAMEBOARD, footman1Options[moveIndex], WHITEFOOTMANTILE)
    GAMEBOARD.print_board()
    footman2Options = gen_legal_placements(GAMEBOARD)
    showPotentialMoves(GAMEBOARD, footman2Options)
    moveIndex = int(input("Select where you would like to place your second footman (0 - " + str(len(footman1Options) - 1) + "): "))
    GAMEBOARD = placeUnit(GAMEBOARD, footman2Options[moveIndex], WHITEFOOTMANTILE)
    gameOver = False
    while not gameOver:
        GAMEBOARD.print_board()
        action = int(input("Choose One:\n Move: 0\n Pull from bag: 1\n"))
        if action == 0:
            col = int(input("Enter the column of the piece to move: "))
            row = NUM_COLS - 1 - int(input("Enter the row of the piece to move: "))
            moveOptions = gen_legal_moves(GAMEBOARD, row, col)
            showPotentialMoves(GAMEBOARD, moveOptions)
            moveIndex = int(input("Select where you would like to move this unit to(0 - " + str(len(moveOptions) - 1) + "): "))
            GAMEBOARD = moveUnit(GAMEBOARD, moveOptions[moveIndex], row, col)
            WHITE_TO_PLAY = False
        if action == 1:
            #print("TODO: Handle bag drawing logic")
            WHITE_TO_PLAY = False


play()
#GAMEBOARD = Board(NUM_COLS)
#GAMEBOARD.print_board()
#placements = gen_legal_placements(GAMEBOARD)
#showPotentialMoves(GAMEBOARD, placements)
#GAMEBOARD = placeUnit(GAMEBOARD, placements[0], WHITEFOOTMANTILE)
#GAMEBOARD.print_board()
#moves = gen_legal_moves(GAMEBOARD, GAMEBOARD.board[2][2], 2, 2)
#showPotentialMoves(GAMEBOARD, moves)
#GAMEBOARD = moveUnit(GAMEBOARD, moves[2], 2, 2)
#GAMEBOARD.print_board()
#moves = gen_legal_moves(GAMEBOARD, GAMEBOARD.board[2][3], 2, 3)
#showPotentialMoves(GAMEBOARD, moves)



