# 581-Project-1: Minesweeper

A single-player Minesweeper game built in Python with **pygame** for **EECS 581** at the **University of Kansas**.

The player uncovers cells on a 10×10 grid, using the numbers to figure out where the mines are, and flags cells they think hide a mine. **Uncover every safe cell to win. Uncover a mine and you lose.**

---

## Table of Contents

- [Teams](#teams)
- [Requirements](#requirements)
- [How to Run](#how-to-run)
- [How to Play](#how-to-play)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Testing](#testing)
- [Sources and Attribution](#sources-and-attribution)

---

## Teams

### Original Project Team

| Name | Role |
|---|---|
| Zachary McCauley | Game Logic |
| Emilia Davis | User Interface / Board Display |
| Eliza Malyshev | Meeting Documentation and Input Processing |
| Daniel Harris | Passing Input Between UI and Game Logic |
| Adira Mongar | Project Manager and Jira Organizer |
| Ryan Graham | Assistance and Integration |
| Jett Viduya | Testing and README |

### Project Maintenance Team

|Name | Role |
| --- | --- |
| Jaycob Campos | Backend / Project Manager |
| Lydia Peng | Backend |
| Khang Phan | QA / Test |
| Jonathan Kazmaier | QA / Test |
| Andrew Kruckemyer | User Interface |
| Nick Heyer | User Interface |

---

## Requirements

- **Python 3.10 or newer** (the code uses `match` statements)
- **pygame-ce**

Install pygame-ce:

```bash
pip install pygame-ce
```

> On Windows, if `pip` isn't recognized, use `py -m pip install pygame-ce`.

---

## How to Run

1. Download or clone this repository.
2. Open a terminal **inside the project folder** (the one containing `ui_display.py` and `SpriteSheet.png`).
3. Run:

```bash
python ui_display.py
```

> **Windows:** you can also use `py ui_display.py`.

> **Note:** Run the game from the project folder. Launching it from a different folder (including VS Code's Run button when a parent folder is open) currently crashes with `FileNotFoundError: SpriteSheet.png`.

---

## How to Play

| Action | Control |
|---|---|
| Uncover a cell | **Left-click** |
| Place / remove a flag | **Right-click** |
| Chord (open all neighbors of a number whose flags are all placed) | **Left-click** an uncovered number |
| Restart on the current difficulty | **R** |
| Back to menu | **Esc** |
| Quit | Close the window |

**Rules**

- Your **first click is always safe**, because mines are placed after it.
- A number shows how many of the **8 surrounding cells** contain mines.
- Opening a cell with no nearby mines **automatically opens the area around it**.
- Flagged cells **can't be uncovered** until the flag is removed.
- Columns are labeled **A–J** and rows **1–10**.

**AI Solver**

- Easy, medium, and hard level AIs can be chosen. The user will also choose either interactive mode or auto-solve mode.
- Easy: Cells are uncovered by the AI at random.
- Medium: Reveals all neighbors of a cell if the number of adjacent flags is equal to that cell's count. Flags all neighbors of a cell if the number of uncovered neighbors is equal to that cell's count. Default to revealing random cell otherwise.
- Hard: Same rules as medium, along with 1-2-1 pattern rule. If three side-by-side revealed cells show “1-2-1,” the AI can logically deduce that the two outer hidden neighbors are mines (and should be flagged), while the inner hidden neighbor is safe (and should be opened). Default to revealing a random cell otherwise.
- Interactive mode: The AI will take turns alternating with the player until the game is either won or lost.
- Auto-solve mode: The AI will automatically play through an entire game by itself until it wins or loses.

---

## Project Structure

```
581-Project-1/
├── ui_display.py               # pygame window, drawing and mouse input (run this file)
├── minesweeper.py              # Game logic: the Minesweeper class
├── SpriteSheet.png             # Cell, flag, mine and number sprites
├── tests                       # Automated tests
├── ai_auto_solve_mode.py       # AI auto-solve mode: AI plays an entire board
├── ai_interactive_mode.py      # AI interactive mode: take turns with player 
├── ai_solver_easy.py           # Easy-level AI configuration
├── ai_solver_medium.py         # Medium-level AI configuration
├── ai_solver_hard.py           # Hard-level AI configuration
└── difficulty_presets.py       # Difficulty presets for board size and mine count
```

---

## How It Works

| Component | File | What it does |
|---|---|---|
| **Board / Game Logic** | `minesweeper.py` | Stores two 10×10 grids: a hidden one with the mines and adjacent-mine counts, and a visible one tracking covered, uncovered and flagged cells. Handles mine placement, digging, flood-fill, flagging, chording and the win check. |
| **AI Solver** | `ai_auto_solve_mode.py`, `ai_interaactive_mode.py` | An AI Solver can take turns with the player making moves or attempt to solve an entire board by itself. Moves are decided by the level set, from easy/medium/hard. |
| **User Interface** | `ui_display.py` | Every frame, asks the game what each cell should look like and draws the matching sprite, plus the A–J / 1–10 labels. |
| **Input Handler** | `ui_display.py` | Converts a mouse click's pixel position into a row and column, then calls `dig()` for a left-click or `flag()` for a right-click. |

**Data flow:**

```
Mouse click → converted to row/column → Game Logic updates the board → UI redraws the board
```

## Testing

Automated tests through Pytest can be found in the tests folder. For the backend, tests include the minesweeper board (configuration, flood-fill, chording, etc.), AI solver (easy/medium/hard, interactive, auto-solve), and difficulty presets.

---

## Sources and Attribution

- [pygame-ce documentation](https://pyga.me/docs/)
- Parts of this README and the test report were drafted with help from Claude (Anthropic AI assistant) and reviewed by the team.
- Each source file lists any additional sources in its prologue comment.
