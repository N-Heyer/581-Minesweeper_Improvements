# pip install pygame-ce --pre
# required for use

# prologue
# Description: pygame setup menu, board display, and player/AI input handling.
# Inputs: mouse and keyboard events, mine count, game mode, and AI skill.
# Outputs: selected game settings and a rendered Minesweeper game.
# AI settings added October 4, 2026 by Andrew Kruckemyer with OpenAI Codex
# assistance for menu layout, event handling, and backend integration.
# Board size tabs added October 6, 2026 with Claude assistance: the
# setup menu now offers 10x10 (10-20 mines), 16x16 (20-50 mines) and 20x20
# (60-99 mines) boards, and the board, labels and click mapping scale to fit.
# external sources: https://www.pygame.org/docs/, Codex , Claude
# author: Emilia Davis and eliza m 
# improvement author: Andrew Kruckemyer

import pygame
from minesweeper import Minesweeper
from difficulty_presets import Difficulty
import sys

pygame.init()

board_size = 160 # base board size
label_size = 16 # base label size
square_size = 16 # base square size
board_scale = 4 # change scale of board

# load font comic sans
font = pygame.font.SysFont("Comic Sans MS", 8 * board_scale)

# Added 9/28/2026 (Andrew Kruckemyer, with help from Claude): smaller font and a
# strip below the board that shows the R / Esc controls
hint_font = pygame.font.SysFont("Comic Sans MS", 5 * board_scale)
bar_height = 76  # pixels of extra window height for the hint bar

# load screen with given dimensions
# Changed 9/28/2026 (Andrew Kruckemyer, with help from Claude): window is bar_height taller
screen = pygame.display.set_mode(((board_size + label_size) * board_scale, (board_size + label_size) * board_scale + bar_height))

# load sprite sheet (the 12 raw 16x16 sprites; scaled per board size below)
sprite_sheet = pygame.image.load("SpriteSheet.png").convert()

# Board size tabs: (rows/columns, min mines, max mines, default mines).
# The 16x16 max of 50 keeps mine density near 20%, like the other two sizes.
BOARD_SIZES = [(10, 10, 20, 15), (16, 20, 50, 40), (20, 60, 99, 80)]

# The window stays the same size for every board; the playing area is always
# board_size * board_scale pixels (640) wide, so cells shrink as the grid grows:
# 10x10 -> 64 px cells, 16x16 -> 40 px cells, 20x20 -> 32 px cells.
board_area = board_size * board_scale
label_offset = label_size * board_scale  # pixels reserved for the row/column labels


def cellSize():
    """Pixel width of one cell for the current board."""
    return board_area // max(board.rows, board.columns)


_sprite_cache = {}
def getSprites(cell_px):
    """Return the 12 sprites scaled to cell_px, building them once per size."""
    if cell_px not in _sprite_cache:
        _sprite_cache[cell_px] = [
            pygame.transform.scale(sprite_sheet.subsurface((i * 16, 0, 16, 16)), (cell_px, cell_px))
            for i in range(12)
        ]
    return _sprite_cache[cell_px]


