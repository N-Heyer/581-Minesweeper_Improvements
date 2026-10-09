"""
Prologue Comment
File: test_backend.py
Description: Tests minesweeper.py to ensure
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

## HELPER FUNCTIONS

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
    board.is_constructed = True

    return board


## TEST CASES

@pytest.mark.parametrize("difficulty, aiLevel, rows, columns, mines", [
    (BEGINNER, 1, 10, 10, 10),
    (INTERMEDIATE, 1, 16, 16, 40),
    (EXPERT, 1, 16, 30, 99),
    (BEGINNER, 2, 10, 10, 10),
    (BEGINNER, 3, 10, 10, 10)
])
def test_board_init(difficulty, aiLevel, rows, columns, mines):
    # test board initialization, check that default settings are enforced

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
    # test invalid board initializations

    with pytest.raises(ValueError):
        Minesweeper(difficulty, aiLevel)

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
def test_check_invalid_bounds(difficulty, row, col):
    # test bound checking of class methods,
    # ensure invalid inputs raise IndexError

    board = Minesweeper(difficulty, 1)

    with pytest.raises(IndexError):
        board.createBoard(row, col)

    with pytest.raises(IndexError):
        board.dig(row, col)

    with pytest.raises(IndexError):
        board.flag(row, col)

    with pytest.raises(IndexError):
        board.chord(row, col)

    with pytest.raises(IndexError):
        board.display(row, col)

@pytest.mark.parametrize("difficulty, row, col", [
    (BEGINNER, 0, 0),
    (BEGINNER, 0, 6),
    (INTERMEDIATE, 0, 0),
    (INTERMEDIATE, 15, 15),
    (EXPERT, 0, 0),
    (EXPERT, 0, 20)
])
def test_create_board(difficulty, row, col):
    # test createBoard(), ensure mine count is correct

    board = Minesweeper(difficulty, 1)
    board.createBoard(row, col)
    board.createBoard(row, col) # ensure a second call does nothing

    # check that number of mines is correct
    mineCount = 0
    for i in range(board.rows):
        for j in range(board.columns):
            if board._internal[i][j] == -1:
                mineCount += 1

    assert board.mines == mineCount
    assert board.is_constructed

@pytest.mark.parametrize("firstRow, firstCol", [
    (0, 0),
    (5, 5),
    (9, 9),
    (3, 0)
])
def test_first_click(firstRow, firstCol):
    # test safe first click,
    # behavior when placing flags before first click

    board = Minesweeper(BEGINNER, 1)
    board.flag(firstRow, firstCol)  # test flagging before first click behavior
    board.createBoard(firstRow, firstCol)
    assert board.flags == 0 # the flag is removed by first click
    assert board._internal[firstRow][firstCol] != -1    # first click can't be a mine
    assert board._external[firstRow][firstCol] == 1     # cell should be revealed

def test_adjacency_count():
    # test that the adjacency count of cells correctly
    # identifies the number of mines adjacent

    for _ in range(10):
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
                        if board._internal[r][c] == -1: # if mine
                            adjMineCount += 1
                    assert board._internal[row][col] == adjMineCount

def test_dig():
    for _ in range(10):
        board = Minesweeper(BEGINNER, 1)
        board.createBoard(0, 0)
        assert board.dig(0, 0) == 2 # test that digging an already revealed cell does nothing

        # find a covered non-mine cell to dig
        target = None
        for i in range(board.rows):
            for j in range(board.columns):
                # not a mine, covered cell
                if board._internal[i][j] != -1 and board._external[i][j] == 0:
                    target = (i, j)
                    break
            if target is not None:
                break
        assert board.dig(target[0], target[1]) == 1

        cellsRevealed = 0
        for i in range(board.rows):
            for j in range(board.columns):
                if board._external[i][j] == 1:
                    cellsRevealed += 1

        assert board._digs == board.rows * board.columns - board.mines - cellsRevealed

@pytest.mark.parametrize("row, col, mineList, expectedRevealedCells", [
    (0, 0, [(3,0), (3,1), (3,2), (3,3), (3,4), (0,4), (1,4), (2,4)], 
        [(0,0), (1,0), (2,0), (0,1), (1,1), (2,1), (0,2), (1,2), (2,2), (0,3), (1,3), (2,3)]),
    (1, 2, ((3,0), (3,1), (3,2), (3,3), (3,4), (0,4), (1,4), (2,4)),
        [(0,0), (1,0), (2,0), (0,1), (1,1), (2,1), (0,2), (1,2), (2,2), (0,3), (1,3), (2,3)]),
    (0, 0, [(3,0), (0,3), (1,5), (4,4), (5,2)],
        [(0,0), (0,1), (1,0), (1,1), (1,2), (1,3), (1,4),
         (0,2), (2,0), (2,1), (2,2), (2,3), (3,2), (2,3), (2,4),
         (3,1), (3,2), (3,3), (3,4), (4,1), (4,2), (4,3)]),
    (4, 4, [(0,0), (5,4)], 
        [(4,4)])
])
def test_flood_fill(row, col, mineList, expectedRevealedCells):
    # test that uncovering an empty cell with no adjacent mines will reveal all neighboring cells

    # set a custom board for flood fill test
    board = make_custom_board(BEGINNER, 1, mineList)

    board.dig(row, col)

    # check that each neighbor of an empty cell that is revealed also gets revealed (flood fill)
    for r, c in expectedRevealedCells:
        assert board._external[r][c] == 1   # revealed

    # check that cells not adjacent to a revealed empty cell are not accidentally uncovered
    for i in range(board.rows):
        for j in range(board.columns):
            if (i, j) not in expectedRevealedCells:
                assert board._external[i][j] == 0   # hidden

def test_flag():
    # test various flagging behaviors

    board = Minesweeper(BEGINNER, 1)
    assert board.remaining() == 10  # start with 10 flags on BEGINNER

    # test flag placement
    for i in range(10):
        board.flag(0, i)
        assert board._external[0][i] == 2
    assert board.flags == 10
    assert board.remaining() == 0
    # test that attempting to flag when remaining() is 0 results in nothing happening
    board.flag(1, 0)
    assert board._external[1][0] == 0   # still an unflagged, hidden cell
    assert board.flags == 10
    assert board.remaining() == 0

    # test removing a flag
    board.flag(0, 0)
    board.flag(0, 1)
    assert board._external[0][0] == 0   # unflagged, hidden cell
    assert board._external[0][1] == 0
    assert board.flags == 8
    assert board.remaining() == 2

    # test attempting to flag an uncovered cell
    board._external[1][0] = 1   # reveal a cell
    board.flag(1, 0)
    assert board._external[1][0] == 1   # still uncovered, not flagged
    assert board.flags == 8
    assert board.remaining() == 2

@pytest.mark.parametrize("row, col, mineList", [
    (4, 3, [(4,2), (5,3), (3,4)]),
    (7, 2, [(7,1), (6,2), (8,2), (7,3), (8,3)]),
    (0, 0, [(1,1)]),
    (0, 0, [(0,1), (1,0), (1,1)]),
    (3, 9, [(4,8), (2,9)])
])
def test_chording(row, col, mineList):
    # tests chording with invalid and valid flag counts

    # create custom board for testing
    board = make_custom_board(BEGINNER, 1, mineList)
    board.dig(row, col)

    # flag all mines
    for r, c in mineList:
        board.flag(r, c)

    assert board.chord(row, col) == 1   # progress made
    for r, c in neighbors(board, row, col):

        # check that mines are still flagged
        if board._internal[r][c] == -1:
            assert board._external[r][c] == 2

        # check that all other cells are uncovered
        else:
            assert board._external[r][c] == 1

@pytest.mark.parametrize("row, col, mineList, flagList", [
    (4, 3, [(4,2), (5,3), (3,4)],
        [(4,2), (5,3), (3,4), (5,2)]),
    (4, 3, [(4,2), (5,3), (3,4)],
        [(4,2), (5,3)])
])
def test_invalid_chording(row, col, mineList, flagList):
    # tests attempting to chord when # of flags != cell's adjacency count

    # create custom board
    board = make_custom_board(BEGINNER, 1, mineList)
    board.dig(row, col)

    # set flags
    for r, c in flagList:
        board.flag(r, c)

    assert board.chord(row, col) == 2   # nothing happens

    # check that no neighbors were revealed
    for r, c in neighbors(board, row, col):
        if (r, c) in flagList:
            assert board._external[r][c] == 2
        else:
            assert board._external[r][c] == 0

@pytest.mark.parametrize("row, col, mineList, flagList", [
    (4, 3, [(4,2), (5,3), (3,4)],
        [(4,2), (5,3), (3,2)]),
    (7, 2, [(7,1), (6,2), (8,2), (7,3), (8,3)],
        [(6,1), (7,1), (8,1), (6,2), (6,3)]),
    (0, 0, [(1,1)],
        [(0,1)]),
    (3, 9, [(4,8), (2,9)],
        [(3,8), (4,9)])
])
def test_chording_loss(row, col, mineList, flagList):
    # test chording when a mine is revealed due to improper flag placement

    board = make_custom_board(BEGINNER, 1, mineList)
    board.dig(row, col)

    # purposefully don't flag every mine, flag safe cells
    for r, c in flagList:
        board.flag(r, c)

    assert board.chord(row, col) == 0   # mine hit
    assert board.lost
    assert board.state() == "Game Over: Loss"

def test_display():
    # test that display function returns proper values

    board = Minesweeper(BEGINNER, 1)
    board.flag(0, 0)

    board._internal[0][1] = -1  # set to mine
    board._external[0][1] = 1   # reveal mine

    board._internal[1][0] = 5   # set non-empty cell
    board._external[1][0] = 1   # reveal cell

    board._external[1][1] = 1   # reveal empty cell

    assert board.display(0, 0) == 0     # flag
    assert board.display(0, 1) == -1    # mine
    assert board.display(1, 1) == -2    # empty cell (0)
    assert board.display(1, 0) == 5     # cell with adjacency count
    assert board.display(0, 2) == -3    # covered

def test_win():
    # test the initial status and state
    # test status and state after all non-mine cells are revealed (win)

    board = Minesweeper(BEGINNER, 1)
    board.createBoard(1, 1)
    # initial status/state
    assert board.status() == False
    assert board.state() == "Playing"

    for row in range(board.rows):
        for col in range(board.columns):
            if board._internal[row][col] != -1: # mine
                board.dig(row, col)

    assert board.status() == True
    assert board.state() == "Victory"

    for row in range(board.rows):
        for col in range(board.columns):
            if board._internal[row][col] == -1:
                assert board._external[row][col] == 0   # mines are still covered

def test_loss():
    # test status and state when clicking a mine (loss)

    board = Minesweeper(BEGINNER, 1)
    board.createBoard(1, 1)

    # compile mine locations
    mineList = []
    for row in range(board.rows):
        for col in range(board.columns):
            if board._internal[row][col] == -1: # not mine
                mineList.append((row, col))

    assert board.dig(mineList[0][0], mineList[0][1]) == 0   # verify that dig returns that a mine was dug
    assert board.lost == True
    assert board.status() == False
    assert board.state() == "Game Over: Loss"

def test_reveal_all_mines():
    # test that all mines on a board are revealed when revealAllMines() is called

    board = Minesweeper(BEGINNER, 1)
    board.createBoard(1, 1)
    board.revealAllMines()

    # check that every mine on the board is revealed
    for row in range(board.rows):
        for col in range(board.columns):
            if board._internal[row][col] == -1: # mine
                assert board._external[row][col] == 1   # revealed