import copy
import random
from collections import defaultdict
import sys
import numpy as np

# Board
NUM_COLS = 6
WHITEDUKE = 1
WHITEFOOTMAN = 2
WHITEASSASSIN = 3
WHITEBOWMAN = 4
WHITECHAMPION = 5
WHITEDRAGOON = 6
EMPTY = 0
BLACKDUKE = -1
BLACKFOOTMAN = -2
BLACKASSASSIN = -3
BLACKBOWMAN = -4
BLACKCHAMPION = -5
BLACKDRAGOON = -6

printable = {
    EMPTY: "[--]",
    WHITEDUKE: "[WD]",
    BLACKDUKE: "[BD]",
    WHITEFOOTMAN: "[WF]",
    WHITEASSASSIN: "[WA]",
    BLACKFOOTMAN: "[BF]",
    BLACKASSASSIN: "[BA]",
    WHITEBOWMAN: "[WB]",
    BLACKBOWMAN: "[BB]",
    WHITECHAMPION: "[WC]",
    BLACKCHAMPION: "[BC]",
    WHITEDRAGOON: "[WDR]",
    BLACKDRAGOON: "[BDR]"
}


SQUAREPLACEMENT = [(1, 0), (-1, 0), (0, 1), (0, -1)]

# Directions for units
MOVE = 0
JUMP = 1
SLIDE = 2
JUMPSLIDE = 3
STRIKE = 4

DUKEUP = [(-1, 0, SLIDE), (1, 0, SLIDE)]
DUKEDOWN = [(0, 1, SLIDE), (0, -1, SLIDE)]

FOOTMANUP = [(1, 0, MOVE), (-1, 0, MOVE), (0, 1, MOVE), (0, -1, MOVE)]
FOOTMANDOWN = [(1, 1, MOVE), (1, -1, MOVE), (-1, -1, MOVE), (-1, 1, MOVE), (0, -2, MOVE)]

ASSASSINUP = [(0, -1, JUMPSLIDE), (-1, 1, JUMPSLIDE), (1, 1, JUMPSLIDE)]
ASSASSINDOWN = [(0, 1, JUMPSLIDE), (-1, -1, JUMPSLIDE), (1, -1, JUMPSLIDE)]

BOWMANUP = [(0, -1, MOVE), (1, 0, MOVE), (-1, 0, MOVE), (-2, 0, JUMP), (2, 0, JUMP), (0, 2, JUMP)]
BOWMANDOWN = [(0, -1, MOVE), (1, 1, MOVE), (-1, 1, MOVE), (0, -2, STRIKE), (1, -1, STRIKE), (-1, -1, STRIKE)]

CHAMPIONUP = [(1, 0, MOVE), (-1, 0, MOVE), (0, 1, MOVE), (0, -1, MOVE), (2, 0, JUMP), (-2, 0, JUMP), (0, 2, JUMP),
              (0, -2, JUMP)]
CHAMPIONDOWN = [(1, 0, STRIKE), (-1, 0, STRIKE), (0, 1, STRIKE), (0, -1, STRIKE), (2, 0, JUMP), (-2, 0, JUMP),
                (0, 2, JUMP), (0, -2, JUMP)]

DRAGOONUP = [(-1, 0, MOVE), (1, 0, MOVE), (0, -2, STRIKE), (-2, -2, STRIKE), (2, -2, STRIKE)]
DRAGOONDOWN = [(0, -1, MOVE), (0, -2, MOVE), (1, -2, JUMP), (-1, -2, JUMP), (-1, 1, SLIDE), (1, 1, SLIDE)]

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

WHITEASSASSINTILE = Tile(WHITEASSASSIN, ASSASSINUP, ASSASSINDOWN)
BLACKASSASSINTILE = Tile(BLACKASSASSIN, ASSASSINUP, ASSASSINDOWN)

WHITEBOWMANTILE = Tile(WHITEBOWMAN, BOWMANUP, BOWMANDOWN)
BLACKBOWMANTILE = Tile(BLACKBOWMAN, BOWMANUP, BOWMANDOWN)

