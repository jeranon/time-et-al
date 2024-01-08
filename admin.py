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
    while True:
        choice = display_navigation(message)
        
        # Add debug print here to show the message before running onboard
        print("Debug: message before onboard:", repr(message))
        
        if choice == "1":
            message = onboard.run_onboard()  # Run the onboarding function
        elif choice == "2":
            message = offboard.run_offboard()  # Run the offboarding function
        elif choice == "3":
            message = manage_shifts()  # Run the shift management function
        elif choice == "4":
            message = job_analysis.main()  # Run the job analysis function
        elif choice == "5":
            break
        else:
            # Correctly setting the message color for error
            message = "ERROR: Invalid choice. Please select again."
            display_navigation(message, display_utils.LIGHT_RED)

if __name__ == "__main__":
    main()
