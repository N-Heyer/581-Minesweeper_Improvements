# Prologue Comment
# File: ai_interactive_mode.py
# Description: Routes to the right AI for the turn-based mode, where the player
#              and the AI take turns, and hands back one move per call.
# Inputs:  playerView (grid of display() values), aiSkill (1-3), the difficulty
#          object the game was built with.
# Outputs: a (row, column) move, or None when the AI has none. Raises ValueError
#          on an AI level outside 1-3.
# External sources: Claude (Anthropic) was used for bug finding, and under my
# direction changed this file to take a view carrying the adjacent mine counts
# instead of _external, which levels 2 and 3 cannot deduce from.
# Author: Jaycob Campos
# Created: Sept 29 2026

from ai_solver_easy import easy_mode

# Picks the AI's next single move, for the mode where the player and the AI take
# turns. Levels 2 and 3 are not written yet.
# input:  playerView - the grid of display() values from getPlayerView();
#         aiSkill - which AI to use, 1-3; gameDifficultyObject - a preset
#         exposing rows and columns
# output: a (row, column) move, None when no move is left (or for the levels not
#         written yet); raises ValueError if aiSkill is not 1, 2, or 3
def getAiMoveInteractive(playerView, aiSkill, gameDifficultyObject):
    match aiSkill:
        case 1:
            return easy_mode(playerView, gameDifficultyObject.rows, gameDifficultyObject.columns)
        case 2:
            return
        case 3:
            return
        case _:
            raise ValueError(f"unknown AI: {aiSkill}")

