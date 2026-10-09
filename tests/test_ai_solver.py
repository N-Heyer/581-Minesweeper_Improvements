"""
Prologue Comment
File: test_ai_solver.py
Description: 
Inputs:  
Outputs: Pytest results of each test case
External sources: Original code with assistance by OpenAI 
                  ChatGPT for correctness. Logic is reviewed
                  and tested by the author.
Author: Khang Phan
Created: [Oct 8 2026]
"""

from minesweeper import Minesweeper
from difficulty_presets import BEGINNER
from ai_solver_easy import easy_mode
from ai_interactive_mode import getAiMoveInteractive
from ai_auto_solve_mode import getMovesForAutoSolve
from random import randint
import pytest

def test_easy_ai():
    # test that the easy AI returns a valid cell

    for _ in range(10):
        board = Minesweeper(BEGINNER, 1)
        board.createBoard(randint(0, board.rows-1), randint(0, board.columns-1))

        # place flags, flagged cells should not be included as possible cells for AI to select
        for row in range(board.rows):
            for col in range(board.columns):
                if board.remaining() > 0 and board._external[row][col] == 0:
                    board.flag(row, col)
            if board.remaining() == 0:
                break

        aiCell = easy_mode(board.getPlayerView(), board.rows, board.columns)
        assert aiCell is not None

        aiRow, aiCol = aiCell
        # check that the bounds of the returned cell are within board dimensions
        assert 0 <= aiRow < board.rows
        assert 0 <= aiCol < board.columns
        assert board._external[aiRow][aiCol] == 0  # not an already revealed or flagged cell

def test_no_possible_tiles():
    # test the easy AI when no moves are possible

    board = Minesweeper(BEGINNER, 1)

    # reveal every cell
    for i in range(board.rows):
        for j in range(board.columns):
            board._external[i][j] = 1
    assert easy_mode(board.getPlayerView(), board.rows, board.columns) is None

    # set some cells as flagged, should still leave no possible options for AI
    for i in range(board.columns):
        board._external[0][i] = 2
    assert easy_mode(board.getPlayerView(), board.rows, board.columns) is None

@pytest.mark.parametrize("aiSkill", [0, 2.5, 4])
def test_invalid_ai_skill(aiSkill):
    board = Minesweeper(BEGINNER, 1)

    with pytest.raises(ValueError):
        getAiMoveInteractive(board.getPlayerView(), aiSkill, BEGINNER)

def test_get_moves_for_auto_solve():
    # test AI auto solve on a board with eligible moves

    board = Minesweeper(BEGINNER, 1)
    board.createBoard(randint(0, board.rows-1), randint(0, board.columns-1))

    aiMoves = getMovesForAutoSolve(board, 1, BEGINNER)
    assert board.state() in ("Victory", "Game Over: Loss")  # should result in either a win or loss
    assert aiMoves is not None

    jumper = aiMoves
    while jumper is not None:
        aiRow, aiCol = jumper.value
        assert 0 <= aiRow < board.rows
        assert 0 <= aiCol < board.columns
        jumper = jumper.next

    # all moves successfully made are checked to be in bounds
    # all moves preceding the final move should be safe
    while aiMoves.next is not None:
        aiRow, aiCol = aiMoves.value
        assert board._internal[aiRow][aiCol] != -1  # not mine
        assert board._external[aiRow][aiCol] == 1   # revealed
        aiMoves = aiMoves.next

    aiRow, aiCol = aiMoves.value    # last move
    # for a loss case, check that last move revealed a mine
    if board.state() == "Game Over: Loss":
        assert board._internal[aiRow][aiCol] == -1
        assert board._external[aiRow][aiCol] == 1
    # for a win case, last move should not be a mine, all mines should still be hidden
    elif board.state() == "Victory":
        assert board._internal[aiRow][aiCol] != -1
        assert board._external[aiRow][aiCol] == 1
        assert board.status()