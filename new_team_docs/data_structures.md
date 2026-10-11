# Data Structures

Describes the code on the `backend-tests` branch (commit `3177710`). Sources:
`minesweeper.py` (class `Minesweeper`), `difficulty_presets.py` (class `Difficulty`), and
`ai_auto_solve_mode.py` (classes `Node` and `Queue`).

Grid dimensions come from the `Difficulty` object passed to the constructor, so they are not
fixed and need not be square. All row/column loops derive from `self.rows` and `self.columns`.

## Board: two parallel grids

Both are 2D lists indexed `[row][col]`, same dimensions, so one cell = the same index in each.

| Grid | Holds | Values |
|------|-------|--------|
| `_internal` (hidden truth) | Mine locations and neighbor counts | `-1` = mine; `0..8` = number of adjacent mines |
| `_external` (player-visible state) | What the player has done to each cell | `0` = covered; `1` = uncovered; `2` = flagged |

A "cell" is not an object. It is the pair (`_internal[r][c]`, `_external[r][c]`).

## Derived cell value: `display(row, col)`

The UI never reads the grids directly. `display` combines both grids into one code:

| Code | Meaning |
|------|---------|
| `-3` | covered |
| `0` | flagged |
| `-1` | uncovered mine |
| `-2` | uncovered, zero adjacent mines |
| `1..8` | uncovered, that many adjacent mines |

The UI uses the code (offset by 3) as a sprite index.

## Player view: `getPlayerView()`

A rows x columns grid of `display()` codes, built on demand. This is the only board data the AI
solvers ever receive — `_internal` is never passed out, so a solver cannot see mine positions it
has not deduced.

## Game state fields

| Field | Purpose |
|-------|---------|
| `rows`, `columns` | board dimensions, copied from the `Difficulty` object |
| `mines` | total mines (was `m` in Project 1) |
| `flags` | flags currently placed, capped at `mines` |
| `_digs` | safe cells still to uncover; win when it reaches 0 |
| `is_constructed` | mines are placed only on the first dig (first click is always safe) |
| `lost` | `True` once a mine has been uncovered; sticky for the rest of the game |
| `gameDifficultyObject` | the `Difficulty` this board was built from; held to pass to the AI |
| `aiLevel` | which solver this board's AI calls use, 1-3 |

## Configuration: `Difficulty`

`Difficulty(rows, columns, mineCount)` holds one board configuration and nothing else. It raises
`ValueError` unless `1 <= mineCount < rows * columns`. Fields `rows`, `columns`, and `mines` are
read directly by `Minesweeper.__init__`.

| Preset | Grid | Mines |
|--------|------|-------|
| `BEGINNER` | 10 x 10 | 10 |
| `INTERMEDIATE` | 16 x 16 | 40 |
| `EXPERT` | 16 x 30 | 99 |

Difficulty is configuration, not board state: it is chosen at setup and fixed for the game. It
does determine the size of the two grids, but nothing changes it once the board exists.

> The setup menu does not use these presets. It builds its own `Difficulty(size, size, mines)`
> from the board-size tabs (10x10 / 16x16 / 20x20) and the typed mine count, so the presets are
> currently used only by the test suite.

## Auto-solve move queue: `Node` and `Queue`

`ai_auto_solve_mode.py` records the moves the AI played in a singly linked FIFO queue.

| Class | Fields | Purpose |
|-------|--------|---------|
| `Node` | `value` = one `(action, row, column)` move; `next` = the following node, `None` at the tail | one link in the queue |
| `Queue` | `head` = the first `Node`, `None` while empty | the queue itself; `enqueue(value)` walks from the head to find the tail |

`autoSolve()` returns the head `Node`, or `None` if the AI had no moves, so a caller can step
through the run move by move.

## State-changing operations and result codes

| Operation | Effect | Returns |
|-----------|--------|---------|
| `createBoard(r, c)` | places mines, keeping `(r, c)` and its 8 neighbors clear, then digs `(r, c)` | the `dig` code for the start cell (`1`), or `2` if the board was already built |
| `dig(r, c)` | uncovers a cell; builds the board first if this is the first dig; zero-cells flood-fill outward | `0` hit a mine, `1` progress, `2` no change (already uncovered, or flagged) |
| `flag(r, c)` | toggles a flag on a covered cell | `0` placed, `1` removed, `2` no change (cell uncovered, or every flag already placed) |
| `clearAllFlags()` | takes every flag off the board and zeroes `flags` | how many flags were removed |
| `chord(r, c)` | uncovers covered neighbors of a number whose adjacent flag count matches it | `0` a dug neighbor was a mine, `1` chord went through, `2` refused |
| `revealAllMines()` | uncovers every mine, for drawing after a loss; leaves `_digs` alone | none |

## Read-only queries

| Operation | Returns |
|-----------|---------|
| `display(r, c)` | the cell's display code (table above) |
| `getPlayerView()` | the whole grid of display codes |
| `remaining()` | flags still to place, `max(0, mines - flags)`, never negative |
| `status()` | `True` once every safe cell is uncovered **and** no mine has been hit |
| `state()` | `"Game Over: Loss"`, `"Victory"`, or `"Playing"` — loss is checked first |
| `getAIMove()` | the solver's next `(action, row, column)`, or `None` |
| `autoSolve()` | head `Node` of the played-move queue, or `None` |

**Errors.** `_checkBounds()` raises `IndexError` for any coordinate off the board, from
`createBoard`, `dig`, `flag`, `chord`, and `display`. `__init__` raises `ValueError` if `aiLevel`
is not 1, 2, or 3. `createBoard` raises `ValueError` if the mines cannot fit outside the
protected first-click area.

**Notes on two easy-to-misread codes.**

- `dig` returning `2` does not distinguish "already uncovered" from "flagged", and `flag`
  returning `2` does not distinguish "cell uncovered" from "out of flags" — a caller that needs
  to tell those apart has to check `display()` or `remaining()` as well.
- `chord` returning `1` means the chord was allowed, not that a cell changed: a number whose
  neighbors are all already uncovered or flagged returns `1` having dug nothing.

## Where state lives

- All game state lives inside one `Minesweeper` instance, created per game.
- Restart and menu return create a new instance; nothing persists between games.
- The UI holds no game state beyond the instance, the `settings` tuple reused for restart
  (board size, mine count, game mode, AI level) and the `game_status` string it draws.
- The flood fill walks an explicit `toCheck` stack rather than recursing, so a large open region
  cannot overflow the call stack.

## Extension notes (keep this section generic)

- Any component that needs board information should go through the public operations above, not
  the underscore-prefixed grids, so internal changes do not propagate. The test suite is the one
  exception: `tests/test_helpers.py` writes `_internal` directly to build fixed boards.
- New per-cell or per-game information should be listed in the tables above when added.
