import os
from clock_in_out import run_clock_in_out

# ANSI Escape Codes for colors
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
LIGHT_BLUE = "\033[94m"
RESET_COLOR = "\033[0m"

def display_navigation(message=""):
    """
    Display the main navigation for the Time-et-al system.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(message)
    print(LIGHT_BLUE + "\nMain Loader" + RESET_COLOR)
    print(LIGHT_BLUE + "----------------------\n" + RESET_COLOR)
    print("1. Clock In/Out")
    print("2. Job Tracking")
    print("3. Exit")
    choice = input("\nEnter your choice (1/2/3): ")
    return choice

def main():
    """
    Main function to run the Time-et-al system.
    """
    message = ""  # Initialize the message
    while True:
        choice = display_navigation(message)
        if choice == "1":
            message = run_clock_in_out()
        elif choice == "2":
            # TODO: Implement job tracking here
            message = LIGHT_RED + "ERROR: Job Tracking not yet implemented." + RESET_COLOR
        elif choice == "3":
            break
        else:
            message = LIGHT_RED + "ERROR: Invalid choice. Please select again." + RESET_COLOR

if __name__ == "__main__":
    main()
