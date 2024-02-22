import os
import json
from datetime import datetime

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

def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

def is_time_overlap(start_time, end_time):
    start = datetime.strptime(start_time, '%H:%M')
    end = datetime.strptime(end_time, '%H:%M')
    # Handle rollover to next day
    if start > end:
        return end.hour <= 4  # Assuming the end time should not exceed 04:59
    else:
        return start < end

def get_shift_times():
    times = {}
    common_days = input("Enter days with common times (e.g., M,T,W,Th,F): ").split(',')
    if common_days:
        common_start = input("Enter common start time (HH:MM): ")
        common_end = input("Enter common end time (HH:MM): ")
        if is_valid_time(common_start) and is_valid_time(common_end) and is_time_overlap(common_start, common_end):
            for day in common_days:
                times[day.strip()] = {"start": common_start, "end": common_end}
        else:
            print(LIGHT_RED + "Invalid time format or overlap." + RESET_COLOR)
            return {}

    individual_days = input("Enter days with individual times (leave blank if none): ").split(',')
    for day in individual_days:
        day = day.strip()
        if day and day not in times:
            start = input(f"Enter start time for {day} (HH:MM): ")
            end = input(f"Enter end time for {day} (HH:MM): ")
            if is_valid_time(start) and is_valid_time(end) and is_time_overlap(start, end):
                times[day] = {"start": start, "end": end}
            else:
                print(LIGHT_RED + "Invalid time format or overlap." + RESET_COLOR)
                return {}
    return times

def get_lunch_break():
    lunch_start = input("Enter lunch start time (HH:MM): ")
    lunch_end = input("Enter lunch end time (HH:MM): ")
    if is_valid_time(lunch_start) and is_valid_time(lunch_end) and is_time_overlap(lunch_start, lunch_end):
        return {"start": lunch_start, "end": lunch_end}
    else:
        print(LIGHT_RED + "Invalid lunch break time format or overlap." + RESET_COLOR)
        return None

def list_shifts(only_names=False):
    shifts = load_shifts()
    print("\nAvailable Shifts:")
    for shift_name in shifts.keys():
        print(f"- {shift_name}")
        if not only_names:
            shift_details = shifts[shift_name]
            for day, timings in shift_details['times'].items():
                print(f"  {day}: {timings['start']} to {timings['end']}")
            print(f"  Lunch: {shift_details['lunch']['start']} to {shift_details['lunch']['end']}")

def display_shift_details(shift_name):
    shifts = load_shifts()
    if shift_name not in shifts:
        return LIGHT_RED + f"Shift '{shift_name}' not found!" + RESET_COLOR
    print(f"\nDetails for shift '{shift_name}':")
    shift_details = shifts[shift_name]
    for day, timings in shift_details['times'].items():
        print(f"  {day}: {timings['start']} to {timings['end']}")
    print(f"  Lunch: {shift_details['lunch']['start']} to {shift_details['lunch']['end']}")

def add_shift():
    shift_name = input("Enter shift name: ")
    shift_times = get_shift_times()
    lunch_break = get_lunch_break()
    if shift_times and lunch_break:
        shifts = load_shifts()
        shifts[shift_name] = {"times": shift_times, "lunch": lunch_break}
        save_shifts(shifts)
        return LIGHT_GREEN + f"Shift '{shift_name}' added successfully!" + RESET_COLOR
    else:
        return LIGHT_RED + "Shift not added due to invalid input." + RESET_COLOR

def edit_shift(shift_name):
    if shift_name.lower() == 'exit':
        return "", RESET_COLOR

    shifts = load_shifts()
    if shift_name not in shifts:
        return LIGHT_RED + f"Shift '{shift_name}' not found!" + RESET_COLOR

    print("Editing shift times. Leave blank to keep current values.")
    shift_times = get_shift_times()
    lunch_break = get_lunch_break()

    if shift_times and lunch_break:
        shifts[shift_name] = {"times": shift_times, "lunch": lunch_break}
        save_shifts(shifts)
        return LIGHT_GREEN + f"Shift '{shift_name}' updated successfully!" + RESET_COLOR
    else:
        return LIGHT_RED + "Shift not updated due to invalid input." + RESET_COLOR

def delete_shift(shift_name):
    if shift_name.lower() == 'exit':
        return "", RESET_COLOR

    shifts = load_shifts()
    if shift_name not in shifts:
        return LIGHT_RED + f"Shift '{shift_name}' not found!" + RESET_COLOR
    del shifts[shift_name]
    save_shifts(shifts)
    return LIGHT_GREEN + f"Shift '{shift_name}' deleted successfully!" + RESET_COLOR

def prompt_for_shift_action(action):
    list_shifts()
    shift_name = input(f"\nEnter the name of the shift you want to {action}: (type 'exit' to return) ")
    if shift_name.lower() == 'exit':
        return None
    return shift_name

def manage_shifts():
    message = ""  # Initialize the message
    message_color = RESET_COLOR  # Initialize the message color

    while True:
        display_message_and_prompt(message, "1. Add Shift\n2. Edit Shift\n3. Delete Shift\n4. List Shifts\n\n0. Exit\n\nEnter your choice: ")
        choice = input().strip().lower()

        if choice == "1":
            shift_name = input("What is the name of the shift? (type 'exit' to return to the previous menu): ")
            if shift_name.lower() == 'exit':
                continue  # Go back to the main menu
            shift_times = get_shift_times()
            if not shift_times:
                message = LIGHT_RED + "Invalid shift times. Please try again." + RESET_COLOR
                continue
            lunch_break = get_lunch_break()
            if not lunch_break:
                message = LIGHT_RED + "Invalid lunch break times. Please try again." + RESET_COLOR
                continue
            shifts = load_shifts()
            shifts[shift_name] = {"times": shift_times, "lunch": lunch_break}
            save_shifts(shifts)
            message = LIGHT_GREEN + f"Shift '{shift_name}' added successfully!" + RESET_COLOR
        elif choice in ["2", "3"]:
            list_shifts(only_names=True)
            shift_name = input(f"\nEnter the name of the shift you want to {'edit' if choice == '2' else 'delete'}: ")
            if shift_name.lower() == 'exit':
                continue
            if shift_name in load_shifts():
                display_shift_details(shift_name)
                confirm = input(f"Do you want to {'edit' if choice == '2' else 'delete'} this shift? (yes/no): ").lower()
                if confirm == 'yes':
                    if choice == "2":
                        message = edit_shift(shift_name)
                    elif choice == "3":
                        message = delete_shift(shift_name)
                    message_color = LIGHT_GREEN
                else:
                    continue
            else:
                message = LIGHT_RED + f"Shift '{shift_name}' not found!" + RESET_COLOR
        elif choice == "4":
            list_shifts(only_names=True)
            shift_name = input(f"\nEnter the name of the shift for which you want to see details: (type 'exit' to return) ")
            if shift_name.lower() == 'exit':
                continue
            if shift_name in load_shifts():
                display_shift_details(shift_name)
            else:
                message = LIGHT_RED + f"Shift '{shift_name}' not found!" + RESET_COLOR
            input("\nPress Enter to go back...")
        elif choice == "0":
            return "", RESET_COLOR
        else:
            message = "ERROR: Invalid choice. Please select again."
            message_color = LIGHT_RED

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
