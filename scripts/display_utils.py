# ANSI Escape Codes
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
LIGHT_BLUE = "\033[94m"
RESET_COLOR = "\033[0m"

import os

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored(message, color=RESET_COLOR):
    """Prints a message in a specified color."""
    message = message or ""
    color = color or RESET_COLOR
    print(color + message + RESET_COLOR, flush=True)

def display_header(title, message="", message_color=RESET_COLOR):
    """Displays a header with a reserved line for an optional message above the title."""
    clear_screen()
    if message:
        print_colored(message, message_color)
    else:
        print_colored("", RESET_COLOR)  # Reset color if no message
    print()  # Print a blank line
    print_colored(f"{title}\n" + "-" * len(title) + "\n", LIGHT_BLUE)

def display_menu(options):
    """Displays a menu with the given options."""
    for key, option in options.items():
        print(f"{key}. {option}")
