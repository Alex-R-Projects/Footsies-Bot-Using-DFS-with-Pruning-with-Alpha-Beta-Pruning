from pynput.keyboard import Key, Controller, Listener as KeyboardListener 
import random
import win32com.client
import time
import subprocess

# Initialize the keyboard controller
keyboard = Controller()
# Key mappings
KEY_MAPPING = {
    "a": "a",         # Move left
    "d": "d",         # Move right
    "space": Key.space  # Attack
}

FRAME_DATA = {
        "neutral_attack": {
        "state": "idle",
        "command": "Neutral + Attack",
        "startup": 5,
        "active": 2,
        "recovery": 16,
        "can_cancel": True,  # Can cancel into another move
        "KO": False,
    },
        
        "move_left": {
        "state": "moving",
        "command": "Move Left",
        "startup": 0,
        "active": 0,
        "recovery": 0,
        "can_cancel": False,
        "KO": False,
    },
        
        "move_right": {
        "state": "moving",
        "command": "Move Right",
        "startup": 0,
        "active": 0,
        "recovery": 0,
        "can_cancel": False,
        "KO": False,
    },
        
        "forward_attack": {
        "state": "forward",
        "command": "Forward + Attack",
        "startup": 4,
        "active": 3,
        "recovery": 15,
        "can_cancel": True,  # Can cancel into another move
        "KO": False,
    },
        
        "backward_attack": {
        "state": "backward",
        "command": "Backward + Attack",
        "startup": 6,
        "active": 2,
        "recovery": 20,
        "can_cancel": True,  # Can cancel into another move
        "KO": False,
    },
}

game_starting = False
KEYPRESS_DURATION = 0.1  # Duration for which keys are held down (in seconds)
ACTION_COOLDOWN = 0.2  # Minimum cooldown between actions (in seconds)
MOVEMENT_PRIORITY_INTERVAL = 1.5  # Time interval to ensure periodic movement (in seconds)

def focus_game_window():
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.AppActivate("FOOTSIES")
        print("Game window focused.")
    except Exception as e:
        print(f"Failed to focus game window: {e}")

# Function to launch the game
def launch_game():
    try:
        game_process = subprocess.Popen(r"FOOTSIES_v1_5_0\FOOTSIES.exe", shell=True)
        if game_process is None:
            raise ValueError("Failed to start the game process.")
        print("Game launched.")
        return game_process
    except Exception as e:
        print(f"Error launching the game: {e}")
        return None
    
def perform_action(action):
    focus_game_window()
    if action == 'neutral_attack':
        keyboard.press(KEY_MAPPING["space"])
        time.sleep(KEYPRESS_DURATION)
        keyboard.release(KEY_MAPPING["space"])
        print("Performed neutral attack.")
    elif action == 'forward_attack':
        keyboard.press(KEY_MAPPING["d"])
        keyboard.press(KEY_MAPPING["space"])
        time.sleep(KEYPRESS_DURATION)
        keyboard.release(KEY_MAPPING["space"])
        keyboard.release(KEY_MAPPING["d"])
        print("Performed forward attack.")
    elif action == 'backward_attack':
        keyboard.press(KEY_MAPPING["a"])
        keyboard.press(KEY_MAPPING["space"])
        time.sleep(KEYPRESS_DURATION)
        keyboard.release(KEY_MAPPING["space"])
        keyboard.release(KEY_MAPPING["a"])
        print("Performed backward attack.")
    elif action == 'hold_attack_release':
        keyboard.press(KEY_MAPPING["space"])
        time.sleep(0.5)  # Simulate holding the attack
        keyboard.release(KEY_MAPPING["space"])
        print("Performed hold attack release.")
    elif action == 'hold_attack_direction_release':
        keyboard.press(KEY_MAPPING["d"])
        keyboard.press(KEY_MAPPING["space"])
        time.sleep(0.5)  # Simulate holding the attack
        keyboard.release(KEY_MAPPING["space"])
        keyboard.release(KEY_MAPPING["d"])
        print("Performed hold attack direction release.")
    else:
        print(f"Unknown action: {action}")

# Get possible moves based on the bot's movement state
def get_possible_moves(movement_state):
    if movement_state == 'idle':
        return ["neutral_attack", "move_left", "move_right"]
    return ["forward_attack", "backward_attack", "move_left", "move_right"]

def on_key_press(key):
    global game_starting
    if key == Key.enter:
        game_starting = True
        print("Game starting...")
        return False

def main():
    global game_starting

    game_process = launch_game()
    if not game_process:
        print("Failed to launch the game. Exiting.")
        return
    
    movement_state = 'idle'
    print("Press Enter to start the bot...")
    with KeyboardListener(on_press=on_key_press) as listener:
        listener.join()
    try:
        while True:
            if game_process.poll() is not None:
                print("Game has exited. Shutting down the bot...")
                break
            possible_moves = get_possible_moves(movement_state)
            # Randomize move selection
            selected_move = random.choice(possible_moves)
            # Perform the selected move
            perform_action(selected_move)
            # Update movement state for next iteration
            if selected_move in ["move_left", "move_right"]:
                movement_state = "moving"
            else:
                movement_state = "idle"
    except KeyboardInterrupt:
        print("Exiting due to user interruption.")
    finally:
        if game_process.poll() is None:
            game_process.terminate()
        print("Bot and game process terminated.")
        
if __name__ == "__main__":
    main()
