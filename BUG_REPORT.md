# Bug Report — `minesweeper.py`

**Owner:** Jaycob Campos
**Audit dates:** 2026-09-28 → 2026-09-29
**Method:** Automated stress testing of the `Minesweeper` class — ~3,200 randomized boards,
targeted probes of every public method with out-of-range, boundary, and repeated-call inputs, a
differential harness comparing the patched class against the inherited one, and a
160,000-operation fuzz of the full public API.

> Line numbers refer to the file as inherited, before any fix landed. They no longer match the
> current file.

Related findings are merged; the original IDs from the first audit pass are kept in parentheses
so the earlier notes still cross-reference.

---

## 1. Coordinate arguments are never validated (BE-1, BE-9)

`dig()`, `flag()`, `chord()`, and `display()` (lines 41, 61, 77, 124) index the grids directly,
so Python's negative indexing silently addresses the opposite edge of the board:

```
dig(-1, 0)     -> 1   (dug row 9)
flag(0, -1)    -> 2
display(-1,-1) -> -2
```

`chord()` handles the same problem a third way: lines 90-95 and 104-113 catch `IndexError` for
`r > 9` / `c > 9` while skipping negatives with an explicit `continue`, and the guards are
asymmetric — the `r < 0` check sits *before* the `try` in the first loop and *inside* it in the
second. A genuine `IndexError` raised by a future bug would be swallowed there.

This was the only reachable crash in the inherited class.

**Fixed.** A `_checkBounds()` helper validates the pair at the top of `createBoard()`, `dig()`,
`flag()`, `chord()`, and `display()`, raising `IndexError` — an out-of-range coordinate is
caller misuse, not a move that legally did nothing, and the inherited code made those
indistinguishable. Both `chord()` sweeps now clamp with `max`/`min` the way `createBoard()` and
`dig()` already did, and the `try`/`except` blocks are gone.

*Verified:* all four methods raise on `(-1,0)`, `(0,-1)`, `(-1,-1)`, `(10,0)`, `(0,10)`,
`(10,10)`, `(99,99)`. The `chord()` rewrite was checked differentially against the inherited
class — 400 playthroughs on identical seeds and move sequences, 4,848 of them edge and corner
chords: 0 divergences in return values, board state, or rendered view.

---

## 2. The mine count is never validated, and a large one hangs forever (BE-2, BE-3)

`__init__` (lines 9-15) accepts anything:

- `Minesweeper(-5)` → `_digs = 5` with zero mines placed — nonsense state.
- `Minesweeper(0)` → `status()` returns `True` immediately, an instant win.

Worse, `createBoard()` (lines 21-32) places mines by rejection sampling with no bound on
attempts. The starting cell is excluded, leaving only 99 placeable cells, so any request for
100 or more mines spins forever. Confirmed: `Minesweeper(100)` and `Minesweeper(200)` never
return.

**Fixed.** `__init__` raises `ValueError` for anything outside 10–20 and for any non-`int`
(`bool` excluded explicitly), which also makes the unbounded loop unreachable. The loop itself
was left alone — there was no behavior worth preserving a rewrite for.

The type check closes a silent hole found by fuzzing: `Minesweeper(15.5)` was previously
*accepted*, producing `_digs = 84.5` and a board that could never be won, with no error raised
at all.

*Verified:* `0, -5, 9, 21, 100, 200, "15", None, [15], (15,), {…}, 15.5, nan, inf` all
rejected; `10, 15, 20` accepted; the bare `Minesweeper()` default still works.
`Minesweeper(100)` and `Minesweeper(200)` now return immediately under a 5-second `SIGALRM`.

---

## 3. `createBoard()` does not guard its own preconditions (BE-4, BE-18)

Two separate failures in one method.

**It is not idempotent.** There is no `is_constructed` guard, so a second call layers a fresh
set of mines onto the existing board while `_digs` keeps its old value:

```
mines after 1st call: 10   after 2nd call: 20
_digs: 89 -> 89            (should be 79)
```

