"""
Prologue Comment
File: backend_tests.py
Description: Tests the minesweeper.py to ensure
             everything behind the scenes is in working
             order.
Inputs:  difficulty, ai level, first-click row/column, mine count/mine position
Outputs: Pytest results of each test case
External sources: Original code with assistance by OpenAI 
                  ChatGPT for correctness. Logic is reviewed
                  and tested by the author.
Author: Khang Phan
Created: [Oct 5 2026]
"""

from minesweeper import Minesweeper
from difficulty_presets import BEGINNER
from difficulty_presets import INTERMEDIATE
from difficulty_presets import EXPERT
import pytest

## Helper Functions
def neighbors(board, row, col):
    neighbors = []

    # identify all cells in 3x3 area
    for i in range(max(0, row-1), min(board.rows, row+2)):
        for j in range(max(0, col-1), min(board.columns, col+2)):

            # exclude center cell
            if i != row or j != col:
                neighbors.append((i, j))
    return neighbors

def make_custom_board(difficulty, aiLevel, mineList):
    board = Minesweeper(difficulty, aiLevel)
    
    for row, col in mineList:
        # set custom mine positions
        board._internal[row][col] = -1

        # increment neighboring cells' adjacency counts
        for i in range(max(0, row-1), min(board.rows, row+2)):
            for j in range(max(0, col-1), min(board.columns, col+2)):
                if board._internal[i][j] != -1:
                    board._internal[i][j] += 1

    return board


## Test Cases
@pytest.mark.parametrize("difficulty, aiLevel, rows, columns, mines", [
    (BEGINNER, 1, 10, 10, 10),
    (INTERMEDIATE, 1, 16, 16, 40),
    (EXPERT, 1, 16, 30, 99),
    (BEGINNER, 2, 10, 10, 10),
    (BEGINNER, 3, 10, 10, 10)
])
def test_board_init(difficulty, aiLevel, rows, columns, mines):
    board = Minesweeper(difficulty, aiLevel)
    assert board.gameDifficultyObject == difficulty
    assert board.aiLevel == aiLevel
    assert board.rows == rows
    assert board.columns == columns
    assert board.mines == mines

    assert board.flags == 0
    assert board._digs == rows * columns - mines

    assert len(board._internal) == rows
    assert len(board._external) == rows
    for i in range(rows):
        assert len(board._internal[i]) == columns
        assert len(board._external[i]) == columns

        for j in range(columns):
            assert board._internal[i][j] == 0   # empty board, all internal cells empty
            assert board._external[i][j] == 0   # all external cells unrevealed

    assert not board.is_constructed
    assert not board.lost

@pytest.mark.parametrize("difficulty, aiLevel", [
    (BEGINNER, 0),
    (BEGINNER, 4),
    (BEGINNER, 2.5)
])
def test_invalid_init(difficulty, aiLevel):
    with pytest.raises(ValueError):
        Minesweeper(difficulty, aiLevel)

#WIP Change to use public methods
@pytest.mark.parametrize("difficulty, row, col", [
    (BEGINNER, 10, 0),
    (BEGINNER, 0, 10),
    # (BEGINNER, 5.5, 0),
    (BEGINNER, -1, 0),
    (INTERMEDIATE, 16, 0),
    (EXPERT, 29, 15),
    (EXPERT, 0, 30),
    (EXPERT, 16, 0)
])
def test_check_bounds(difficulty, row, col):
    board = Minesweeper(difficulty, 1)
    with pytest.raises(IndexError):
        board._checkBounds(row, col)

#WIP
# def test_create_board():

    # _internal = solution grid (-1 mine, 0-8 adjacent mines)
    # _external = player view (0 covered, 1 uncovered, 2 flagged)
@pytest.mark.parametrize("firstRow, firstCol", [
    (0, 0),
    (5, 5),
    (9, 9),
    (3, 0)
])
def test_first_click(firstRow, firstCol):
    board = Minesweeper(BEGINNER, 1)
    board.flag(firstRow, firstCol)  # test flagging before first click behavior
    board.createBoard(firstRow, firstCol)
    board.createBoard(0, 0)   # test to ensure a second call does nothing
    assert board.flags == 0
    assert board.is_constructed
    assert board._internal[firstRow][firstCol] != -1 
    assert board._external[firstRow][firstCol] == 1

    # _internal = solution grid (-1 mine, 0-8 adjacent mines)
    # _external = player view (0 covered, 1 uncovered, 2 flagged)
def test_adjacency_count():
    for i in range(10):
        board = Minesweeper(BEGINNER, 1)
        board.createBoard(0, 0)

        # for every cell on the board
        for row in range(board.rows):
            for col in range(board.columns):

                # if a cell has at least one adjacent mine
                if board._internal[row][col] > 0:
                    adjMineCount = 0

                    # verify the adjacency count is correct
                    for r, c in neighbors(board, row, col):
                        if board._internal[r][c] == -1:
                            adjMineCount += 1
                    assert board._internal[row][col] == adjMineCount

#WIP
# def test_dig():

    # _internal = solution grid (-1 mine, 0-8 adjacent mines)
    # _external = player view (0 covered, 1 uncovered, 2 flagged)
