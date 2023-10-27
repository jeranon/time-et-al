import os
from utilities import onboard, offboard
from shift_editor import manage_shifts
import job_analysis  # Import the job_analysis module

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
    print("3. Edit Shifts")
    print("4. Job Analysis")  # New option for Job Analysis
    print("5. Exit")
    choice = input("\nEnter your choice (1/2/3/4/5): ")  # Adjusted input prompt
    return choice

def main():
    """
    Main function to run the administrative tasks of the Time-et-al system.
    """
    message = ""  # Initialize the message
    while True:
        choice = display_navigation(message)
        if choice == "1":
            message = onboard.run_onboard()  # Run the onboarding function
        elif choice == "2":
            message = offboard.run_offboard()  # Run the offboarding function
        elif choice == "3":
            message = manage_shifts()  # Run the shift management function
        elif choice == "4":  # New choice for Job Analysis
            message = job_analysis.main()  # Run the main function of job_analysis
        elif choice == "5":
            break
        else:
            message = LIGHT_RED + "ERROR: Invalid choice. Please select again." + RESET_COLOR

if __name__ == "__main__":
    main()
