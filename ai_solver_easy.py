# Prologue Comment
# File: ai_solver.py
# Description: Easy-difficulty AI. Picks a random covered, unflagged cell as
#              the next move; the caller performs the dig.
# Inputs:  playerView (grid of display() values), rows, columns.
# Outputs: (row, column) tuple, or None if no legal move remains.
# External sources: Claude (Anthropic) was used for bug finding.
# Author: Jaycob Campos
# Created: Sept 29 2026

from random import randint


# Collects every covered, unflagged tile and returns one of them at random, so
# the easy AI plays off the player's view and never reads the solution.
# input:  playerView - the grid of display() values from getPlayerView();
#         rows, columns - the board dimensions
# output: a (row, column) tuple, or None when no covered tile is left
def easy_mode(playerView, rows, columns):
    possibleTiles = []

    for row in range(rows):
        for column in range(columns):
            # TODO: read code and understand it
            if playerView[row][column] == -3:
                possibleTiles.append((row, column))

    if len(possibleTiles) == 0:
        return None

    return possibleTiles[randint(0, len(possibleTiles) - 1)]
