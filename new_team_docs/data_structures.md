# Data Structures (Inherited Game Engine)

Source: `minesweeper.py`, class `Minesweeper`. Descriptions below are of the inherited code as it stands.
Grid dimensions are fixed-size and square (currently 10 × 10); all row/column loops derive from that size.

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

## Game state fields

| Field | Purpose |
|-------|---------|
| `m` | total mines |
| `flags` | flags currently placed |
| `_digs` | safe cells still to uncover; win when it reaches 0 |
| `is_constructed` | mines are placed only after the first click (first click is always safe) |

## Planned addition: difficulty

A difficulty value will be part of the game configuration, chosen at setup and fixed for the duration of a game. It is configuration, not board state: it does not alter the two grids. [PLANNED: update with the final name, type, and location once built.]

## State-changing operations and result codes

| Operation | Effect | Returns |
|-----------|--------|---------|
| `createBoard(r, c)` | places mines (excluding start cell), fills counts, then digs start cell | none |
| `dig(r, c)` | uncovers a cell; zero-cells flood-fill to neighbors | `0` hit a mine, `1` progress, `2` no change |
| `flag(r, c)` | toggles flag on a covered cell | `0` placed, `1` removed, `2` no change |
| `chord(r, c)` | uncovers neighbors of a number whose flag count matches | `0` lost, `1` progress, `2` no change |
| `status()` | win check | `True` if won |

## Where state lives

- All game state lives inside one `Minesweeper` instance, created per game.
- Restart and menu return create a new instance; nothing persists between games.
- The UI holds no game state beyond the instance and the setup choices reused for restart (currently the mine count; difficulty is planned to be included).

## Extension notes (keep this section generic)

- Any component that needs board information should go through the public operations above, not the underscore-prefixed grids, so internal changes do not propagate.
- New per-cell or per-game information should be listed in the tables above when added.
