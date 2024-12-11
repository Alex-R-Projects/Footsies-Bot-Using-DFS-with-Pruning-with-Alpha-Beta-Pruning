from pynput.keyboard import Key, Controller, Listener as KeyboardListener
import win32com.client
import subprocess
import random
import time

# Initialize the keyboard controller
keyboard = Controller()

# Key mappings for keyboard input simulation
KEY_MAPPING = {
    "a": "a",         # Move left
    "d": "d",         # Move right
    "space": Key.space  # Attack
}

# Frame data for moves with attributes affecting decision-making
FRAME_DATA = {
    "neutral_attack": {
        "state": "idle",
        "command": "Neutral + Attack",
        "startup": 5, 
        "active": 2, 
        "recovery": 16, 
        "can_cancel": True, 
        "KO": False
    },
    "forward_attack": {
        "state": "forward",
        "command": "Forward + Attack",
        "startup": 4,
        "active": 3,
        "recovery": 15,
        "can_cancel": True,
        "KO": False
    },
    "backward_attack": {
        "state": "backward",
        "command": "Backward + Attack",
        "startup": 6,
        "active": 2,
        "recovery": 20,
        "can_cancel": True,
        "KO": False
    },
    "hold_attack_release": {
        "command": "Hold Attack then Neutral + Release",
        "startup": 12,
        "active": 4,
        "recovery": 29,
        "can_cancel": False,
        "KO": True
    },
    "hold_attack_direction_release": {
        "command": "Hold Attack then Forward or Backward + Release",
        "startup": 3,
        "active": 6,
        "recovery": 47,
        "can_cancel": False,
        "KO": True
    }
}

# Global flags and constants
game_starting = False
KEYPRESS_DURATION = 0.1  # Duration for which keys are held down (in seconds)
ACTION_COOLDOWN = 0.2  # Minimum cooldown between actions (in seconds)
MOVEMENT_PRIORITY_INTERVAL = 1.5  # Time interval to ensure periodic movement (in seconds)

# Function to focus the game window
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

# Tree structure for decision-making using DFS
class TreeNode:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

# Function to create a decision tree for attacks
def create_tree_for_attack():
    root = TreeNode("Root")
    for move in FRAME_DATA.keys():
        action_node = TreeNode(move)
        for follow_up in FRAME_DATA.keys():
            action_node.add_child(TreeNode(follow_up))
        root.add_child(action_node)
    return root

# Function to evaluate moves
def evaluation_function(move_name, last_move, consecutive_moves):
    move_data = FRAME_DATA[move_name]
    score = (
        (20 / (move_data["startup"] + 1)) +
        (10 * move_data["active"]) -
        (move_data["recovery"] / 4)
    )
    if move_data["can_cancel"]:
        score += 25
    if move_data["KO"]:
        score += 30

    # Penalize consecutive repeated moves
    if move_name == last_move:
        penalty = 10 + (5 * consecutive_moves)
        score -= penalty

    # Add random variation
    score += random.uniform(0, 5)

    return score

# Depth-First Search (DFS) with Alpha-Beta Pruning
def dfs_with_pruning(node, depth, is_maximizing, alpha, beta, last_move, consecutive_moves):
    if not node.children:
        return evaluation_function(node.name, last_move, consecutive_moves), node

    best_node = None
    if is_maximizing:
        max_eval = float('-inf')
        for child in node.children:
            eval, _ = dfs_with_pruning(child, depth + 1, False, alpha, beta, last_move, consecutive_moves)
            if eval > max_eval:
                max_eval = eval
                best_node = child
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_node
    else:
        min_eval = float('inf')
        for child in node.children:
            eval, _ = dfs_with_pruning(child, depth + 1, True, alpha, beta, last_move, consecutive_moves)
            if eval < min_eval:
                min_eval = eval
                best_node = child
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_node

# Function to perform actions
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

# Start game on Enter key press
def on_key_press(key):
    global game_starting
    if key == Key.enter:
        game_starting = True
        print("Game starting...")
        return False

# Decision tree initialization
tree = create_tree_for_attack()

# Main loop
def main():
    global game_starting

    game_process = launch_game()
    if not game_process:
        print("Failed to launch the game. Exiting.")
        return

    print("Press Enter to start the bot...")
    with KeyboardListener(on_press=on_key_press) as listener:
        listener.join()

    last_action_time = 0
    last_move = None
    consecutive_moves = 0

    try:
        while True:
            if game_process.poll() is not None:
                print("Game has exited. Shutting down the bot...")
                break

            current_time = time.time()

            # Ensure periodic movement
            if current_time - last_action_time >= ACTION_COOLDOWN:
                optimize_value, best_node = dfs_with_pruning(
                    tree, depth=0, is_maximizing=True, alpha=float('-inf'), beta=float('inf'),
                    last_move=last_move, consecutive_moves=consecutive_moves
                )
                selected_move = best_node.name

                # Update consecutive move tracking
                if selected_move == last_move:
                    consecutive_moves += 1
                else:
                    consecutive_moves = 0

                perform_action(selected_move)
                last_move = selected_move
                last_action_time = current_time

    except KeyboardInterrupt:
        print("Exiting due to user interruption.")
    finally:
        if game_process.poll() is None:
            game_process.terminate()
        print("Bot terminated.")

if __name__ == "__main__":
    main()
