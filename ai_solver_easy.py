# Prologue Comment
# File: ai_solver.py
# Description: Easy-difficulty AI. Picks a random covered, unflagged cell as
#              the next move; the caller performs the dig.
# Inputs:  external (player-visible 2D grid), rows, columns.
# Outputs: (row, column) tuple, or None if no legal move remains.
# External sources: Claude (Anthropic) was used for bug finding.
# Author: Jaycob Campos
# Created: Sept 29 2026

from random import randint


def easy_mode(external, rows, columns):
    possibleTiles = []

    for row in range(rows):
        for column in range(columns):
            if external[row][column] == 0:
                possibleTiles.append((row, column))

    if len(possibleTiles) == 0:
        return None

    return possibleTiles[randint(0, len(possibleTiles) - 1)]
