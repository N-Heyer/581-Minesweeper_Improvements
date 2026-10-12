"""
Prologue Comment
File: test_frontend.py
Description: Tests the pygame UI rules in ui_display.py: board-size
             presets, click-to-cell mapping, the setup mine field,
             sprite and label choice, the flag counter, and the
             hint-bar status text.
Inputs:  board size, pixel position, mine-field keystrokes,
         display() tile codes, game mode
Outputs: Pytest results of each test case
External sources: None
Author: QA (frontend unit tests)
Created: [Oct 11 2026]
"""
import pygame
import pytest

import ui_display as ui
from difficulty_presets import Difficulty
from minesweeper import Minesweeper


def use_board(size_index):
    # Point the UI at one of the three menu board sizes.
    size, _lo, _hi, default = ui.BOARD_SIZES[size_index]
    ui.board = Minesweeper(Difficulty(size, size, default), aiLevel=1)
    ui.game_status = "Player only"
    return ui.board


def test_menu_mine_counts_are_legal():
    # Every count the setup menu can start with is a legal Difficulty,
    # and the typed default sits inside that size's min/max.
    assert len(ui.BOARD_SIZES) == 3
    for size, lo, hi, default in ui.BOARD_SIZES:
        assert 1 <= lo <= default <= hi < size * size
        for mines in (lo, default, hi):
            assert Difficulty(size, size, mines).mines == mines


def test_menu_modes_match_the_backend():
    # The setup menu's AI levels are the only ones Minesweeper accepts.
    assert [value for value, _label in ui.MODE_OPTIONS] == ["player", "interactive", "auto"]
    assert [level for level, _label in ui.AI_OPTIONS] == [1, 2, 3]
    assert set(ui.AI_DESCRIPTIONS) == {1, 2, 3}


@pytest.mark.parametrize("size_index, pixels", [
    (0, 64),
    (1, 40),
    (2, 32),
])
def test_cell_size_fills_the_board(size_index, pixels):
    # 10x10, 16x16, and 20x20 must use the whole 640px playing area,
    # or the last row and column would have a dead pixel strip.
    use_board(size_index)
    assert ui.cellSize() == pixels
    assert ui.cellSize() * ui.board.rows == ui.board_area
    assert ui.cellSize() * ui.board.columns == ui.board_area


