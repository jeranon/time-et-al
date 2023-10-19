import os
from utilities import onboard, offboard
from shift_editor import manage_shifts  # Importing the function

# ANSI Escape Codes for colors
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
LIGHT_BLUE = "\033[94m"
RESET_COLOR = "\033[0m"

def display_navigation(message=""):
    """
    Display the main administrative menu for the Time-et-al system.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(message)
    print(LIGHT_BLUE + "\nAdmin Menu" + RESET_COLOR)
    print(LIGHT_BLUE + "----------------------\n" + RESET_COLOR)
    print("1. Onboard Employee")
    print("2. Offboard Employee")
    print("3. Edit Shifts")  # New Option
    print("4. Exit")
    choice = input("\nEnter your choice (1/2/3/4): ")
    return choice

def main():
    """
    Main function to run the administrative tasks of the Time-et-al system.
    """
    message = ""  # Initialize the message
    while True:
        choice = display_navigation(message)
        if choice == "1":
            message = onboard.run_onboard()  # Assuming onboard.py has a function called run_onboard
        elif choice == "2":
            message = offboard.run_offboard()  # Assuming offboard.py has a function called run_offboard
        elif choice == "3":
            manage_shifts()  # Run the shift management function
            message = LIGHT_GREEN + "Shifts edited successfully." + RESET_COLOR
        elif choice == "4":
            break
        else:
            message = LIGHT_RED + "ERROR: Invalid choice. Please select again." + RESET_COLOR

if __name__ == "__main__":
    main()