WHITECHAMPIONTILE = Tile(WHITECHAMPION, CHAMPIONUP, CHAMPIONDOWN)
BLACKCHAMPIONTILE = Tile(BLACKCHAMPION, CHAMPIONUP, CHAMPIONDOWN)

WHITEDRAGOONTILE = Tile(WHITEDRAGOON, DRAGOONUP, DRAGOONDOWN)
BLACKDRAGOONTILE = Tile(BLACKDRAGOON, DRAGOONUP, DRAGOONDOWN)


# USE THIS TO GENERATE ALL LEGAL MOVES FOR A TILE AT THE GIVEN ROW AND COL
# RETURNS 2 ARRAYS, ONE OF THE DESTINATION ROW AND COLS OF ALL VALID MOVES
# SECOND ARRAY HAS THE TYPE OF MOVE, NEED THAT FOR MAKING MOVE
def gen_legal_moves(board, row, col, noDukeAttack):
    tile = board.board[row][col]
    isWhiteTile = tile.type // abs(tile.type)
    legal_moves = []
    moveTypes = []
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
                    if not noDukeAttack or (noDukeAttack and targetType != BLACKDUKE and targetType != WHITEDUKE):
                        legal_moves.append((row + y_delta, col + x_delta))
                        moveTypes.append(moveType)

        if moveType == JUMP:
            targetType = board.board[row + y_delta][col + x_delta].type
            if targetType == EMPTY or (targetType < EMPTY and tile.type > EMPTY) or (
                    targetType > EMPTY and tile.type < EMPTY):
                if not noDukeAttack or (noDukeAttack and targetType != BLACKDUKE and targetType != WHITEDUKE):
                    legal_moves.append((row + y_delta, col + x_delta))
                    moveTypes.append(moveType)

        if moveType == STRIKE:
            targetType = board.board[row + y_delta][col + x_delta].type
            if (targetType < EMPTY and tile.type > EMPTY) or (
                    targetType > EMPTY and tile.type < EMPTY):
                if not noDukeAttack or (noDukeAttack and targetType != BLACKDUKE and targetType != WHITEDUKE):
                    legal_moves.append((row + y_delta, col + x_delta))
                    moveTypes.append(moveType)

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
                    legal_moves.append((y_pos, x_pos))
                    moveTypes.append(moveType)
                    x_index += x_delta
                    y_index += y_delta
                elif (targetType < EMPTY and tile.type > EMPTY) or (targetType > EMPTY and tile.type < EMPTY):
                    if not noDukeAttack or (noDukeAttack and targetType != BLACKDUKE and targetType != WHITEDUKE):
                        legal_moves.append((y_pos, x_pos))
                        moveTypes.append(moveType)
                        stop = True
                        continue
                else:
                    stop = True

        if moveType == JUMPSLIDE:
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
                    legal_moves.append((y_pos, x_pos))
                    moveTypes.append(moveType)
                    x_index += x_delta
                    y_index += y_delta
                elif (targetType < EMPTY and tile.type > EMPTY) or (targetType > EMPTY and tile.type < EMPTY):
                    if not noDukeAttack or (noDukeAttack and targetType != BLACKDUKE and targetType != WHITEDUKE):
                        legal_moves.append((y_pos, x_pos))
                        moveTypes.append(moveType)
                        x_index += x_delta
                        y_index += y_delta
                else:
                    x_index += x_delta
                    y_index += y_delta
    return legal_moves, moveTypes


def check_in_check(board, checkingWhite):
    target = EMPTY
    if checkingWhite == 1:
        target = WHITEDUKE
    else:
        target = BLACKDUKE
    enemyMoves = []
    dukePos = None
    for row in range(NUM_COLS):
        for col in range(NUM_COLS):
            if board.board[row][col].type == target:
                dukePos = (row, col)
    for row in range(NUM_COLS):
        for col in range(NUM_COLS):
            if board.board[row][col].type != EMPTY and board.board[row][col].type // abs(board.board[row][col].type) == checkingWhite * -1:
                moves, moveTypes = gen_legal_moves(board, row, col, False)
                enemyMoves.append(moves)
    for bigMove in enemyMoves:
        for moves in bigMove:
            if moves == dukePos:
                return True
    return False