With 20 mines there are only 80 safe cells, so `_digs` can never reach 0 — the game becomes
unwinnable.

**A flag placed before generation voids first-click safety.** `flag()` (lines 61-71) has no
`is_constructed` guard, so it marks cells on an empty board — and `createBoard()` ends by
calling `dig(s_row, s_col)` (line 34), which returns `2` and reveals nothing when that cell is
already flagged:

```
flag(3, 3)        -> 0    (accepted; is_constructed still False)
createBoard(3, 3) -> board generated, is_constructed = True
cells revealed    -> 0    (dig() bailed out on the flag)
```

The board goes live with nothing uncovered, so the *next* dig is an ordinary one on a fully
mined board with no protection. Reproduced: that call hit a mine and returned `0` — a loss on
what the player sees as their first click.

**Fixed.** `if self.is_constructed: return` after the bounds check, and a clear of
`(s_row, s_col)` — resetting `_external` and decrementing `flags` — before mines are placed.
Flagging before generation stays legal everywhere else, which is what players expect.

*Verified:* mine count stays at 10 and `_digs` is unchanged across three `createBoard()` calls.
Across 300 seeded boards, flag-then-dig-the-same-cell always clears the flag, reveals the start
cell, restores `flags` to 0, and never puts a mine under the first click; a flag on a
*different* cell correctly survives generation.

---

## 4. The class cannot express or act on a loss (BE-5, BE-6)

`status()` (line 148) is a boolean win check. After digging a mine it still returns `False` —
indistinguishable from a game in progress — so there is no way to ask the class what is
happening.

The public surface is also missing any way to uncover the mines: `chord, createBoard, dig,
display, flag, is_constructed, m, status`. Nothing exposes "reveal every mine," so a
reveal-on-loss cannot be built on top of this class at all.

**Fixed.** Added a `lost` flag set by `dig()` when a mine is uncovered, and a `state()` method
returning `"Playing"` / `"Game Over: Loss"` / `"Victory"`. Added `revealAllMines()`, which sets
`_external = 1` on every cell where `_internal == -1` and deliberately leaves `_digs` alone so
`status()` cannot report a win as a side effect.

`status()`'s return type is unchanged. It has to stay `bool`: the existing contract compares it
against `True`, and returning a string there would make that comparison `False` forever,
silently deleting the win condition. (An `IntEnum` tri-state with `VICTORY = 1` would also keep
`== True` working, since `1 == True` — deliberately not done; it breaks the moment someone
renumbers the members.) Both additions are purely additive, so no existing signature moved.

*Verified:* loss detected and sticky; `status()` still returns `False` on a loss rather than
lying; 200/200 perfect playthroughs report `"Victory"`; across 400 fuzzed games including
chord-triggered losses the `lost` flag matched board truth every time. `revealAllMines()`
uncovers every mine, leaves safe cells untouched, is idempotent, and is harmless if called
before `createBoard()`.

---

## 5. The flag count is not capped (BE-7, BE-16)

`flag()` (lines 61-71) increments `self.flags` without limit. Testing placed **21 flags on a
10-mine board**, so a `m - flags` remaining-mines figure reads `-11`. The comment on line 11
says the maximum "may be used later," which is no longer true.

**Fixed.** `flag()` returns `2` ("nothing happened") once `flags == m`, and a `remaining()`
accessor returns `max(0, m - flags)`. The stale comment now states the cap is enforced by
`flag()` and reported by `remaining()`.

*Verified:* on a 10-mine board only 10 of 99 covered cells accept a flag, `flags` tops out at
10, and `remaining()` never goes negative under 200 boards of random flag hammering. Unflagging
still works while at the cap.

---

## 6. Board size is hardcoded throughout (BE-12)

Lines 14-15, 22-23, 28-29 and 50-51 all use literal `10`/`9`, so the grid dimension is repeated
in eight places with no single source of truth.

