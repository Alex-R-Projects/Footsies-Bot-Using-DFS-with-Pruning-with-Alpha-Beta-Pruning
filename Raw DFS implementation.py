import csv
import time
import matplotlib.pyplot as plt
from pynput.keyboard import Key, Controller, Listener as KeyboardListener
import win32com.client
import subprocess

# Initialize the keyboard controller
keyboard = Controller()

# Key mappings for keyboard input simulation
KEY_MAPPING = {
    "a": "a",         # Move left
    "d": "d",         # Move right
    "space": Key.space  # Attack
}

# Move definitions (no evaluation or additional metadata)
MOVES = [
    "neutral_attack",
    "forward_attack",
    "backward_attack",
    "move_left",
    "move_right",
    "hold_attack_release",
    "hold_attack_direction_release"
]

# Global flags and constants
game_starting = False
KEYPRESS_DURATION = 0.1  # Duration for which keys are held down (in seconds)
ACTION_COOLDOWN = 0.2  # Minimum cooldown between actions (in seconds)

# Metrics tracking
metrics = {
    "depths_explored": [],
    "computation_times": [],
    "actions_per_second": []
}

# Function to focus the game window
def focus_game_window():
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.AppActivate("FOOTSIES")  # Replace with your game's window title
        print("Game window focused.")
    except Exception as e:
        print(f"Failed to focus game window: {e}")

# Function to launch the game
def launch_game():
    try:
        game_process = subprocess.Popen(r"C:\Users\mrale\OneDrive\Desktop\FOOTSIES_v1_5_0\FOOTSIES.exe", shell=True)
        if game_process is None:
            raise ValueError("Failed to start the game process.")
        print("Game launched.")
        return game_process
    except Exception as e:
        print(f"Error launching the game: {e}")
        return None

# Function to perform actions
def perform_action(action):
    focus_game_window()
    if action == 'neutral_attack':
        keyboard.press(KEY_MAPPING["space"])
        time.sleep(KEYPRESS_DURATION)
        keyboard.release(KEY_MAPPING["space"])
    elif action == 'forward_attack':
        keyboard.press(KEY_MAPPING["d"])
        keyboard.press(KEY_MAPPING["space"])
        time.sleep(KEYPRESS_DURATION)
        keyboard.release(KEY_MAPPING["space"])
        keyboard.release(KEY_MAPPING["d"])
    elif action == 'backward_attack':
        keyboard.press(KEY_MAPPING["a"])
        keyboard.press(KEY_MAPPING["space"])
        time.sleep(KEYPRESS_DURATION)
        keyboard.release(KEY_MAPPING["space"])
        keyboard.release(KEY_MAPPING["a"])
    elif action == 'move_left':
        keyboard.press(KEY_MAPPING["a"])
        time.sleep(KEYPRESS_DURATION)
        keyboard.release(KEY_MAPPING["a"])
    elif action == 'move_right':
        keyboard.press(KEY_MAPPING["d"])
        time.sleep(KEYPRESS_DURATION)
        keyboard.release(KEY_MAPPING["d"])
    elif action == 'hold_attack_release':
        keyboard.press(KEY_MAPPING["space"])
        time.sleep(1)  # Hold for a longer duration
        keyboard.release(KEY_MAPPING["space"])
    elif action == 'hold_attack_direction_release':
        keyboard.press(KEY_MAPPING["d"])
        keyboard.press(KEY_MAPPING["space"])
        time.sleep(1)
        keyboard.release(KEY_MAPPING["space"])
        keyboard.release(KEY_MAPPING["d"])
    print(f"Performed action: {action}")

# DFS implementation to iterate through moves
def dfs_moves(moves, depth, current_path=[], current_depth=0):
    start_time = time.time()

    if depth == 0:
        # Reached the maximum depth; perform the action corresponding to the current move
        move_to_perform = current_path[-1]
        perform_action(move_to_perform)
        metrics["depths_explored"].append(current_depth)
        metrics["computation_times"].append(time.time() - start_time)
        return

    for move in moves:
        dfs_moves(moves, depth - 1, current_path + [move], current_depth + 1)

# Function to compute actions per second
def compute_actions_per_second():
    total_actions = len(metrics["depths_explored"])
    total_time = sum(metrics["computation_times"])
    return total_actions / total_time if total_time > 0 else 0

# Function to save and display the graph
def save_graph():
    """
    Save the performance metrics graph to a specific file path.
    """
    save_path = r"C:\Users\mrale\OneDrive\Desktop\dfs_performance_metrics.png"
    plt.figure(figsize=(10, 6))
    plt.plot(metrics["depths_explored"], label="Depths Explored")
    plt.plot(metrics["computation_times"], label="Computation Time (s)")
    plt.xlabel("Action Count")
    plt.ylabel("Metric Value")
    plt.title("Raw DFS Performance Metrics")
    plt.legend()
    plt.savefig(save_path)
    plt.show()
    print(f"Graph saved as '{save_path}'.")


# Start game on Enter key press
def on_key_press(key):
    global game_starting
    if key == Key.enter:
        game_starting = True
        print("Game starting...")
        return False

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

    # Initialize metrics
    depths_explored = []
    actions_per_second = []
    computation_times = []

    try:
        while True:
            # Check if the game process is still running
            if game_process.poll() is not None:
                print("Game has exited. Shutting down the bot...")
                break

            print("Starting DFS on moves...")

            # Start measuring metrics
            start_time = time.time()
            dfs_moves(MOVES, depth=3)  # Start DFS with the moves list and a depth of 3
            end_time = time.time()

            # Collect metrics for this DFS run
            depths_explored.append(3)  # Fixed depth for this implementation
            actions_per_second.append(len(MOVES) / (end_time - start_time))
            computation_times.append(end_time - start_time)

            time.sleep(1)  # Wait a bit before restarting DFS

    except KeyboardInterrupt:
        print("Exiting due to user interruption.")
    finally:

            # Ensure the game process is terminated
        if game_process.poll() is None:
            game_process.terminate()

    # Save metrics graph
        print("Saving performance metrics graph...")
        save_graph()

        print("Bot terminated.")




if __name__ == "__main__":
    main()