# If 1, check if white has won
def check_game_won(board, checkingWhite):
    return len(gen_duke_moves(board, checkingWhite * -1)) == 0 and check_in_check(checkingWhite * -1)

def gen_duke_moves(board, checkingWhite):
    target = EMPTY
    if checkingWhite == 1:
        target = WHITEDUKE
    else:
        target = BLACKDUKE
    dukeMoves = []
    enemyMoves = []
    ignore = []
    dukePos = None
    for row in range(NUM_COLS):
        for col in range(NUM_COLS):
            if board.board[row][col].type == target:
                dukePos = (row, col)
                dukeMoves, ignore = gen_legal_moves(board, row, col, True)
    for row in range(NUM_COLS):
        for col in range(NUM_COLS):
            if board.board[row][col].type != EMPTY and board.board[row][col].type // abs(board.board[row][col].type) == checkingWhite * -1:
                moves, moveTypes = gen_legal_moves(board, row, col, False)
                enemyMoves.append(moves)
    for bigMove in enemyMoves:
        for moves in bigMove:
            for dukeMove in dukeMoves:
                if dukeMove == moves:
                    dukeMoves.remove(dukeMove)
    return dukeMoves, ignore


class Board:
    def __init__(self, size):
        self.board = [[EMPTYTILE, BLACKFOOTMANTILE, BLACKDUKETILE, BLACKFOOTMANTILE, EMPTYTILE, EMPTYTILE],
                      [EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE],
                      [EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE],
                      [EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE],
                      [EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE],
                      [EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE, EMPTYTILE]]
        self.whiteToPlay = 1
        self.bags = Bags()
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
def moveUnit(board, move, moveType, row, col):
    newState = copy.deepcopy(board)
    toMove = newState.board[row][col]
    if newState.board[move[0]][move[1]].type == BLACKDUKE or newState.board[move[0]][move[1]].type == WHITEDUKE:
        print("THIS is literally illegal")
    if moveType != STRIKE:
        newState.board[move[0]][move[1]] = toMove
        newState.board[row][col] = EMPTYTILE
    elif moveType == STRIKE:
        newState.board[move[0]][move[1]] = EMPTYTILE
    toMove.isUp = not toMove.isUp
    newState.whiteToPlay = -1 * newState.whiteToPlay
    return newState

# Place the given tile at the given placement on the given board and return a new copy of the board
def placeUnit(board, placement, Tile):
    newState = copy.deepcopy(board)
    newState.board[placement[0]][placement[1]] = Tile
    newState.whiteToPlay = -1 * newState.whiteToPlay
    return newState

def placeStartingUnit(board, placement, Tile):
    newState = copy.deepcopy(board)
    newState.board[placement[0]][placement[1]] = Tile
    return newState

# Will give a list of valid new unit placements based on whos turn it is and where the duke is
def gen_legal_placements(board):
    target = (0, 0)
    for row in range(NUM_COLS):
        for col in range(NUM_COLS):
            if board.whiteToPlay == 1:
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


class Bags:
    # Start by filling each bag with the correct number of units
    def __init__(self):
        self.playerBag = [WHITEFOOTMANTILE, WHITEASSASSINTILE, WHITEBOWMANTILE, WHITECHAMPIONTILE, WHITEDRAGOONTILE]
        self.aiBag = [BLACKFOOTMANTILE, BLACKASSASSINTILE, BLACKBOWMANTILE, BLACKCHAMPIONTILE, BLACKDRAGOONTILE]

    # Pull a unit from the bag based on which player turn it is (bool)
    # Returns an empty tile if bag is empty
    def pull(self, isPlayersTurn):
        if isPlayersTurn == 1:
            if len(self.playerBag) == 0:
                #print("Bag is empty! Move a unit instead!")
                return EMPTYTILE
            toRemove = self.playerBag[random.randrange(len(self.playerBag))]
            # print("You drew a " + printable[toRemove.type])
            self.playerBag.remove(toRemove)
            return toRemove
        else:
            if len(self.aiBag) == 0:
                return EMPTYTILE
            toRemove = self.aiBag[random.randrange(len(self.aiBag))]
            self.aiBag.remove(toRemove)
            return toRemove

