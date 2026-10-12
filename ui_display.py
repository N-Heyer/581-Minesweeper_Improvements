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
# Win/loss board screens added October 11, 2026 with OpenAI Codex assistance.
# external sources: https://www.pygame.org/docs/, Codex , Claude
# author: Emilia Davis and eliza m 
# improvement author: Andrew Kruckemyer

import pygame
from minesweeper import Minesweeper
from difficulty_presets import Difficulty
from ai_interactive_mode import applyAiMove
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
game_status = ""  # hint-bar text; MainGameplay and EndScreen replace this

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


def spriteIndex(tile):
    """Map a display() code onto the sprite sheet. Covered (-3) is sprite 0."""
    return tile + 3


def rowLabel(row):
    """Row header. The first row is 1."""
    return str(row + 1)


def columnLabel(col):
    """Column header. Column 0 is A."""
    return chr(ord("A") + col)


def flagsRemaining():
    """Flags the player can still place. Shown on the hint bar."""
    return board.mines - board.flags


def cellFromPixel(x, y):
    """Convert a window pixel to (row, col), or None when it misses the grid."""
    cell_px = cellSize()
    col = (x - label_offset) // cell_px
    row = (y - label_offset) // cell_px
    if not (0 <= row < board.rows and 0 <= col < board.columns):
        return None
    return row, col


