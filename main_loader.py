import os
import ctypes
import pyautogui
import threading
import time
from datetime import datetime
from scripts.clock_in_out import run_clock_in_out, set_current_time, periodic_status_update

# ANSI Escape Codes for colors
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
LIGHT_BLUE = "\033[94m"
RESET_COLOR = "\033[0m"

def update_time():
    while True:
        current_time = datetime.now().strftime("%H:%M")
        set_current_time(current_time)
        time.sleep(15)  # Update time every 15 seconds

def clear_screen():
    """
    Clear the console screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def display_navigation(message=""):
    """
    Display the main navigation for the Time-et-al system.
    """
    clear_screen()
    print(message)
    print(LIGHT_BLUE + "\nMain Loader" + RESET_COLOR)
    print(LIGHT_BLUE + "----------------------\n" + RESET_COLOR)
    print("1. Clock In/Out")
    print("0. Exit")
    choice = input("\nEnter your choice (1/0): ")
    return choice

def main():
    """
    Main function to run the Time-et-al system.
    """
    # Set console to full screen mode by simulating the F11 key press
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')

    hWnd = kernel32.GetConsoleWindow()
    user32.ShowWindow(hWnd, 3)  # Maximize the window first

    # Simulate F11 key press to toggle full-screen mode
    pyautogui.press('f11')

    # Start the time update thread
    threading.Thread(target=update_time, daemon=True).start()

    # Start the periodic status update thread
    threading.Thread(target=periodic_status_update, daemon=True).start()

    # Clear the screen before running the clock in/out function
    clear_screen()

    # Run the clock in/out function
    run_clock_in_out()

if __name__ == "__main__":
    main()