# Tree structure from https://github.com/int8/monte-carlo-tree-search
class Node:
    def __init__(self, boardState, parent=None):
        self.state = boardState
        self.parent = parent
        self.children = []
        self.number_of_visits = 0
        self.results = defaultdict(int)
        self.untried_states = gen_legal_actions(self.state)


    def q(self):
        wins = self.results[self.parent.state.whiteToPlay]
        loses = self.results[-1 * self.parent.state.whiteToPlay]
        return wins - loses

    def n(self):
        return self.number_of_visits

    def expand(self):
        nextMove = self.untried_states.pop()
        child = Node(nextMove, parent=self)
        self.children.append(child)
        return child

    def is_terminal_node(self):
        return checkResults(self.state) != 0

    def rollout(self):
        current_state = self.state
        while checkResults(current_state) == 0:
            valid_states = gen_legal_actions(current_state)
            # for state in valid_states:
                # state.print_board()
            if len(valid_states) != 0:
                current_state = valid_states[np.random.randint(len(valid_states))]
                current_state.print_board()
            else:
                print("No result")
                break
        current_state.print_board()
        print(len(gen_duke_moves(current_state, current_state.whiteToPlay)))
        return checkResults(current_state)

    def best_child(self, c_param=1.4):
        weights = [
            (c.q() / c.n()) + 1.4 * np.sqrt((2 * np.log(self.n()) / c.n()))
            for c in self.children
        ]
        return self.children[np.argmax(weights)]

    def is_fully_expanded(self):
        return len(self.untried_states) == 0

    def backpropogate(self, result):
        self.number_of_visits += 1
        self.results[result] += 1
        if self.parent:
            self.parent.backpropogate(result)

class SearchTree:
    def __init__(self, node):
        self.root = node

    def choose_action(self, depth):
        for x in range(depth):
            n = self.tree_policy()
            reward = n.rollout()
            n.backpropogate(reward)
        return self.root.best_child(c_param=0.0)

    def tree_policy(self):
        current_node = self.root
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node

def checkResults(state):
    if check_game_won(state, 1):
        return 1
    elif check_game_won(state, -1):
        return -1
    else:
        return 0

def gen_legal_actions(state):
    valid_states = []
    inCheck = check_in_check(state, state.whiteToPlay)
    for row in range(NUM_COLS):
        for col in range(NUM_COLS):
            if state.whiteToPlay == 1:
                if state.board[row][col].type > 0:
                    if state.board[row][col].type == WHITEDUKE:
                        allMoves, allTypes = gen_duke_moves(state, state.whiteToPlay)
                        for index in range(len(allMoves)):
                            valid_states.append(moveUnit(state, allMoves[index], allTypes[index], row, col))
                    if not inCheck and not state.board[row][col].type != WHITEDUKE:
                        allMoves, allTypes = gen_legal_moves(state, row, col, True)
                        for index in range(len(allMoves)):
                            valid_states.append(moveUnit(state, allMoves[index], allTypes[index], row, col))
            else:
                if state.board[row][col].type < 0:
                    if state.board[row][col].type == BLACKDUKE:
                        allMoves, allTypes = gen_duke_moves(state, state.whiteToPlay)
                        for index in range(len(allMoves)):
                            valid_states.append(moveUnit(state, allMoves[index], allTypes[index], row, col))
                    if not inCheck and state.board[row][col].type != BLACKDUKE:
                        allMoves, allTypes = gen_legal_moves(state, row, col, True)
                        for index in range(len(allMoves)):
                            valid_states.append(moveUnit(state, allMoves[index], allTypes[index], row, col))
        if not inCheck and len(gen_legal_placements(state)) > 0:
            newUnit = state.bags.pull(state.whiteToPlay)
            if newUnit != EMPTYTILE:
                placementOptions = gen_legal_placements(state)
                for option in placementOptions:
                    valid_states.append(placeUnit(state, option, newUnit))
    return valid_states

