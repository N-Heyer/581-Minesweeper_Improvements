# File: ai_solver_medium.py
# Description: Medium AI using neighbor counts to flag mines or dig safe
#              cells. Falls back to a random covered, unflagged cell.
# Inputs: playerView, rows, columns.
# Outputs: ("dig", row, column), ("flag", row, column), or None.
# External sources: None
# Author: Lydia Peng
# Created: October 4, 2026

from ai_solver_easy import easy_mode

#Return one move deduced from neighbor counts, or None.
def find_basic_move(playerView, rows, columns):
    for row in range(rows):
        for column in range(columns):
            value = playerView[row][column]

            # Revealed zeros use -2; revealed numbers use 1 through 8.
            if value == -2:
                number = 0
            elif 1 <= value <= 8:
                number = value
            else:
                continue

            hidden_neighbors = []
            flagged_neighbors = 0

            for neighbor_row in range(max(0, row - 1), min(rows, row + 2)):
                for neighbor_column in range(
                    max(0, column - 1), min(columns, column + 2)
                ):
                    if neighbor_row == row and neighbor_column == column:
                        continue

                    neighbor = playerView[neighbor_row][neighbor_column]

                    if neighbor == -3:
                        hidden_neighbors.append((neighbor_row, neighbor_column))
                    elif neighbor == 0:
                        flagged_neighbors += 1

            if not hidden_neighbors:
                continue

            remaining_mines = number - flagged_neighbors

            # Every remaining hidden neighbor must be a mine.
            if remaining_mines == len(hidden_neighbors):
                target_row, target_column = hidden_neighbors[0]
                return ("flag", target_row, target_column)

            # All adjacent mines are flagged; other hidden neighbors are safe.
            if remaining_mines == 0:
                target_row, target_column = hidden_neighbors[0]
                return ("dig", target_row, target_column)

    return None


def medium_mode(playerView, rows, columns):
    move = find_basic_move(playerView, rows, columns)

    if move is not None:
        return move

    random_move = easy_mode(playerView, rows, columns)

    if random_move is None:
        return None

    action, row, column = random_move
    return (action, row, column)