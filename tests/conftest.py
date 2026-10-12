"""
Prologue Comment
File: conftest.py
Description: Gives pygame a dummy display so UI tests can import
             ui_display without opening a window.
Inputs:  none
Outputs: SDL video and audio drivers set before tests import pygame
External sources: None
Author: QA (frontend unit tests)
Created: [Oct 11 2026]
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
