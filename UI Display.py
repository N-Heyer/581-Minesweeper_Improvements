# pip install pygame-ce --pre
# required for use

# prologue
# external sources: https://www.pygame.org/docs/
# author: Emilia Davis and eliza m 
# improvement author: Andrew Kruckemyer

import pygame
from minesweeper import Minesweeper
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
bar_height = 40  # pixels of extra window height for the hint bar

# load screen with given dimensions
# Changed 9/28/2026 (Andrew Kruckemyer, with help from Claude): window is bar_height taller
screen = pygame.display.set_mode(((board_size + label_size) * board_scale, (board_size + label_size) * board_scale + bar_height))

# load sprite sheet and create list of sprites
surface = pygame.image.load("SpriteSheet.png").convert()
sprites = []
# for every sprite in the sheet
for i in range(12):
    # find the area where the sprite sits
    sprite = surface.subsurface((i * 16, 0, 16, 16))
    # scale the sprite to fit the board
    sprite = pygame.transform.scale(sprite, (square_size * board_scale, square_size * board_scale))
    # add the sprite to the list of sprites
    sprites.append(sprite)

# displays board
def showBoard(surface):
    for row in range(10):
        for col in range(10):
            # draw sprite onto surface at given position
            #print(row, col)
            tile = board.display(row, col)
            surface.blit(sprites[tile + 3], (col * square_size * board_scale + label_size * board_scale, row * square_size * board_scale + label_size * board_scale))
                    
    for row in range(10):
        label = font.render(str(row + 1), False, (255, 255, 255)) # labels 1-10, no anti-aliasing, white color
        surface.blit(label, (0, row * square_size * board_scale + label_size * board_scale)) # 

    # create labels for columns A - J
    for col in range(10):
        label = font.render(chr(ord('A') + col), False, (255, 255, 255)) # labels A-J, no anti-aliasing, white color
        surface.blit(label, (col * square_size * board_scale + label_size * board_scale, 0)) 

    # Added 9/28/2026 (Andrew Kruckemyer, with help from Claude): controls hint bar
    bar_top = (board_size + label_size) * board_scale  # first pixel row below the board
    pygame.draw.rect(surface, (0, 0, 0), (0, bar_top, surface.get_width(), bar_height))
    hint = hint_font.render("R: Restart  |  Esc: Menu", False, (255, 255, 255))
    surface.blit(hint, (surface.get_width() // 2 - hint.get_width() // 2, bar_top + (bar_height - hint.get_height()) // 2))
    # Added 9/29/2026 (Khang Phan): flag remaining counter
    flagCount = hint_font.render("Flags: " + str(board.m - board.flags), False, (255, 255, 255))
    surface.blit(flagCount, (flagCount.get_width(), bar_top + (bar_height - flagCount.get_height()) // 2))

def DoSetup():
    running = True
    menu_running = True
    mines = ""
    is_valid = True
    m = None
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Added 9/28/2026 (Andrew Kruckemyer): close the window right away
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                is_valid = True
                if event.key == pygame.K_RETURN:
                    try:
                        m = int(mines)
                        if 10 <= m <= 20:
                            menu_running = False
                        else:
                            raise ValueError
                    except ValueError:
                        is_valid = False
                elif event.key == pygame.K_BACKSPACE:
                    if mines: #checks if string is empty
                        mines = mines[:-1]
                elif event.unicode.isdigit():
                    mines += event.unicode

        screen.fill((0, 0, 0))
        if is_valid:
            text = font.render("Enter Number of Mines (10-20): " + mines, False, (255, 255, 255))
        else:
            text = font.render("Enter Number of Mines (10-20): " + mines + " | Enter a Valid Value", False, (255, 255, 255))
        screen.blit(text, ((board_size + label_size) * board_scale // 2 - text.get_width() // 2, (board_size + label_size) * board_scale // 2 - text.get_height() // 2))
        pygame.display.flip()
    return m

def MainGameplay():
    win = False
    running = True
    while running:
        # checks for events such as clicks
        for event in pygame.event.get():
            # ends program if user clicks X
            if event.type == pygame.QUIT:
                # Added 9/28/2026 (Andrew Kruckemyer): close the window right away
                pygame.quit()
                sys.exit()

            # Added 9/28/2026 (Andrew Kruckemyer): R restarts with
            # the same mine count, Esc goes back to the start screen. The special return
            # values are handled by the main loop at the bottom of the file.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                if event.key == pygame.K_ESCAPE:
                    return "menu"

            if event.type == pygame.MOUSEBUTTONDOWN:
                # get mouse position
                pos = pygame.mouse.get_pos()
                # find board square that was clicked
                col = (pos[0] - label_size * board_scale) // (square_size * board_scale) #adjustments for pixels
                row = (pos[1] - label_size * board_scale) // (square_size * board_scale) #adjustments for pixels
                # Changed 9/28/2026 (Andrew Kruckemyer, with help from Claude): also ignore
                # clicks past the last row/column, since the hint bar sits below the board
                if col < 0 or row < 0 or row > 9 or col > 9:
                    continue
                #col = pos[0] // (square_size * board_scale)
                #row = pos[1] // (square_size * board_scale)
                if event.button == 1: # left click
                    if board.is_constructed == False:
                        board.createBoard(row,col)
                    #eliza m added this section
                    # Ryan G. modified this.
                    match board.dig(row, col):
                        case 0:
                            running=False #HAHA LOZER
                        case 2:
                            if board.chord(row, col) == 0:
                                running = False

                    if board.status()==True:
                        win = True
                        running=False #won game!!!
                    #elif board.dig(row,col)==2:
                    #    pass
                    #elif board.dig(row,col)==1:
                        #
                    #print(f"left click : {row}, {col}")
                if event.button == 3: # right click
                    board.flag(row, col) #eliza m added this line
                    #print(f"right click : {row}, {col}")

        # display and update board
        showBoard(screen)
        pygame.display.flip()
    return win

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


# Loop to run the game
# Changed 9/28/2026 (Andrew Kruckemyer, with help from Claude): mines is remembered between
# games so R can restart with the same count. None means "show the setup screen".
mines = None
while True:
    if mines is None:
        mines = DoSetup()
    board = Minesweeper(mines)
    win = MainGameplay()
    if win == "restart":
        continue  # new board, same mine count
    if win == "menu":
        mines = None  # back to the setup screen
        continue
    if not EndScreen(win):
        break
    mines = None  # after the end screen, Enter still goes to setup like before