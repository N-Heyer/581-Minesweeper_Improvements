"""
Prologue Comment
File: test_ai_solver.py
Description: Includes helper functions to reduce redundancy
             in test files
Inputs: (board, row, col), (difficulty, ai level, mine list)
Outputs: a list of neighbors, a custom board
External sources: None
Author: Khang Phan
Created: [Oct 10 2026]
"""

from minesweeper import Minesweeper

def neighbors(board, row, col):
    # Identifies the surrounding neighbors of the passed in cell
    
    neighbors = []

    # identify all cells in 3x3 area, bounded by board dimensions
    for i in range(max(0, row-1), min(board.rows, row+2)):
        for j in range(max(0, col-1), min(board.columns, col+2)):

            # exclude center cell
            if i != row or j != col:
                neighbors.append((i, j))
    return neighbors

def make_custom_board(difficulty, aiLevel, mineList):
    # Sets a custom board to test specific functions

    board = Minesweeper(difficulty, aiLevel)
    
    for row, col in mineList:
        # set custom mine positions
        board._internal[row][col] = -1

        # increment neighboring cells' adjacency counts
        for i in range(max(0, row-1), min(board.rows, row+2)):
            for j in range(max(0, col-1), min(board.columns, col+2)):
                if board._internal[i][j] != -1:
                    board._internal[i][j] += 1

    board.mines = len(mineList)
    board._digs = board.rows * board.columns - board.mines
    board.is_constructed = True

    return board