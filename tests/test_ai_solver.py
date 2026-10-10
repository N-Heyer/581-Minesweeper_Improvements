"""
Prologue Comment
File: test_ai_solver.py
Description: Tests the AI solver at easy,
             medium, and hard levels along with
             interactive and auto solve modes
Inputs: row, column, list of cells (mines, flags, safe, etc.), 
        difficulty, ai level
Outputs: Pytest results of each test case
External sources: Original code with assistance by OpenAI 
                  ChatGPT for correctness. Logic is reviewed
                  and tested by the author.
Author: Khang Phan
Created: [Oct 8 2026]
"""
import pytest

from minesweeper import Minesweeper
from difficulty_presets import BEGINNER
from test_helpers import neighbors, make_custom_board
from ai_solver_easy import easy_mode
from ai_solver_medium import find_basic_move, medium_mode
from ai_solver_hard import find_121_move, hard_mode
from ai_interactive_mode import getAiMoveInteractive
from ai_auto_solve_mode import getMovesForAutoSolve


def test_easy_ai():
    # test that the easy AI returns a valid cell

    for _ in range(10):
        board = Minesweeper(BEGINNER, 1)
        board.createBoard(0, 0)

        # place flags, flagged cells should not be included as possible cells for AI to select
        for row in range(board.rows):
            for col in range(board.columns):
                if board.remaining() > 0 and board._external[row][col] == 0:
                    board.flag(row, col)
            if board.remaining() == 0:
                break

        move = easy_mode(board.getPlayerView(), board.rows, board.columns)
        assert move is not None

        action, row, col = move
        # check that the bounds of the returned cell are within board dimensions
        assert action == "dig"
        assert 0 <= row < board.rows
        assert 0 <= col < board.columns
        assert board._external[row][col] == 0  # not an already revealed or flagged cell

@pytest.mark.parametrize("row, col, mineList", [
    (1, 1, [(2,0), (1,2)])
])
def test_medium_flag(row, col, mineList):
    # test medium AI's basic move for flagging a cell
    # where (# of hidden neighbors == adjacency count)

    # set custom board
    board = make_custom_board(BEGINNER, 2, mineList)
    board.dig(row, col)

    # not enough information to dig or flag
    assert find_basic_move(board.getPlayerView(), board.rows, board.columns) is None

    # reveal all neighbors that are not a mine
    for r, c in neighbors(board, row, col):
        if board._internal[r][c] != -1:
            board._external[r][c] = 1   # reveal if not a mine
    move = find_basic_move(board.getPlayerView(), board.rows, board.columns)
    action, moveRow, moveCol = move

    assert action == "flag"
    assert (moveRow, moveCol) in mineList

@pytest.mark.parametrize("row, col, mineList, safeCells", [
    (1, 1, [(0,0), (0,2), (3,1)],
        [(1,0), (2,0), (0,1), (2,1), (1,2), (2,2)])
])
def test_medium_dig(row, col, mineList, safeCells):
    # test medium AI's basic move for digging
    # where (adjacency count - flag count = 0)

    # set custom board
    board = make_custom_board(BEGINNER, 2, mineList)
    board.dig(row, col)

    # not enough information
    assert find_basic_move(board.getPlayerView(), board.rows, board.columns) is None

    # flag all neighboring mines
    for r, c in mineList:
        board.flag(r, c)

    move = find_basic_move(board.getPlayerView(), board.rows, board.columns)
    action, moveRow, moveCol = move

    assert action == "dig"
    # only legal moves (not random) are in safeCells
    assert (moveRow, moveCol) in safeCells

def test_medium_hard_ai_fallback():
    # test the medium AI defaulting to choosing a random cell
    # when not enough information to find basic move

    board = Minesweeper(BEGINNER, 3)
    
    # empty board with 0 information
    # not enough info to find a basic move
    # default to random move
    medMove = find_basic_move(board.getPlayerView(), board.rows, board.columns)
    hardMove = find_121_move(board.getPlayerView(), board.rows, board.columns)
    assert medMove is None
    assert hardMove is None

    for move in (medium_mode(board.getPlayerView(), board.rows, board.columns),
                 hard_mode(board.getPlayerView(), board.rows, board.columns)):
        assert move is not None
        action, randomRow, randomCol = move

        assert action == "dig"
        assert 0 <= randomRow < board.rows
        assert 0 <= randomCol < board.columns
        assert board._external[randomRow][randomCol] == 0

