"""
Prologue Comment
File: difficulty_presets.py
Description: Defines the difficulty presets for the Minesweeper board.
             Each preset stores the grid size (rows and columns) and the
             number of mines. Provides BEGINNER, INTERMEDIATE, and EXPERT
             configurations used by the Board class.
Inputs:  rows, columns, and mineCount when a Difficulty is created.
Outputs: Difficulty objects (BEGINNER, INTERMEDIATE, EXPERT), each
         exposing rows, columns, and mines - the three fields the
         Minesweeper constructor reads.
External sources: None — original code.
Author: Jaycob Campos
Created: [sept 29 2026]
"""


# holds the configuration for one difficulty level
class Difficulty:
    # input:  rows, columns - the board dimensions; mineCount - how many mines
    # output: none
    # fields: rows, columns, mines - read directly by Minesweeper.__init__
    def __init__(self, rows, columns, mineCount):
        self.rows = rows
        self.columns = columns
        self.mines = mineCount

# preset difficulty levels used throughout the game.
BEGINNER = Difficulty(10, 10, 10)
INTERMEDIATE = Difficulty(16, 16, 40)
EXPERT = Difficulty(16, 30, 99)
