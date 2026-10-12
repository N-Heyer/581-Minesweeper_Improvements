# Bug Report - minesweeper board and AI solver

**Owner:** Khang Phan
**Audit date:** 10/10/2026
**Method:** 83 automated test cases written with pytest

---

## 1. [BUG] getMovesForAutoSolve() only expects a 2-tuple

getMovesForAutoSolve saves the sequence of moves that the AI solver takes to solve a board. It expects only a 2-tuple (row, col) when it digs, causing an error for the medium and hard level AI solvers. Medium and hard return a 3-tuple ("dig"/"flag", row, col), while easy returns a 2-tuple (row, col).

Proposed Solution: Change easy_mode() to return a 3-tuple, change getMovesForAutoSolve(), medium_mode(), and hard_mode() accordingly to handle 3-tuples. 

## 2. [POSSIBLE IMPROVEMENT] simple 1-2-1 rule

find_121_move() will reject any cases where there are more than 3 hidden neighbors, even if those neighbors are irrelevant to the rule. Using the following table as an example, if N1, N2, N3, N10, N11, and N12 are not revealed, find_121_move() fails to find the move according to the 1-2-1 rule (N5,N9 are mines). The R neighbors should be the only ones required in the 1-2-1 rule.

|Col1|Col2|Col3|
|:--:|:--:|:--:|
| N1 | N2 | N3 |
| R  |  1 | N5 |
| R  |  2 | N7 |
| R  |  1 | N9 |
|N10 |N11 |N12 |

Proposed Solution: Only check for hidden neighbors on either side of the 1-2-1 pattern. 