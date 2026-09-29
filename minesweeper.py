# Prologue Comment
# File: minesweeper.py
# Description: Game model for a 10x10 Minesweeper board. Places mines after the
#              first click so that cell is always safe, counts each cell's
#              adjacent mines, and handles digging with flood fill, flagging,
#              chording, and win/loss detection. No display or input code.
# Inputs:  mine count (int, 10-20) at construction; row and column (0-9) for
#          every move.
# Outputs: status codes from dig/flag/chord, a sprite index from display(), a
#          bool from status(), a text state from state(), a count from
#          remaining(). Raises ValueError on a bad mine count, IndexError on a
#          coordinate off the board.
# External sources: Game logic inherited from the Project 1 team. Claude Code
# (Anthropic) was used as a tool under my direction - I set the scope of each
# change, chose the approach, and reviewed the result. Directed by me, it audited
# this file for bugs and implemented the fixes I specified: bounds and mine-count
# validation, the createBoard guards, the flag cap, remaining(), revealAllMines(),
# state(), and this prologue.
# Author: Zachary McCauley; improvements by Jaycob Campos
# Created: Sept 13 2026

# use from minesweeper import Minesweeper

import random

# the board is a fixed 10x10 grid; these name the bounds the methods validate
BOARD_SIZE = 10
MIN_MINES = 10
MAX_MINES = 20