@pytest.mark.parametrize("mineList, revealList", [
    # first two mines are the ones relevant to the 1-2-1 pattern
    # first 3 revealed cells are the 1-2-1 pattern
    # ([(3,3),(3,5),   (0,4)],
    #     [(2,3),(2,4),(2,5),   (1,3), (1,4), (1,5)]),
    # ([(7,3),(9,3),   (6,0), (9,0)],
    #     [(7,2),(8,2),(9,2),   (7,1), (8,1), (9,1)]),

    ([(3,3),(3,5),   (0,4),(2,1),(2,7)],
        [(2,3),(2,4),(2,5),   (1,3),(1,4),(1,5),(1,2),(2,2),(3,2),(1,6),(2,6),(3,6)]),
    ([(7,3),(9,3),   (6,0),(9,0),(5,3)],
        [(7,2),(8,2),(9,2),   (7,1),(8,1),(9,1),(6,1),(6,2),(6,3)]),
    ([(8,7),(8,9),   (9,5)],
        [(9,7),(9,8),(9,9),   (8,6),(9,6)])
])
def test_find_121_move(mineList, revealList):
    # test that when the only move possible requires the 1-2-1 pattern,
    # find_121_move() flags the expected mine positions

    # set custom board with pre-revealed cells - force the 1-2-1 pattern rule
    board = make_custom_board(BEGINNER, 3, mineList)
    for r, c in revealList:
        board.dig(r, c)

    # check that test environment is set up properly
    pattern = [board.getPlayerView()[r][c] for r, c in revealList[:3]]
    assert pattern == [1, 2, 1]

    move = find_121_move(board.getPlayerView(), board.rows, board.columns)
    assert move is not None
    action, moveRow, moveCol = move

    assert action == "flag"
    assert (moveRow, moveCol) in mineList[:2]   # one of the mines directly next to the 1-2-1

@pytest.mark.parametrize("mineList, revealList, expected", [
    # first two mines are the ones relevant to the 1-2-1 pattern
    # first 3 revealed cells are the 1-2-1 pattern
    # first 2 expected cells are flagged mines, last is revealed
    ([(3,3),(3,5),   (0,4),(2,1),(2,7)],
        [(2,3),(2,4),(2,5),   (1,3),(1,4),(1,5),(1,2),(2,2),(3,2),(1,6),(2,6),(3,6)],
        [(3,3),(3,5),   (3,4)]),
    ([(7,3),(9,3),   (6,0),(9,0),(5,3)],
        [(7,2),(8,2),(9,2),   (7,1),(8,1),(9,1),(6,1),(6,2),(6,3)],
        [(7,3),(9,3),   (8,3)]),
    ([(8,7),(8,9),   (9,5)],
        [(9,7),(9,8),(9,9),   (8,6),(9,6)],
        [(8,7),(8,9),   (8,8)])
])
def test_121_sequence(mineList, revealList, expected):
    # test a sequence of moves when 1-2-1 pattern rule is forced
    # should flag the two mines and reveal the mine next to the 2

    # set custom board with pre-revealed cells - force the 1-2-1 pattern rule
    board = make_custom_board(BEGINNER, 3, mineList)
    for r, c in revealList:
        board.dig(r, c)

    view = board.getPlayerView()

    # check that test environment is set up properly
    pattern = [view[r][c] for r, c in revealList[:3]]
    assert pattern == [1, 2, 1]
    for r, c in expected:
        assert view[r][c] == -3 # initially hidden
    assert find_basic_move(view, board.rows, board.columns) is None # no basic move can be made

    # next 3 moves should be handling the 1-2-1 rule
    for _ in range(3):
        move = hard_mode(board.getPlayerView(), board.rows, board.columns)
        assert move is not None
        
        action, moveRow, moveCol = move
        assert action in {"flag", "dig"}
        assert 0 <= moveRow < board.rows
        assert 0 <= moveCol < board.columns
        assert board._external[moveRow][moveCol] == 0

        if action == "flag":
            assert board._internal[moveRow][moveCol] == -1
            board.flag(moveRow, moveCol)
        else:
            assert board._internal[moveRow][moveCol] != -1
            board.dig(moveRow, moveCol)

    for r, c in expected[:2]:
        assert board._external[r][c] == 2
    row, col = expected[2]
    assert board._external[row][col] == 1

