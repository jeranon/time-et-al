import os
import json

# ANSI Escape Codes for colors
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
LIGHT_BLUE = "\033[94m"
RESET_COLOR = "\033[0m"

SHIFT_FILE_PATH = os.path.join("data", "reference", "shifts.json")

def load_shifts():
    if os.path.exists(SHIFT_FILE_PATH):
        with open(SHIFT_FILE_PATH, 'r') as file:
            return json.load(file)
    else:
        with open(SHIFT_FILE_PATH, 'w') as file:
            json.dump({}, file)
        return {}

def save_shifts(shifts):
    with open(SHIFT_FILE_PATH, 'w') as file:
        json.dump(shifts, file, indent=4)

def list_shifts():
    shifts = load_shifts()
    print("\nCurrent Shifts:")
    for shift_name, timings in shifts.items():
        print(f"- {shift_name}: {timings['start']} to {timings['end']}")

def add_shift(shift_name, start_time, end_time):
    shifts = load_shifts()
    shifts[shift_name] = {
        "start": start_time,
        "end": end_time
    }
    save_shifts(shifts)
    return LIGHT_GREEN + f"Shift '{shift_name}' added successfully!" + RESET_COLOR

def edit_shift(shift_name, new_start_time, new_end_time):
    shifts = load_shifts()
    if shift_name not in shifts:
        return LIGHT_RED + f"Shift '{shift_name}' not found!" + RESET_COLOR
    shifts[shift_name] = {
        "start": new_start_time if new_start_time else shifts[shift_name]['start'],
        "end": new_end_time if new_end_time else shifts[shift_name]['end']
    }
    save_shifts(shifts)
    return LIGHT_GREEN + f"Shift '{shift_name}' updated successfully!" + RESET_COLOR

def delete_shift(shift_name):
    shifts = load_shifts()
    if shift_name not in shifts:
        return LIGHT_RED + f"Shift '{shift_name}' not found!" + RESET_COLOR
    del shifts[shift_name]
    save_shifts(shifts)
    return LIGHT_GREEN + f"Shift '{shift_name}' deleted successfully!" + RESET_COLOR

def manage_shifts():
    message = ""  # Initialize the message
    while True:
        display_message_and_prompt(message, "1. Add Shift\n2. Edit Shift\n3. Delete Shift\n4. List Shifts\n5. Exit\n\nEnter your choice (1/2/3/4/5): ")
        choice = input()
        
        if choice == "1":
            shift_name = input("Enter shift name: ")
            start_time = input("Enter start time (HH:MM format): ")
            end_time = input("Enter end time (HH:MM format): ")
            message = add_shift(shift_name, start_time, end_time)
        elif choice == "2":
            list_shifts()
            shift_name = input("\nEnter the name of the shift you want to edit: ")
            new_start_time = input("Enter new start time (HH:MM format, leave blank to keep the current value): ")
            new_end_time = input("Enter new end time (HH:MM format, leave blank to keep the current value): ")
            message = edit_shift(shift_name, new_start_time, new_end_time)
        elif choice == "3":
            list_shifts()
            shift_name = input("\nEnter the name of the shift you want to delete: ")
            message = delete_shift(shift_name)
        elif choice == "4":
            list_shifts()
            input("\nPress Enter to go back...")
        elif choice == "5":
            break
        else:
            message = LIGHT_RED + "ERROR: Invalid choice. Please select again." + RESET_COLOR

def display_message_and_prompt(message="", prompt=""):
    """
    Display a message and a prompt for the user.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(message)
    print(LIGHT_BLUE + "\nShift Editor" + RESET_COLOR)
    print(LIGHT_BLUE + "----------------------\n" + RESET_COLOR)
    if prompt:
        print(prompt)

if __name__ == "__main__":
    os.system('')
    print(LIGHT_RED + "ERROR: This script cannot be run directly. Please run through admin.py. Press Enter to exit..." + RESET_COLOR)
    input("")
