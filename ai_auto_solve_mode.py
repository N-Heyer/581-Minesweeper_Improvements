# Prologue Comment
# File: ai_auto_solve_mode.py
# Description: Auto-solve mode. Lets the AI play the board out on its own, one
#              move at a time, and keeps the moves it played in a queue so the
#              caller can step through or replay them. Holds the Node and Queue
#              classes that queue is built from.
# Inputs:  the board being played, aiSkill (1-3), the difficulty object the game
#          was built with.
# Outputs: the head Node of a queue of (row, column) moves, or None when the AI
#          had no moves. Raises ValueError on an AI level outside 1-3.
# External sources: Claude (Anthropic) was used for bug finding, and under my
# direction fixed enqueue adding the first move twice and changed this file to
# dig as it goes instead of working every move out up front.
# Author: Jaycob Campos
# Created: Sept 29 2026

from ai_interactive_mode import getAiMoveInteractive

# one link in the Queue below - the move it holds, and the link after it
class Node:
    # input:  value - the (row, column) move this node holds
    # output: none
    # fields: value = the move, next = the next Node, or None at the tail
    def __init__(self, value):
        self.value = value
        self.next = None

# a first in, first out queue of moves, built out of Nodes
class Queue:
    # input:  none
    # output: none
    # fields: head = the first Node in the queue, or None while it is empty
    def __init__(self):
        self.head = None

    # Adds a move to the back of the queue, walking from the head to find the
    # tail. Starts the queue off when it is still empty.
    # input:  value - the (row, column) move to add
    # output: none
    def enqueue(self, value):

        if self.head is None:
            self.head = Node(value)

        elif self.head is not None:
            jumper = self.head

            while jumper.next is not None:
                jumper = jumper.next

            jumper.next = Node(value)


# Plays the board out, asking the AI for one move at a time so every move is
# chosen from the board as it stands. Working the whole run out up front cannot
# work past the easy AI, because each move after the first depends on the numbers
# the earlier ones uncovered.
# input:  board - the Minesweeper board to play; aiSkill - which AI to use, 1-3;
#         gameDifficultyObject - a preset exposing rows and columns
# output: the head Node of a queue of the (row, column) moves played, or None if
#         the AI had no moves; raises ValueError if aiSkill is not 1, 2, or 3
def getMovesForAutoSolve(board, aiSkill, gameDifficultyObject):
    queue = Queue()

    while board.state() == "Playing":
        move = getAiMoveInteractive(board.getPlayerView(), aiSkill, gameDifficultyObject)

        if move is None:
            break

        queue.enqueue(move)

        if board.dig(move[0], move[1]) == 2:
            break

    return queue.head
