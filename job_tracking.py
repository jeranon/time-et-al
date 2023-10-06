import os

# ANSI Escape Codes for colors
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
LIGHT_BLUE = "\033[94m"
BUTTER_YELLOW = "\033[38;5;221m"
LIGHT_PURPLE = "\033[38;5;141m"
RESET_COLOR = "\033[0m"

if __name__ == "__main__":
    os.system('')
    print(LIGHT_RED + "ERROR: This script cannot be run directly. Please run through main_loader.py. Press Enter to exit..." + RESET_COLOR)
    input("")