class Minesweeper:
    # input:  mines - how many mines to place, an int from 10 to 20
    # output: none; raises ValueError if mines is not an int in that range
    # fields: m = mine count, flags = flags placed (never more than m),
    #         _digs = safe cells still to uncover, _internal = solution grid
    #         (-1 mine, 0-8 adjacent mines), _external = player view
    #         (0 covered, 1 uncovered, 2 flagged), lost = True once a mine
    #         has been uncovered
    def __init__(self, mines = 15):
        if not isinstance(mines, int) or isinstance(mines, bool):
            raise ValueError(f"mine count must be an int, got {type(mines).__name__}")
        if mines < MIN_MINES or mines > MAX_MINES:
            raise ValueError(f"mine count must be {MIN_MINES}-{MAX_MINES}, got {mines}")
        self.m = mines
        self.flags = 0
        self._digs = BOARD_SIZE * BOARD_SIZE - mines
        self.is_constructed = False
        self.lost = False
        self._internal = [[0 for c in range(BOARD_SIZE)] for r in range(BOARD_SIZE)]
        self._external = [[0 for c in range(BOARD_SIZE)] for r in range(BOARD_SIZE)]

    # input:  row, col - a coordinate pair to check
    # output: none; raises IndexError if either falls outside the board
    def _checkBounds(self, row, col):
        if not 0 <= row < BOARD_SIZE or not 0 <= col < BOARD_SIZE:
            raise IndexError(f"({row}, {col}) is outside the {BOARD_SIZE}x{BOARD_SIZE} board")

    # Places the mines and digs the starting space. Does nothing if the board has
    # already been built, and clears a flag on the starting space first so that
    # space is always safely uncovered.
    # input:  s_row, s_col - the space the player clicked first, never a mine
    # output: none; raises IndexError if the coordinates are off the board
    def createBoard(self, s_row, s_col):
        self._checkBounds(s_row, s_col)
        if self.is_constructed:
            return
        if self._external[s_row][s_col] == 2:
            self._external[s_row][s_col] = 0
            self.flags -= 1
        c = 0
        while c < self.m:
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)
            if self._internal[row][col] < 0 or (row == s_row and col == s_col):
                pass
            else:
                self._internal[row][col] = -1
                for i in range(max(0, row - 1), min(BOARD_SIZE, row + 2)):
                    for j in range(max(0, col - 1), min(BOARD_SIZE, col + 2)):
                        if self._internal[i][j] != -1:
                            self._internal[i][j] += 1
                c += 1
        self.is_constructed = True
        self.dig(s_row, s_col)

    # Uncovers a cell, flood filling outward when it has no adjacent mines.
    # input:  row, col - the cell to dig
    # output: 2 if nothing changed (already uncovered or flagged), 1 if the cell
    #         was uncovered, 0 if it held a mine and the player lost;
    #         raises IndexError if the coordinates are off the board
    def dig(self, row, col):
        self._checkBounds(row, col)
        if self._external[row][col] != 0:
            return 2
        else:
            self._external[row][col] = 1
            if self._internal[row][col] == -1:
                self.lost = True
                return 0
            else:
                if self._internal[row][col] == 0:
                    for i in range(max(0, row - 1), min(BOARD_SIZE, row + 2)):
                        for j in range(max(0, col - 1), min(BOARD_SIZE, col + 2)):
                            self.dig(i, j)
                self._digs -= 1
                return 1

    # Places or removes a flag. Flagging before createBoard() is allowed.
    # input:  row, col - the cell to flag or unflag
    # output: 2 if nothing happened (cell already uncovered, or every flag is
    #         already placed), 1 if a flag was removed, 0 if one was placed;
    #         raises IndexError if the coordinates are off the board
    def flag(self, row, col):
        self._checkBounds(row, col)
        if self._external[row][col] == 1:
            return 2
        elif self._external[row][col] == 2:
            self._external[row][col] = 0
            self.flags -= 1
            return 1
        else:
            if self.flags >= self.m:
                return 2
            self._external[row][col] = 2
            self.flags += 1
            return 0

    # input:  none
    # output: how many flags the player still has to place, never negative
    def remaining(self):
        return max(0, self.m - self.flags)

    # Digs every covered neighbor of an uncovered number, but only when that
    # number equals the count of flags around it.
    # input:  row, col - the uncovered number to chord from
    # output: 2 if nothing happened, 1 if progress was made, 0 if the player hit
    #         a mine; raises IndexError if the coordinates are off the board
    def chord(self, row, col):
        self._checkBounds(row, col)
        displayVal = self.display(row, col)
        if displayVal <= 0:
            return 2
        flagCount = 0
        for r in range(max(0, row - 1), min(BOARD_SIZE, row + 2)):
            for c in range(max(0, col - 1), min(BOARD_SIZE, col + 2)):
                if self.display(r, c) == 0:
                    flagCount += 1
        if flagCount != displayVal:
            return 2
        toReturn = 1
        for r in range(max(0, row - 1), min(BOARD_SIZE, row + 2)):
            for c in range(max(0, col - 1), min(BOARD_SIZE, col + 2)):
                if self.display(r, c) == -3:
                    toReturn = 1 if self.dig(r, c) > 0 and toReturn == 1 else 0
        return toReturn

    # input:  row, col - the cell to draw
    # output: which sprite that cell should use - -3 covered, -2 zero, -1 mine,
    #         0 flag, 1-8 the adjacent mine count;
    #         raises IndexError if the coordinates are off the board
    def display(self, row, col):
        self._checkBounds(row, col)
        cell = self._external[row][col]
        if cell == 2:
            return 0
        elif cell == 1:
            if self._internal[row][col] == -1:
                return -1
            elif self._internal[row][col] == 0: 
                return -2
            else:
                return self._internal[row][col]
        else:
            return -3

    # Should be called after every dig.
    # input:  none
    # output: True once every safe cell is uncovered, False otherwise. False does
    #         not mean the player lost - use state() for that.
    def status(self):
        if self._digs == 0:
            return True
        else:
            return False

    # The status indicator. Kept separate from status(), whose bool return the
    # callers compare against True.
    # input:  none
    # output: "Game Over: Loss" once a mine has been uncovered, "Victory" once
    #         every safe cell is uncovered, otherwise "Playing"
    def state(self):
        if self.lost:
            return "Game Over: Loss"
        elif self._digs == 0:
            return "Victory"
        else:
            return "Playing"

    # Uncovers every mine, for the caller to draw after a loss. Leaves _digs
    # alone, so status() cannot report a win as a side effect.
    # input:  none
    # output: none; every mine cell becomes uncovered in the player's view
    def revealAllMines(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self._internal[row][col] == -1:
                    self._external[row][col] = 1
