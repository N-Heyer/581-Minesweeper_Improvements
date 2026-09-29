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