@pytest.mark.parametrize("aiLevel", [1, 2, 3])
def test_no_possible_tiles(aiLevel):
    # test the easy AI when no moves are possible

    board = Minesweeper(BEGINNER, aiLevel)

    # reveal every cell
    for row in range(board.rows):
        for col in range(board.columns):
            board._external[row][col] = 1
    assert getAiMoveInteractive(board.getPlayerView(), aiLevel, board.gameDifficultyObject) is None

    # set some cells as flagged, should still leave no possible options for AI
    for i in range(board.columns):
        board._external[0][i] = 2
    assert getAiMoveInteractive(board.getPlayerView(), aiLevel, board.gameDifficultyObject) is None

@pytest.mark.parametrize("aiSkill", [0, 2.5, 4])
def test_invalid_ai_skill(aiSkill):
    board = Minesweeper(BEGINNER, 1)    # just for player view

    with pytest.raises(ValueError):
        getAiMoveInteractive(board.getPlayerView(), aiSkill, BEGINNER)

@pytest.mark.parametrize("aiLevel", [1, 2, 3])
def test_get_moves_for_auto_solve(aiLevel):
    # test AI auto solve on a general board with eligible moves

    board = Minesweeper(BEGINNER, aiLevel)
    board.createBoard(0, 0)

    moves = getMovesForAutoSolve(board, aiLevel, BEGINNER)
    assert board.state() in ("Victory", "Game Over: Loss")  # should result in either a win or loss
    assert moves is not None

    # verify that all moves are within bounds
    while moves is not None:
        action, moveRow, moveCol = moves.value
        assert action in ("dig", "flag")
        assert 0 <= moveRow < board.rows
        assert 0 <= moveCol < board.columns
        if action == "dig":
            assert board._external[moveRow][moveCol] == 1
        else:
            assert board._external[moveRow][moveCol]
        moves = moves.next

@pytest.mark.parametrize("aiLevel", [1, 2, 3])
def test_auto_solve_win(aiLevel):
    # test a win state for the autosolve with each AI level

    board = Minesweeper(BEGINNER, aiLevel)
    board.createBoard(0, 0)

    # flag all mines, AI solver will ignore these flagged cells
    # guarantees that the AI (easy, medium, hard) will win
    for i in range(board.rows):
        for j in range(board.columns):
            if board._internal[i][j] == -1: # mine
                board.flag(i, j)

    # get the sequence of moves and verify the game was won
    moves = getMovesForAutoSolve(board, aiLevel, BEGINNER)
    assert moves is not None
    assert board.state() == "Victory"
    assert board.status()   # true when win status

    # ensure that every move was valid
    while moves is not None:
        action, moveRow, moveCol = moves.value
        assert 0 <= moveRow < board.rows
        assert 0 <= moveCol < board.columns
        if action == "dig":
            assert board._internal[moveRow][moveCol] != -1
            assert board._external[moveRow][moveCol] == 1
        moves = moves.next

    for i in range(board.rows):
        for j in range(board.columns):
            if board._internal[i][j] == -1:
                assert board._external[i][j] == 2   # should still be flagged, not revealed
            else:
                assert board._external[i][j] == 1   # all safe cells should be revealed

@pytest.mark.parametrize("aiLevel", [1, 2, 3])
def test_auto_solve_loss(aiLevel):
    # test a loss state for the autosolve with each AI level

    # create a custom board that uses the AI's logic to force
    # a loss state
    mineList = [(1,0),(1,1)]
    board = make_custom_board(BEGINNER, aiLevel, mineList)
    for i in range(2):
        board.flag(i, 1)
    board.dig(0,0)

    # get sequence of moves and verify game lost
    moves = getMovesForAutoSolve(board, aiLevel, BEGINNER)
    assert moves is not None
    assert board.state() == "Game Over: Loss"
    
    # ensure every move before last (mine hit) was safe and valid
    while moves.next is not None:
        action, moveRow, moveCol = moves.value
        assert 0 <= moveRow < board.rows
        assert 0 <= moveCol < board.columns
        if action == "dig":
            assert board._internal[moveRow][moveCol] != -1
            assert board._external[moveRow][moveCol] == 1
        moves = moves.next

    # last move must have hit a mine
    action, moveRow, moveCol = moves.value
    assert 0 <= moveRow < board.rows
    assert 0 <= moveCol < board.columns
    if action == "dig":
        assert board._internal[moveRow][moveCol] == -1
        assert board._external[moveRow][moveCol] == 1