import os
from scripts import onboard, offboard, job_analysis, display_utils, reactivate, reprint_ID, edit_employee
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
        "3": "Reactivate Employee",
        "4": "Reprint ID Card",
        "5": "Edit Shifts",
        "6": "Edit Employee",
        "7": "Job Analysis",
        "\n0": "Exit"
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
            message, message_color = onboard.run_onboard()  # Run the onboarding function
        elif choice == "2":
            message, message_color = offboard.run_offboard()  # Run the offboarding function
        elif choice == "3":
            message, message_color = reactivate.run_reactivate()  # Run the reactivation function
        elif choice == "4":
            message, message_color = reprint_ID.run_reprint()  # Run the reprint ID function
        elif choice == "5":
            message, message_color = manage_shifts()  # Run the shift management function
        elif choice == "6":
            message, message_color = edit_employee.run_edit() #Run the edit employee function
        elif choice == "7":
            message, message_color = job_analysis.main()  # Run the job analysis function
        elif choice == "0":
            break  # Exit the loop to terminate the program
        else:
            message = "ERROR: Invalid choice. Please select again."
            message_color = display_utils.LIGHT_RED

if __name__ == "__main__":
    main()
