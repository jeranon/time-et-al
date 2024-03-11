import json
import os
from scripts.id_gen import generate_id
from scripts import display_utils

EMPLOYEE_FILE_PATH = os.path.join("data", "reference", "employees.json")

def load_employees():
    """
    Load the employee data from employees.json and return it as a list of dictionaries,
    only including active employees.
    """
    with open(EMPLOYEE_FILE_PATH, 'r') as file:
        employees_dict = json.load(file)
    # Filter out inactive employees (where 'active' is not "1")
    return [{'id': key, **value} for key, value in employees_dict.items() if value['active'] == 1]

def run_reprint():
    """
    Function to handle the reprinting of employee ID cards.
    """
    employees = load_employees()
    employees_sorted = sorted(employees, key=lambda x: x['name'])

    display_utils.display_header("Reprint Employee ID Card")
    
    print("List of Employees:")
    for employee in employees_sorted:
        print(f"{employee['id']}: {employee['name']}")

    while True:
        employee_id = input("Enter Employee ID to reprint or type 'exit' to quit: ").strip()
        if employee_id.lower() == 'exit':
            return "Operation cancelled.", display_utils.RESET_COLOR

        # Find the employee with the matching ID
        employee = next((emp for emp in employees if emp['id'] == employee_id), None)
        if employee:
            generate_id(employee_id, employee['name'])  # Pass both employee_id and user_name
            return f"ID card reprinted for employee {employee_id} - {employee['name']}.", display_utils.LIGHT_GREEN
        else:
            print("Invalid Employee ID. Please try again.")

if __name__ == "__main__":
    if can_run_directly:
        print("ERROR: This script cannot be run directly. Please run through admin.py.")
        input("Press Enter to exit...")
    else:
        display_utils.print_colored("ERROR: This script cannot be run directly. Please run through admin.py.", display_utils.LIGHT_RED)
        input("Press Enter to exit...")