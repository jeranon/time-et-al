import os
from scripts import onboard, offboard, job_analysis, display_utils
from scripts.shift_editor import manage_shifts

def display_navigation(message="", message_color=display_utils.RESET_COLOR):
    """
    Display the main administrative menu for the Time-et-al system.
    """
    message = message or ""
    message_color = message_color or display_utils.RESET_COLOR

    display_utils.display_header("Admin Menu", message, message_color)
    
    options = {
        "1": "Onboard Employee",
        "2": "Offboard Employee",
        "3": "Edit Shifts",
        "4": "Job Analysis",
        "5": "Exit"
    }
    display_utils.display_menu(options)
    choice = input("\nEnter your choice: ")
    return choice
    
def main():
    """
    Main function to run the administrative tasks of the Time-et-al system.
    """
    message = ""  # Initialize the message
    message_color = display_utils.RESET_COLOR  # Initialize the message color

    while True:
        choice = display_navigation(message, message_color)
        
        # Reset message and color for each iteration
        message = ""
        message_color = display_utils.RESET_COLOR

        if choice == "1":
            message, message_color = onboard.run_onboard()  # Run the onboarding function and get message and color
        elif choice == "2":
            message, message_color = offboard.run_offboard()  # Similar changes for other functions if they return color
        elif choice == "3":
            message, message_color = manage_shifts()  # Ensure this function also returns a color
        elif choice == "4":
            message, message_color = job_analysis.main()  # Ensure this function also returns a color
        elif choice == "5":
            break
        else:
            message = "ERROR: Invalid choice. Please select again."
            message_color = display_utils.LIGHT_RED

if __name__ == "__main__":
    main()
