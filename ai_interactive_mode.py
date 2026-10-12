# Prologue Comment
# File: ai_interactive_mode.py
# Description: Routes to the right AI for the turn-based mode, where the player
#              and the AI take turns, and hands back one move per call.
# Inputs:  playerView (grid of display() values), aiSkill (1-3), the difficulty
#          object the game was built with.
# Outputs: an Easy coordinate, a Medium/Hard action tuple, or None. Raises ValueError
#          on an AI level outside 1-3.
# External sources: Claude (Anthropic) was used for bug finding, and under my
# direction changed this file to take a view carrying the adjacent mine counts
# instead of _external, which levels 2 and 3 cannot deduce from.
# Author: Jaycob Campos
# Created: Sept 29 2026

from ai_solver_easy import easy_mode
from ai_solver_medium import medium_mode
from ai_solver_hard import hard_mode

# Picks the AI's next single move, for the mode where the player and the AI take
# turns. Easy returns a coordinate; Medium and Hard return an action and coordinate.
# input:  playerView - the grid of display() values from getPlayerView();
#         aiSkill - which AI to use, 1-3; gameDifficultyObject - a preset
#         exposing rows and columns
# output: (row, column) for Easy, (action, row, column) for Medium/Hard,
#         or None when no move is left; raises ValueError for an invalid skill
def getAiMoveInteractive(playerView, aiSkill, gameDifficultyObject):
    match aiSkill:
        case 1:
            return easy_mode(playerView, gameDifficultyObject.rows, gameDifficultyObject.columns)
        case 2:
            return medium_mode(
                playerView,
                gameDifficultyObject.rows,
                gameDifficultyObject.columns
            )
        case 3:
            return hard_mode(
                playerView,
                gameDifficultyObject.rows,
                gameDifficultyObject.columns
            )
        case _:
            raise ValueError(f"unknown AI: {aiSkill}")


# Added Oct 7, 2026 by Andrew Kruckemyer with OpenAI Codex assistance.
def applyAiMove(board, move):
    """Apply Easy coordinates or Medium/Hard actions; return the board status code."""
    if len(move) == 2:
        action = "dig"
        row, column = move
    else:
        action, row, column = move
    if action == "dig":
        # dig() constructs the first-click opening when needed.
        return board.dig(row, column)
    if action == "flag":
        return board.flag(row, column)
    raise ValueError(f"Unknown AI action: {action}")