@pytest.mark.parametrize("size_index", [0, 1, 2])
def test_every_cell_accepts_its_corner_and_center(size_index):
    use_board(size_index)
    cell_px = ui.cellSize()
    for row in range(ui.board.rows):
        for col in range(ui.board.columns):
            left = ui.label_offset + col * cell_px
            top = ui.label_offset + row * cell_px
            assert ui.cellFromPixel(left, top) == (row, col)
            assert ui.cellFromPixel(left + cell_px // 2, top + cell_px // 2) == (row, col)
            assert ui.cellFromPixel(left + cell_px - 1, top + cell_px - 1) == (row, col)


@pytest.mark.parametrize("size_index", [0, 1, 2])
def test_clicks_outside_the_grid_are_ignored(size_index):
    # Labels, the hint bar, and the pixel just past the grid are not cells.
    use_board(size_index)
    cell_px = ui.cellSize()
    assert ui.cellFromPixel(0, 0) is None
    assert ui.cellFromPixel(-1, -1) is None
    assert ui.cellFromPixel(ui.label_offset - 1, ui.label_offset + cell_px // 2) is None
    assert ui.cellFromPixel(ui.label_offset + cell_px // 2, ui.label_offset - 1) is None
    assert ui.cellFromPixel(ui.label_offset + ui.board_area, ui.label_offset) is None
    assert ui.cellFromPixel(ui.label_offset, ui.label_offset + ui.board_area) is None
    assert ui.cellFromPixel(12, ui.label_offset + ui.board_area + 8) is None


@pytest.mark.parametrize("win", [True, False])
def test_end_screen_buttons_sit_in_the_hint_bar(win):
    # Play again / Settings must fit the window, miss each other,
    # and must not land on a cell.
    use_board(0)
    restart, menu = ui.drawEndScreen(win)
    width, height = ui.screen.get_size()
    assert 0 <= restart.left and restart.right <= width
    assert 0 <= menu.left and menu.right <= width
    assert restart.bottom <= height and menu.bottom <= height
    assert not restart.colliderect(menu)
    bar_top = ui.label_offset + ui.board_area
    assert restart.top >= bar_top and menu.top >= bar_top
    assert ui.cellFromPixel(*restart.center) is None
    assert ui.cellFromPixel(*menu.center) is None


@pytest.mark.parametrize("start, character, backspace, expected", [
    ("", "1", False, "1"),
    ("1", "5", False, "15"),
    ("9", "9", False, "99"),
    ("15", "3", False, "15"),
    ("15", "", True, "1"),
    ("1", "", True, ""),
    ("", "", True, ""),
    ("1", "a", False, "1"),
    ("1", "", False, "1"),
])
def test_update_mine_text(start, character, backspace, expected):
    # The field takes digits only, and never more than two of them.
    assert ui.updateMineText(start, character, backspace) == expected


@pytest.mark.parametrize("size_index, text, accepted", [
    (0, "10", True),
    (0, "15", True),
    (0, "20", True),
    (0, "9", False),
    (0, "21", False),
    (0, "09", False),
    (0, "", False),
    (0, "ab", False),
    (1, "19", False),
    (1, "20", True),
    (1, "40", True),
    (1, "50", True),
    (1, "51", False),
    (2, "59", False),
    (2, "60", True),
    (2, "80", True),
    (2, "99", True),
    (2, "100", False),
])
def test_mine_count_accepted(size_index, text, accepted):
    _size, lo, hi, _default = ui.BOARD_SIZES[size_index]
    assert ui.mineCountAccepted(text, lo, hi) is accepted


def test_two_digits_can_type_every_legal_count():
    # The field stops at two characters, so a legal count must fit in two digits.
    for _size, lo, hi, default in ui.BOARD_SIZES:
        for mines in (lo, default, hi):
            assert len(str(mines)) <= 2


@pytest.mark.parametrize("tile, index", [
    (-3, 0),  # covered
    (-2, 1),  # revealed empty
    (-1, 2),  # mine
    (0, 3),   # flag
    (1, 4),   # number 1
    (8, 11),  # number 8, last sprite
])
def test_sprite_index(tile, index):
    assert ui.spriteIndex(tile) == index
    assert 0 <= index < 12


def test_sprites_are_cached_per_cell_size():
    ui._sprite_cache.clear()
    first = ui.getSprites(64)
    assert ui.getSprites(64) is first
    assert len(first) == 12
    assert all(sprite.get_size() == (64, 64) for sprite in first)
    smaller = ui.getSprites(32)
    assert smaller is not first
    assert smaller[0].get_size() == (32, 32)


def test_label_font_shrinks_to_fit_the_cell():
    # 10x10 stays at 32 pt. 16x16 and 20x20 shrink so the header fits the cell.
    ui._label_font_cache.clear()
    ui.getLabelFont(64)
    ui.getLabelFont(40)
    ui.getLabelFont(32)
    assert set(ui._label_font_cache) == {32, 30, 24}
    assert ui.getLabelFont(64) is ui._label_font_cache[32]


def test_headers_match_the_board_size():
    assert [ui.columnLabel(col) for col in range(10)] == list("ABCDEFGHIJ")
    assert [ui.columnLabel(col) for col in range(16)] == list("ABCDEFGHIJKLMNOP")
    assert ui.columnLabel(19) == "T"
    assert [ui.rowLabel(row) for row in range(10)] == [str(n) for n in range(1, 11)]
    assert [ui.rowLabel(row) for row in range(20)] == [str(n) for n in range(1, 21)]


def test_flags_remaining_drops_as_flags_are_placed():
    board = use_board(0)
    assert ui.flagsRemaining() == board.mines
    board.flag(0, 0)
    board.flag(0, 1)
    assert ui.flagsRemaining() == board.mines - 2
    board.flag(0, 0)
    assert ui.flagsRemaining() == board.mines - 1


def _paint_cell(board, row, col, external, internal=0):
    board._external[row][col] = external
    board._internal[row][col] = internal


def test_show_board_blits_the_sprite_for_each_tile():
    # display() codes have to land on the matching sprite, not a neighbor.
    board = use_board(0)
    _paint_cell(board, 0, 0, 0)          # covered
    _paint_cell(board, 0, 1, 1, 0)       # revealed empty
    _paint_cell(board, 0, 2, 1, -1)      # mine
    _paint_cell(board, 0, 3, 2)          # flag
    _paint_cell(board, 0, 4, 1, 1)       # number 1
    _paint_cell(board, 1, 0, 1, 8)       # number 8

    surface = pygame.Surface(ui.screen.get_size()).convert()
    surface.fill((1, 2, 3))
    ui.showBoard(surface)

    cell_px = ui.cellSize()
    sprites = ui.getSprites(cell_px)
    for row, col in ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0)):
        tile = board.display(row, col)
        drawn = surface.subsurface((
            ui.label_offset + col * cell_px,
            ui.label_offset + row * cell_px,
            cell_px,
            cell_px,
        ))
        assert pygame.image.tobytes(drawn, "RGB") == pygame.image.tobytes(sprites[ui.spriteIndex(tile)], "RGB")


@pytest.mark.parametrize("mode, ai_pending, ai_stopped, skill, expected", [
    ("player", False, False, "Easy", "Player only"),
    ("player", True, False, "Easy", "Player only"),
    ("auto", True, False, "Hard", "Auto-solve: Hard AI"),
    ("auto", False, True, "Medium", "AI cannot continue. R: Restart | Esc: Menu"),
    ("interactive", True, False, "Easy", "AI turn: Easy"),
    ("interactive", False, False, "Medium", "Your turn: uncover a cell or place/remove a flag"),
])
def test_status_text(mode, ai_pending, ai_stopped, skill, expected):
    assert ui.statusText(mode, ai_pending, ai_stopped, skill) == expected


def test_idle_auto_solve_keeps_the_previous_status():
    # Auto-solve with no pending move and no stop has nothing new to say.
    assert ui.statusText("auto", False, False, "Easy") is None


def test_outcome_status_matches_the_backend():
    assert ui.outcomeStatus(True) == "Victory"
    assert ui.outcomeStatus(False) == "Game Over: Loss"
