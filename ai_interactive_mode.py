from ai_solver_easy import easy_mode
from difficulty_presets import BEGINNER
from difficulty_presets import INTERMEDIATE
from difficulty_presets import EXPERT


def possibleTile(external, difficulty):
    match difficulty:
        case 1:
            easy_mode(external, BEGINNER.rows, BEGINNER.columns)
        case 2:
            pass
        case 3:
            pass

def interactiveMode(external, difficultly):
    pass