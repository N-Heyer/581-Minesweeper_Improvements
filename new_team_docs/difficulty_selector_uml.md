# Difficulty Selector: UML Class Diagram (DRAFT)

Abstract view. Shows roles and relationships only; update after the selector is built.

```mermaid
classDiagram
    direction LR

    class UI["UI / Input"] {
        presents choice at setup
    }
    class DS["Difficulty Setting [PLANNED]"] {
        offers levels
        holds selected level
    }
    class GC["Game Configuration [PLANNED]"] {
        holds setup choices for one game
    }
    class AI["AI Solver [PLANNED]"] {
        proposes moves
    }
    class GE["Game Engine"] {
        owns board and game state
    }

    note for DS "Levels offered: Easy, Medium, Hard"

    UI --> DS : shows selection at setup
    DS --> GC : stores selected level
    AI ..> GC : reads level
    AI ..> GE : reads visible board state
    UI --> GE : starts a game
```

## Legend

- Solid arrow: the source uses or drives the target. Dotted arrow: the source only reads from the target.
- `[PLANNED]`: not built yet; update after implementation.
- Names match `architecture_overview.md`.
- Difficulty is shown only as a value that other components read; what it changes is not decided.
- If the selector becomes the custom feature, rename Difficulty Setting to Custom Feature in this diagram and in the architecture doc.