@pytest.mark.parametrize("row, col, mineList", [
    (0, 0, ((3,0), (3,1), (3,2), (3,3), (3,4), (0,4), (1,4), (2,4))),
    (1, 2, ((3,0), (3,1), (3,2), (3,3), (3,4), (0,4), (1,4), (2,4)))
])
def test_flood_fill(row, col, mineList):
    # set a custom board for flood fill test
    board = make_custom_board(BEGINNER, 1, mineList)

    board.dig(row, col)
    assert board._external[row][col] == 1
    # check that each neighbor of an empty cell that is revealed is also revealed (flood fill)
    for i in range(board.rows):
        for j in range(board.columns):

            if board._internal[i][j] == 0 and board._external[i][j] == 1:
                for r, c in neighbors(board, i, j):
                    assert board._external[r][c] == 1

            # ensure mines are still covered
            if board._internal[i][j] == -1:
                assert board._external[i][j] == 0

    # _internal = solution grid (-1 mine, 0-8 adjacent mines)
    # _external = player view (0 covered, 1 uncovered, 2 flagged)
def test_flag():
    board = Minesweeper(BEGINNER, 1)
    assert board.remaining() == 10

    # test flag placement
    for i in range(10):
        board.flag(0, i)
        assert board._external[0][i] == 2
    assert board.flags == 10
    assert board.remaining() == 0
    board.flag(1, 0)
    assert board._external[1][0] == 0
    assert board.flags == 10
    assert board.remaining() == 0

    # test removing a flag
    board.flag(0, 0)
    board.flag(0, 1)
    assert board._external[0][0] == 0
    assert board._external[0][1] == 0
    assert board.flags == 8
    assert board.remaining() == 2

    # test attempting to flag an uncovered cell
    board._external[1][0] = 1
    board.flag(1, 0)
    assert board._external[1][0] == 1
    assert board.flags == 8
    assert board.remaining() == 2

    # _internal = solution grid (-1 mine, 0-8 adjacent mines)
    # _external = player view (0 covered, 1 uncovered, 2 flagged)
#WIP Add more tests, add invalid chording (flags > adj count), add chording loss
@pytest.mark.parametrize("row, col, mineList", [
    (4, 3, ((4, 2), (5, 3), (3, 4)))
])
def test_chording(row, col, mineList):
    # create custom board for testing
    board = make_custom_board(BEGINNER, 1, mineList)
    for r, c in mineList:
        board.flag(r, c)
    board.dig(row, col)

    board.chord(row, col)
    for r, c in neighbors(board, row, col):

        # check that mines are still flagged
        if board._internal[r][c] == -1:
            assert board._external[r][c] == 2

        # check that all other cells are uncovered
        else:
            assert board._external[r][c] == 1

    # _internal = solution grid (-1 mine, 0-8 adjacent mines)
    # _external = player view (0 covered, 1 uncovered, 2 flagged)
def test_display():
    board = Minesweeper(BEGINNER, 1)
    board.flag(0, 0)

    board._internal[0][1] = -1  # set to mine
    board._external[0][1] = 1   # reveal mine

    board._internal[1][0] = 5   # set non-empty cell
    board._external[1][0] = 1   # reveal cell

    board._external[1][1] = 1   # reveal empty cell

    assert board.display(0, 0) == 0
    assert board.display(0, 1) == -1
    assert board.display(1, 1) == -2
    assert board.display(1, 0) == 5
    assert board.display(0, 2) == -3

    # _internal = solution grid (-1 mine, 0-8 adjacent mines)
    # _external = player view (0 covered, 1 uncovered, 2 flagged)
def test_win():
    board = Minesweeper(BEGINNER, 1)
    board.createBoard(1, 1)
    assert board.status() == False
    assert board.state() == "Playing"

    for row in range(board.rows):
        for col in range(board.columns):
            if board._internal[row][col] != -1:
                board.dig(row, col)

    assert board.status() == True
    assert board.state() == "Victory"

    # _internal = solution grid (-1 mine, 0-8 adjacent mines)
    # _external = player view (0 covered, 1 uncovered, 2 flagged)
def test_loss():
    board = Minesweeper(BEGINNER, 1)
    board.createBoard(1, 1)

    # compile mine locations
    mineList = []
    for row in range(board.rows):
        for col in range(board.columns):
            if board._internal[row][col] == -1:
                mineList.append((row, col))

    assert board.dig(mineList[0][0], mineList[0][1]) == 0
    assert board.lost == True
    assert board.status() == False
    assert board.state() == "Game Over: Loss"

    # for r, c in mineList:
    #     assert board._external[r][c] == 1   # all mines should now be revealed

    # _internal = solution grid (-1 mine, 0-8 adjacent mines)
    # _external = player view (0 covered, 1 uncovered, 2 flagged)
def test_reveal_all_mines():
    board = Minesweeper(BEGINNER, 1)
    board.createBoard(1, 1)
    board.revealAllMines()
    for row in range(board.rows):
        for col in range(board.columns):
            if board._internal[row][col] == -1:
                assert board._external[row][col] == 1