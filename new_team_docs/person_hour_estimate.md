# Person-Hours Estimate & Methodology

## Estimation Method

We estimated effort using story points, assigned during sprint planning through team estimation. Each task on our GitHub project board was sized on a modified Fibonacci scale (1, 2, 3, 5, 8), where the numbers reflect relative effort and complexity. The group that owned each task set its points.

We chose story points over direct hour estimates because relative sizing made more sense for a team without prior velocity data. Judging a task by its complexity also lets the team break it into smaller tasks when necessary.

## Converting Points to Hours

To produce an hour estimate for planning, we mapped story points to hours at a conversion rate of **1.5 hours per point**.

| Difficulty scale | Story points | Interpretation                 |
|------------------|--------------|--------------------------------|
| Trivial          | 1            | done in one sitting            |
| Small            | 2–3          | a normal, well-understood task |
| Medium           | 5            | real logic with edge cases     |
| Large            | 8            | many moving parts              |

## Estimated Totals


| Area                    | Story points | Est. hours |
|-------------------------|--------------|------------|
| Backend logic           | 5            | 7.5        |
| UI and user events      | 5            | 7.5        |
| Integration / QA / docs | 2            | 3.0        |
| **Total**               | **12**       | **18.0**   |

Hours are story points × 1.5. Backend and UI were sized as medium (5). Integration / QA / docs was sized as small (2).

## Actual vs Estimate

Actuals are the entries in `person_hours_log.md` through 10/10/2026, sorted into the three areas
above.

| Area                    | Est. hours | Actual hours | Variance |
|-------------------------|------------|--------------|----------|
| Backend logic           | 7.5        | 5.0          | −2.5     |
| UI and user events      | 7.5        | 7.5          | 0.0      |
| Integration / QA / docs | 3.0        | 9.5          | +6.5     |
| **Total**               | **18.0**   | **22.0**     | **+4.0** |

How the log maps onto each area:

- **Backend logic** — back-end debugging (2.0) and the medium and hard AI solvers (3.0).
- **UI and user events** — R/Esc keys (1.5), the AI settings menu (2.0), board sizing and the
  user-specified mine count (4.0).
- **Integration / QA / docs** — the meeting log (0.5), this folder's documentation (3.0), and
  the pytest suite (6.0).

### Why the estimate missed

- **Integration / QA / docs was sized far too small.** It was given 2 points (3.0 hours) and
  took 9.5. The 83-case pytest suite alone was 6.0 hours and had no line in the estimate.
- **The AI solvers were never sized separately.** They were folded into "backend logic," which
  is why that area reads as under budget while the total went over.
- **Documentation was bundled with QA.** The two have different owners on this team and should
  be sized apart next sprint.

Totals are 22.0 hours against an 18.0-hour estimate: **22% over**.
