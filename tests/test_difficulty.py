"""
Prologue Comment
File: test_difficulty.py
Description: Tests difficulty_presets.py to ensure
             the working initialization and error
             checking
Inputs:  row count, column count, mine count
Outputs: Pytest results of each test case
External sources: Original code with assistance by OpenAI 
                  ChatGPT for correctness. Logic is reviewed
                  and tested by the author.
Author: Khang Phan
Created: [Oct 8 2026]
"""
import pytest

from difficulty_presets import Difficulty

@pytest.mark.parametrize("rows, columns, mines", [
    (10, 10, 1),
    (10, 10, 99),
    (10, 10, 10),
    (16, 16, 40),
    (16, 30, 99)
])
def test_difficulty_init(rows, columns, mines):
    diffObj = Difficulty(rows, columns, mines)
    assert diffObj.rows == rows
    assert diffObj.columns == columns
    assert diffObj.mines == mines

@pytest.mark.parametrize("rows, columns, mines", [
    (10, 10, -1),
    (10, 10, 0),
    (10, 10, 100),
    (16, 16, 256),
    (16, 30, 480)
])
def test_invalid_init(rows, columns, mines):
    with pytest.raises(ValueError):
        Difficulty(rows, columns, mines)