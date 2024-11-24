import subprocess # This library would be used to open the game FOOTSIES.exe
import time # This would be used to delay keyboard presses and wait for the game to launch
import keyboard # This library will allows the program to send keybaord inputs to the game
# We can use these two libraries to force the installation of the necessary libraries
import os
import sys


# Frame data for moves
FRAME_DATA = {
    "neutral_attack": { # this is the low kick attack, this can go into a KO attack
        "command": "Neutral + Attack",
        "startup": 5,
        "active": 2,
        "recovery": 16,
        "on_hit": -1,
        "on_block": -3,
        "on_guard_break": 18,
        "properties": "Can cancel into neutral special move by pressing attack on hit and on block",
        "KO": False # this means that this move ALONE won't KO the opponent
    },
    "forward_or_backward_attack": { # This is the knee attack, this can go into a KO attack
        "command": "Forward or Backward + Attack",
        "startup": 4,
        "active": 3,
        "recovery": 15,
        "on_hit": -1,
        "on_block": -3,
        "on_guard_break": 18,
        "properties": "Can cancel into neutral special move by pressing attack on hit and on block",
        "KO": False # this means that this move ALONE won't KO the opponent

    },
    "hold_attack_release": { # This is the high kick attack
        "command": "Hold Attack then Neutral + Release",
        "startup": 12,
        "active": 4,
        "recovery": 29,
        "on_hit": None,
        "on_block": -10,
        "on_guard_break": 3,
        "properties": None, 
        "KO": True # This move will KO the opponent
    },
    "hold_attack_direction_release": { # this is the uppercut-type move
        "command": "Hold Attack then Forward or Backward + Release",
        "startup": 3,
        "active": 6,
        "recovery": 47,
        "on_hit": None,
        "on_block": -30,
        "on_guard_break": -18,
        "properties": "1F-6F full invincibility", 
        "KO": True # this move will KO the opponent
    },
    "forward_x2": { # foward dash
        "command": "Forward x2",
        "startup": None,
        "active": None,
        "recovery": 16,
        "on_hit": None,
        "on_block": None,
        "on_guard_break": None,
        "properties": None
    },
    "backward_x2": { # back dash
        "command": "Backward x2",
        "startup": None,
        "active": None,
        "recovery": 22,
        "on_hit": None,
        "on_block": None,
        "on_guard_break": None,
        "properties": "1F-4F full invincibility"
    }
}

GAME_PATH = r"[GAME PATH GOES HERE]" # For this project I'm going to assume that the game is going on desktop

# Alex, should we have the game.exe in the folder directory?


def get_distance():
    pass

# Evaluation function: Scores the game state for Player 1.
def evaluate():
    pass
# Generate possible child states based on available moves
def get_children():
    pass

def decided_move():
    pass

# Alpha-beta pruning implementation
def alpha_beta(state, depth, alpha, beta, is_maximizing_player):
    if depth == 0 or abs(state[0] - state[1]) == 1:  # Terminal state or striking range
        return evaluate(state)

    if is_maximizing_player:
        max_eval = float('-inf')
        for child in get_children(state, True):
            eval = alpha_beta(child, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:  # Beta cutoff
                break
        return max_eval
    else:
        min_eval = float('inf')
        for child in get_children(state, False):
            eval = alpha_beta(child, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:  # Alpha cutoff
                break
        return min_eval


def main():
    # Launch the game
    try:
        process = subprocess.Popen(GAME_PATH, shell=True)
        print(f"Game launched with PID: {process.pid}")
    except FileNotFoundError:
        print("Error: game.exe not found!")
    except Exception as e:
        print(f"An error occurred: {e}")
            