# displays board
def showBoard(surface):
    cell_px = cellSize()
    sprites = getSprites(cell_px)
    label_font = getLabelFont(cell_px)
    for row in range(board.rows):
        for col in range(board.columns):
            # draw sprite onto surface at given position
            tile = board.display(row, col)
            surface.blit(sprites[spriteIndex(tile)], (col * cell_px + label_offset, row * cell_px + label_offset))

    # row labels 1..rows, centered beside each row (no anti-aliasing, white)
    for row in range(board.rows):
        label = label_font.render(rowLabel(row), False, (255, 255, 255))
        surface.blit(label, label.get_rect(center=(label_offset // 2, row * cell_px + label_offset + cell_px // 2)))

    # column labels A.. (A-J, A-P or A-T), centered above each column
    for col in range(board.columns):
        label = label_font.render(columnLabel(col), False, (255, 255, 255))
        surface.blit(label, label.get_rect(center=(col * cell_px + label_offset + cell_px // 2, label_offset // 2)))

    # Added 9/28/2026 (Andrew Kruckemyer, with help from Claude): controls hint bar
    bar_top = (board_size + label_size) * board_scale  # first pixel row below the board
    pygame.draw.rect(surface, (0, 0, 0), (0, bar_top, surface.get_width(), bar_height))
    hint = hint_font.render("R: Restart  |  Esc: Menu", False, (255, 255, 255))
    surface.blit(hint, (surface.get_width() // 2 - hint.get_width() // 2, bar_top + 8))
    # Added 9/29/2026 (Khang Phan): flag remaining counter
    flagCount = hint_font.render("Flags: " + str(flagsRemaining()), False, (255, 255, 255))
    surface.blit(flagCount, (12, bar_top + 8))
    status = hint_font.render(game_status, True, (255, 255, 255))
    surface.blit(status, (12, bar_top + 42))

# Menu choices map to backend AI levels; mine count is independent of AI skill.
# Medium/Hard integration added Oct 7, 2026 with OpenAI Codex assistance.
MODE_OPTIONS = [("player", "Player only"), ("interactive", "Interactive AI"),
                ("auto", "Auto-solve")]
AI_OPTIONS = [(1, "Easy"), (2, "Medium"), (3, "Hard")]
AI_DESCRIPTIONS = {
    1: "Easy opens random covered, unflagged cells.",
    2: "Medium uses nearby numbers to flag mines and open cells.",
    3: "Hard adds the 1-2-1 pattern to Medium's rules.",
}


def updateMineText(mines, character="", backspace=False):
    """Apply one setup-menu key. The mine field holds at most two digits."""
    if backspace:
        return mines[:-1]
    if character in "0123456789" and len(mines) < 2:
        return mines + character
    return mines


def mineCountAccepted(text, min_mines, max_mines):
    """True when the typed mine count is an integer inside this board size's range."""
    return text.isdigit() and min_mines <= int(text) <= max_mines


def statusText(mode, ai_pending, ai_stopped, skill_name):
    """Hint-bar status for the current turn. None leaves the previous text up."""
    if mode == "player":
        return "Player only"
    if mode == "auto" and ai_stopped:
        return "AI cannot continue. R: Restart | Esc: Menu"
    if ai_pending:
        if mode == "auto":
            return f"Auto-solve: {skill_name} AI"
        return f"AI turn: {skill_name}"
    if mode == "interactive":
        return "Your turn: uncover a cell or place/remove a flag"
    return None


def outcomeStatus(win):
    """Hint-bar text once the game is over. Matches Minesweeper.state()."""
    return "Victory" if win else "Game Over: Loss"


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
                    mines = updateMineText(mines, backspace=True)
                    error = ""
                elif event.unicode:
                    updated = updateMineText(mines, character=event.unicode)
                    if updated != mines:
                        mines = updated
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
                        if rect.collidepoint(event.pos):
                            ai_level = value
                start_requested = start_button.collidepoint(event.pos)
            if start_requested:
                size, min_mines, max_mines, _ = BOARD_SIZES[size_index]
                if mineCountAccepted(mines, min_mines, max_mines):
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
            "auto": "Watch the AI uncover cells and flag mines.",
        }
        screen.blit(hint_font.render(descriptions[mode], True, (200, 210, 225)), (32, 380))
        for rect, (value, label) in zip(ai_buttons, AI_OPTIONS):
            drawButton(rect, label, mode != "player" and ai_level == value,
                       enabled=mode != "player")
        detail = AI_DESCRIPTIONS[ai_level] if mode != "player" else "AI skill applies only to AI game modes."
        screen.blit(hint_font.render(detail, True, (200, 210, 225)), (32, 530))
        screen.blit(hint_font.render("All AI levels may guess and hit a mine.", True,
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
    ai_stopped = False
    skill_name = dict(AI_OPTIONS)[board.aiLevel]
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
            # Clicks on the row/column labels or the hint bar are ignored.
            cell = cellFromPixel(event.pos[0], event.pos[1])
            if cell is None:
                continue
            row, col = cell
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
                ai_stopped = True
                ai_pending = False
            else:
                result = applyAiMove(board, move)
                # Stop auto-play on a refused move (e.g. no flags remaining).
                ai_stopped = result == 2
                ai_pending = mode == "auto" and not ai_stopped
                next_ai_move = pygame.time.get_ticks() + 600

        if board.state() != "Playing":
            return board.state() == "Victory"
        status = statusText(mode, ai_pending, ai_stopped, skill_name)
        if status is not None:
            game_status = status
        # Clear the setup screen and previous frame before drawing gameplay.
        screen.fill((0, 0, 0))
        showBoard(screen)
        pygame.display.flip()
        clock.tick(60)


def drawEndScreen(win):
    """Keep the final board visible and put outcome/actions below it."""
    screen.fill((0, 0, 0))
    showBoard(screen)
    bar_top = label_offset + board_area
    pygame.draw.rect(screen, (18, 21, 28), (0, bar_top, screen.get_width(), bar_height))
    color = (120, 235, 150) if win else (255, 140, 140)
    title = font.render("Victory!" if win else "Game Over: Loss", True, color)
    screen.blit(title, (12, bar_top + 4))
    restart_button = pygame.Rect(290, bar_top + 6, 185, 32)
    menu_button = pygame.Rect(485, bar_top + 6, 205, 32)
    drawButton(restart_button, "Play again (R)", selected=True)
    drawButton(menu_button, "Settings (Enter)")
    detail = "All safe cells uncovered." if win else "All mines revealed."
    text = hint_font.render(detail + "  R: Restart | Enter / Esc: Menu", True, (230, 230, 230))
    screen.blit(text, (12, bar_top + 44))
    return restart_button, menu_button


def EndScreen(win):
    """Show a frozen final board; return restart or menu without accepting moves."""
    global game_status
    game_status = outcomeStatus(win)
    if not win:
        # Reveal flagged mines too; keep all other cells in their final state.
        board.revealAllMines()
    clock = pygame.time.Clock()
    while True:
        restart_button, menu_button = drawEndScreen(win)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_button.collidepoint(event.pos):
                    return "restart"
                if menu_button.collidepoint(event.pos):
                    return "menu"
        clock.tick(60)


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
        if EndScreen(win) == "menu":
            settings = None