import os
import threading
import time
from datetime import datetime

# ANSI Escape Codes for colors
LIGHT_BLUE = "\033[94m"
RESET_COLOR = "\033[0m"

clock_display = "Initializing clock..."

def update_clock():
    """
    Update the clock display every second.
    """
    global clock_display
    while True:
        now = datetime.now()
        clock_display = LIGHT_BLUE + now.strftime("%H:%M:%S") + RESET_COLOR
        print(f"Debug: Updating clock display to {clock_display}")  # Debugging clock update
        time.sleep(1)

def display_clock():
    """
    Display the clock in the console.
    """
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(clock_display)
        time.sleep(1)

if __name__ == "__main__":
    os.system('')  # Initialize ANSI escape codes on Windows
    print("Debug: Starting clock thread")  # Debugging thread start
    threading.Thread(target=update_clock, daemon=True).start()
    display_clock()
