# Prologue Comment
# File: ai_solver_hard.py
# Description: Hard-difficulty AI. Applies Medium's neighbor-count rules,
#              then checks horizontal and vertical 1-2-1 patterns on either
#              side of the revealed numbers. Validates the surrounding
#              covered cells before deducing a mine. Falls back to a random
#              covered, unflagged cell when no deduction applies.
# Inputs: playerView (grid of display() values), rows, columns.
# Outputs: ("dig", row, column), ("flag", row, column), or None if no
#          legal move remains. Returns one action per call.
# External sources: None
# Author: Lydia Peng
# Created: October 5, 2026
from ai_solver_medium import find_basic_move
from ai_solver_easy import easy_mode

#Collect covered neighbors and count adjacent flags.
def hidden_neighbors(playerView, rows, columns, row, column):
    hidden = set()
    flags = 0

    for r in range(max(0, row - 1), min(rows, row + 2)):
        for c in range(max(0, column - 1), min(columns, column + 2)):
            if (r, c) == (row, column):
                continue

            if playerView[r][c] == -3:
                hidden.add((r, c))
            elif playerView[r][c] == 0:
                flags += 1

    return hidden, flags

#Find a valid 1-2-1 pattern and return one flag action."""
def find_121_move(playerView, rows, columns):
    for row in range(rows):
        for column in range(columns):
            # Search across a row or down a column.
            for dr, dc in ((0, 1), (1, 0)):
                numbers = [
                    (row + i * dr, column + i * dc)
                    for i in range(3)
                ]

                if not all(
                    0 <= r < rows and 0 <= c < columns
                    for r, c in numbers
                ):
                    continue

                if [playerView[r][c] for r, c in numbers] != [1, 2, 1]:
                    continue

                # Examine both sides of the revealed numbers.
                for side in (-1, 1):
                    targets = [
                        (r + side * dc, c + side * dr)
                        for r, c in numbers
                    ]

                    if not all(
                        0 <= r < rows and 0 <= c < columns
                        for r, c in targets
                    ):
                        continue

                    if not all(
                        playerView[r][c] == -3 for r, c in targets
                    ):
                        continue

                    a, b, c = targets
                    expected_hidden = [
                        {a, b},
                        {a, b, c},
                        {b, c}
                    ]

                    valid = True

                    for position, expected in zip(numbers, expected_hidden):
                        hidden, flags = hidden_neighbors(
                            playerView, rows, columns, *position
                        )

                        # Extra hidden neighbors or flags invalidate this
                        # simple version of the 1-2-1 deduction.
                        if hidden != expected or flags != 0:
                            valid = False
                            break

                    if valid:
                        return ("flag", a[0], a[1])

    return None

#Use basic rules, then 1-2-1, then a random dig
def hard_mode(playerView, rows, columns):
    move = find_basic_move(playerView, rows, columns)

    if move is not None:
        return move

    move = find_121_move(playerView, rows, columns)

    if move is not None:
        return move

    random_move = easy_mode(playerView, rows, columns)

    if random_move is None:
        return None

    row, column = random_move
    return ("dig", row, column)