**Fixed.** A `BOARD_SIZE` constant backs every size-dependent value — grid construction,
`_digs`, bounds validation, mine placement, and all four neighbor sweeps.

*Note:* this was briefly generalized further to a `(rows, columns)` tuple supporting
rectangular boards, then deliberately reverted. The board is specified as a fixed 10x10 grid,
so the generalization was out of scope.

---

## 7. Dead debug code left in the class (BE-11, BE-13)

`_printB()` (line 156) prints the solution board — a development aid that has no place in the
shipped class. `display()` carries five commented-out `print` calls on lines 127, 131, 134,
137 and 140.

**Fixed.** Both deleted. `_printB()` had zero callers anywhere in the repository, verified by
search, so removing it changed nothing; it remains in git history if it is ever wanted.

---

## 8. Prologue comment is incomplete (BE-10)

Lines 1-4 give only the filename and author. Missing: description, inputs, outputs, creation
date, and external sources.

**Fixed.** Rewritten to the team's Prologue Comment template — file, description, inputs,
outputs, external sources, author, and creation date (2026-09-13, from
`git log --diff-filter=A`).

---

## 9. Return codes are magic numbers, and `0/1/2` mean different things per method (BE-17)

`dig()` returns `0` for a loss, `flag()` returns `0` for *success*, and `chord()` returns `2`
for "nothing happened." Nothing in the signatures says so. `display()` (line 124) is the same
problem in another shape: `-3/-2/-1/0` are sprite-sheet offsets this class has no business
knowing about.

Related: `chord()`'s `if displayVal <= 0:` guard rejects covered / mine / zero / flag in a
single comparison that only works because of how those offsets happen to be numbered. Renumber
them and `<= 0` silently starts admitting cases it used to reject.

*Proposed fix:* give each method its own `IntEnum` — `DigResult`, `FlagResult`, `ChordResult`,
`CellView` — one type per method, so a `FlagResult` can never be compared against a
`DigResult` case. Two constraints, because the existing return values are a fixed contract:

- **`IntEnum`, not `Enum`, and the numeric values must not change.** Existing code does
  arithmetic on `display()`'s result, compares it against raw ints, and dispatches `dig()`
  through `match` with `case 0:` / `case 2:`. Literal patterns compare with `==`, so `IntEnum`
  members match; a plain `Enum` falls through *every* case and the game silently never ends —
  no traceback, just an unlosable board. Verified experimentally.
- `str()` on an `IntEnum` member yields `"3"` only on Python 3.11+. On 3.10 it would render
  `CellView.THREE` wherever a cell value is printed.

**Open.** This is a readability and contract change, not a crash fix.

---

## 10. Minor mine-placement and flood-fill imperfections (BE-14, BE-15)

Line 24 excludes only `(s_row, s_col)` from mine placement, not its neighbors, so the opening
dig can reveal a bare number instead of an open region. Most implementations guarantee a
zero-cell start; the specification makes the adjacent-cell guarantee optional.

Lines 50-52 include `(row, col)` itself in the flood fill's neighbor sweep. The recursive call
returns `2` immediately, so it is a harmless no-op, but the inner loop should skip its own
centre.

**Open.** Neither is a crash and neither is required.

---

## Withdrawn — filed in error

**Flagging a safe cell makes the game unwinnable (BE-8).** The first pass recorded that because
`dig()` returns early on any non-zero `_external` (line 42), the flood fill skips flagged cells,
`_digs` is never decremented for them, and the game becomes unwinnable.

**The claim is wrong, and no fix is needed.** The board is not unwinnable — it is merely
un-*won* until the player unflags the cell and digs it. Tested across 200 boards: every one that
failed to win with a safe cell flagged **won after unflagging and digging that cell**. Zero
permanently unwinnable.

A win means uncovering all non-mine cells. A flagged safe cell is not uncovered, so refusing to
declare victory is correct behavior. The fix originally proposed — deriving the win from "every
safe cell uncovered **or flagged**" — would have declared victory while a non-mine cell was
still covered, and was not applied.