_label_font_cache = {}
def getLabelFont(cell_px):
    """Label font that fits inside one cell (same 32 pt font on the 10x10 board)."""
    pt = min(8 * board_scale, cell_px * 3 // 4)
    if pt not in _label_font_cache:
        _label_font_cache[pt] = pygame.font.SysFont("Comic Sans MS", pt)
    return _label_font_cache[pt]


# displays board
def showBoard(surface):
    cell_px = cellSize()
    sprites = getSprites(cell_px)
    label_font = getLabelFont(cell_px)
    for row in range(board.rows):
        for col in range(board.columns):
            # draw sprite onto surface at given position
            tile = board.display(row, col)
            surface.blit(sprites[tile + 3], (col * cell_px + label_offset, row * cell_px + label_offset))

    # row labels 1..rows, centered beside each row (no anti-aliasing, white)
    for row in range(board.rows):
        label = label_font.render(str(row + 1), False, (255, 255, 255))
        surface.blit(label, label.get_rect(center=(label_offset // 2, row * cell_px + label_offset + cell_px // 2)))

    # column labels A.. (A-J, A-P or A-T), centered above each column
    for col in range(board.columns):
        label = label_font.render(chr(ord('A') + col), False, (255, 255, 255))
        surface.blit(label, label.get_rect(center=(col * cell_px + label_offset + cell_px // 2, label_offset // 2)))

    # Added 9/28/2026 (Andrew Kruckemyer, with help from Claude): controls hint bar
    bar_top = (board_size + label_size) * board_scale  # first pixel row below the board
    pygame.draw.rect(surface, (0, 0, 0), (0, bar_top, surface.get_width(), bar_height))
    hint = hint_font.render("R: Restart  |  Esc: Menu", False, (255, 255, 255))
    surface.blit(hint, (surface.get_width() // 2 - hint.get_width() // 2, bar_top + 8))
    # Added 9/29/2026 (Khang Phan): flag remaining counter
    flagCount = hint_font.render("Flags: " + str(board.mines - board.flags), False, (255, 255, 255))
    surface.blit(flagCount, (12, bar_top + 8))
    status = hint_font.render(game_status, True, (255, 255, 255))
    surface.blit(status, (12, bar_top + 42))

# Menu choices map to backend AI levels. Medium and Hard stay disabled until
# their solvers are implemented; board mine count is independent of AI skill.
MODE_OPTIONS = [("player", "Player only"), ("interactive", "Interactive AI"),
                ("auto", "Auto-solve")]
AI_OPTIONS = [(1, "Easy"), (2, "Medium (soon)"), (3, "Hard (soon)")]


def drawButton(rect, label, selected=False, enabled=True):
    """Draw one menu control with a visible selected or disabled state."""
    color = (45, 105, 165) if selected else (55, 60, 70)
    if not enabled:
        color = (30, 32, 38)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (130, 180, 230) if selected else (90, 95, 105),
                     rect, width=2, border_radius=8)
    text = hint_font.render(label, True, (255, 255, 255) if enabled else (130, 130, 130))
    screen.blit(text, text.get_rect(center=rect.center))


def DoSetup():
    """Return (board size, mine count, game mode, AI level) after valid setup input."""
    size_index = 0  # index into BOARD_SIZES; starts on the 10x10 tab
    mines, mode, ai_level = str(BOARD_SIZES[0][3]), "player", 1
    error = ""
    clock = pygame.time.Clock()
    size_buttons = [pygame.Rect(32 + i * 216, 120, 208, 52) for i in range(3)]
    mode_buttons = [pygame.Rect(32 + i * 216, 315, 208, 52) for i in range(3)]
    ai_buttons = [pygame.Rect(32 + i * 216, 460, 208, 52) for i in range(3)]
    start_button = pygame.Rect(232, 655, 240, 56)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            start_requested = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    start_requested = True
                elif event.key == pygame.K_BACKSPACE:
                    mines = mines[:-1]
                    error = ""
                elif event.unicode in "0123456789" and event.unicode and len(mines) < 2:
                    mines += event.unicode
                    error = ""
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Switching board size resets the mine count to that size's default
                for i, rect in enumerate(size_buttons):
                    if rect.collidepoint(event.pos) and i != size_index:
                        size_index = i
                        mines = str(BOARD_SIZES[i][3])
                        error = ""
                for rect, (value, _) in zip(mode_buttons, MODE_OPTIONS):
                    if rect.collidepoint(event.pos):
                        mode = value
                if mode != "player":
                    for rect, (value, _) in zip(ai_buttons, AI_OPTIONS):
                        if rect.collidepoint(event.pos) and value == 1:
                            ai_level = value
                start_requested = start_button.collidepoint(event.pos)
            if start_requested:
                size, min_mines, max_mines, _ = BOARD_SIZES[size_index]
                if mines.isdigit() and min_mines <= int(mines) <= max_mines:
                    return size, int(mines), mode, ai_level
                error = f"Enter a mine count from {min_mines} to {max_mines} for {size}x{size}."

        size, min_mines, max_mines, _ = BOARD_SIZES[size_index]
        screen.fill((18, 21, 28))
        title = font.render("Game settings", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 45)))
        for i, (rect, (s, lo, hi, _)) in enumerate(zip(size_buttons, BOARD_SIZES)):
            drawButton(rect, f"{s}x{s}  ({lo}-{hi})", i == size_index)
        for text, y in [("Board size", 85),
                        (f"Mines ({min_mines}-{max_mines}): " + (mines or "_"), 190),
                        ("Backspace to edit; type your mine count.", 230),
                        ("Game mode", 280), ("AI skill", 425)]:
            screen.blit(hint_font.render(text, True, (230, 230, 230)), (32, y))
        for rect, (value, label) in zip(mode_buttons, MODE_OPTIONS):
            drawButton(rect, label, mode == value)
        descriptions = {
            "player": "Play the board yourself without AI turns.",
            "interactive": "You and the AI take turns on the same board.",
            "auto": "Watch the AI open one cell at a time.",
        }
        screen.blit(hint_font.render(descriptions[mode], True, (200, 210, 225)), (32, 380))
        for rect, (value, label) in zip(ai_buttons, AI_OPTIONS):
            drawButton(rect, label, mode != "player" and ai_level == value,
                       enabled=mode != "player" and value == 1)
        detail = "Easy opens random covered, unflagged cells." if mode != "player" else "AI skill applies only to AI game modes."
        screen.blit(hint_font.render(detail, True, (200, 210, 225)), (32, 530))
        screen.blit(hint_font.render("Medium and Hard solvers are not available yet.", True,
                                    (170, 180, 195)), (32, 565))
        if error:
            screen.blit(hint_font.render(error, True, (255, 140, 140)), (32, 610))
        drawButton(start_button, "Start game / Enter", selected=True)
        pygame.display.flip()
        clock.tick(60)


def MainGameplay(mode):
    """Run player input and timed AI turns without blocking the window."""
    global game_status
    clock = pygame.time.Clock()
    ai_pending = mode == "auto"
    next_ai_move = pygame.time.get_ticks() + 600
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                if event.key == pygame.K_ESCAPE:
                    return "menu"
            # Ignore board input while the AI owns the turn or the game is over.
            if (event.type != pygame.MOUSEBUTTONDOWN or mode == "auto"
                    or ai_pending or board.state() != "Playing"):
                continue
            # Convert the click to a cell using the current board's cell size
            cell_px = cellSize()
            col = (event.pos[0] - label_offset) // cell_px
            row = (event.pos[1] - label_offset) // cell_px
            if not (0 <= row < board.rows and 0 <= col < board.columns):
                continue
            before = board.getPlayerView()
            if event.button == 1:
                # The backend clears pre-game flags and builds the first opening.
                if board.dig(row, col) == 2:
                    board.chord(row, col)
            elif event.button == 3:
                board.flag(row, col)
            # A successful dig, chord, or flag action gives the AI one turn.
            if (mode == "interactive" and board.is_constructed
                    and before != board.getPlayerView()
                    and board.state() == "Playing"):
                ai_pending = True
                next_ai_move = pygame.time.get_ticks() + 600

        if ai_pending and board.state() == "Playing" and pygame.time.get_ticks() >= next_ai_move:
            move = board.getAIMove()
            if move is None:
                # No legal move: let the user restart or return to setup.
                game_status = "AI has no legal moves. R: Restart | Esc: Menu"
                ai_pending = False
            else:
                if not board.is_constructed:
                    board.createBoard(*move)
                else:
                    board.dig(*move)
                ai_pending = mode == "auto"
                next_ai_move = pygame.time.get_ticks() + 600

        if board.state() != "Playing":
            return board.state() == "Victory"
        if mode == "player":
            game_status = "Player only"
        elif ai_pending:
            game_status = "Auto-solve: Easy AI" if mode == "auto" else "AI turn: Easy"
        elif mode == "interactive":
            game_status = "Your turn: uncover a cell or place/remove a flag"
        # Clear the setup screen and previous frame before drawing gameplay.
        screen.fill((0, 0, 0))
        showBoard(screen)
        pygame.display.flip()
        clock.tick(60)


def EndScreen(win):
    running = True
    shouldContinue = False
    while running: # loop to run end screen
        for event in pygame.event.get(): # i copied this from above :3
            # ends program if user clicks X
            if event.type == pygame.QUIT:
                # Added 9/28/2026 (Andrew Kruckemyer): close the window right away
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                shouldContinue = True
                running = False
        # display end screen
        screen.fill((0, 0, 0)) # fill screen with black
        if win:
            text = font.render("You win. :) | Press enter to play again.", False, (255, 255, 255)) # show win text
        else:
            text = font.render("You lose. :( | Press enter to play again.", False, (255, 255, 255)) # show lose text
        screen.blit(text, ((board_size + label_size) * board_scale // 2 - text.get_width() // 2, (board_size + label_size) * board_scale // 2 - text.get_height() // 2)) # center text
        pygame.display.flip() # update display
    return shouldContinue


# Remember all settings on restart; returning to the menu allows new choices.
# Main guard also lets UI helpers be imported for checks without starting a game.
if __name__ == "__main__":
    settings = None
    game_status = ""
    while True:
        if settings is None:
            settings = DoSetup()
        size, mines, mode, ai_level = settings
        board = Minesweeper(Difficulty(size, size, mines), aiLevel=ai_level)
        win = MainGameplay(mode)
        if win == "restart":
            continue
        if win == "menu":
            settings = None
            continue
        if not EndScreen(win):
            break
        settings = None