def play():
    # Generate board and bags
    GAMEBOARD = Board(NUM_COLS)
    # Have player enter starting info
    startingCol = int(input("Enter the column of your Duke (0 - 5): "))
    GAMEBOARD = placeStartingUnit(GAMEBOARD, (5, startingCol), WHITEDUKETILE)
    GAMEBOARD.print_board()
    footman1Options = gen_legal_placements(GAMEBOARD)
    showPotentialMoves(GAMEBOARD, footman1Options)
    moveIndex = int(
        input("Select where you would like to place your first footman (0 - " + str(len(footman1Options) - 1) + "): "))
    GAMEBOARD = placeStartingUnit(GAMEBOARD, footman1Options[moveIndex], WHITEFOOTMANTILE)
    GAMEBOARD.print_board()
    footman2Options = gen_legal_placements(GAMEBOARD)
    showPotentialMoves(GAMEBOARD, footman2Options)
    moveIndex = int(
        input("Select where you would like to place your second footman (0 - " + str(len(footman1Options) - 1) + "): "))
    GAMEBOARD = placeStartingUnit(GAMEBOARD, footman2Options[moveIndex], WHITEFOOTMANTILE)
    GAMEBOARD.whiteToPlay = 1
    # Main game loop
    gameOver = False
    while not gameOver:
        GAMEBOARD.print_board()
        # Player chooses action
        action = int(input("Choose One:\n Move: 0\n Pull from bag: 1\n"))
        if action == 0:
            col = int(input("Enter the column of the piece to move: "))
            row = NUM_COLS - 1 - int(input("Enter the row of the piece to move: "))
            moveOptions, moveTypes = gen_legal_moves(GAMEBOARD, row, col, True)
            if len(moveOptions) == 0:
                print("No moves available for the selected unit, please try again")
                continue
            showPotentialMoves(GAMEBOARD, moveOptions)
            moveIndex = int(
                input("Select where you would like to move this unit to(0 - " + str(len(moveOptions) - 1) + "): "))
            GAMEBOARD = moveUnit(GAMEBOARD, moveOptions[moveIndex], moveTypes[moveIndex], row, col)
        if action == 1:
            newUnit = GAMEBOARD.bags.pull(True)
            if newUnit == EMPTYTILE:
                continue
            placementOptions = gen_legal_placements(GAMEBOARD)
            showPotentialMoves(GAMEBOARD, placementOptions)
            moveIndex = int(input("Select where you would like to place the new unit (0 - " + str(
                len(placementOptions) - 1) + "): "))
            GAMEBOARD = placeUnit(GAMEBOARD, placementOptions[moveIndex], newUnit)
            GAMEBOARD.print_board()
        result = checkResults(GAMEBOARD)
        if result > 0:
            print("White wins!")
            gameOver = True
        elif result < 0:
            print("Black wins")
            gameOver = True
        else:
            print("Game continues, no winner yet\n")
        print("AI playing now")
        root = Node(GAMEBOARD)
        tree = SearchTree(root)
        best_node = tree.choose_action(5)
        GAMEBOARD = best_node.state
    print("Game ended")


play()
#GAMEBOARD = Board(NUM_COLS)
# GAMEBOARD.print_board()
# root = Node(GAMEBOARD)
# tree = SearchTree(root)
# best_node = tree.choose_action(5)
# print(len(gen_legal_actions(best_node.state)))
# best_node.state.print_board()
# placements = gen_legal_placements(GAMEBOARD)
# showPotentialMoves(GAMEBOARD, placements)
# GAMEBOARD = placeUnit(GAMEBOARD, placements[0], WHITEFOOTMANTILE)
# GAMEBOARD.print_board()
# moves = gen_legal_moves(GAMEBOARD, GAMEBOARD.board[2][2], 2, 2)
# showPotentialMoves(GAMEBOARD, moves)
# GAMEBOARD = moveUnit(GAMEBOARD, moves[2], 2, 2)
# GAMEBOARD.print_board()
# moves = gen_legal_moves(GAMEBOARD, GAMEBOARD.board[2][3], 2, 3)
# showPotentialMoves(GAMEBOARD, moves)
