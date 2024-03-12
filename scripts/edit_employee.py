import json
import os
from scripts import display_utils

EMPLOYEE_FILE_PATH = os.path.join("data", "reference", "employees.json")

def load_employees():
    with open(EMPLOYEE_FILE_PATH, "r") as file:
        return json.load(file)

def list_active_employees(employees):
    print("\nList of Active Employees:")
    for emp_id, details in sorted(employees.items(), key=lambda x: x[1]['name']):
        if details['active']:
            print(f"- {details['name']} (ID: {emp_id})")

def display_employee_info(employee_id, employees):
    if employee_id in employees:
        employee = employees[employee_id]
        print(f"\nEmployee ID: {employee_id}")
        for key, value in employee.items():
            print(f"{key.capitalize()}: {value}")
    else:
        print(f"\nEmployee ID {employee_id} not found.")

def edit_employee_details(employee_id, employees):
    if employee_id in employees:
        print("\nEnter the new details for the employee (leave blank to keep current value):")
        name = input("Name: ").strip() or employees[employee_id]['name']
        shift = input("Shift (day/night): ").strip() or employees[employee_id]['shift']
        active = input("Active (1 for active, 0 for inactive): ").strip() or employees[employee_id]['active']
        
        # Update the employee details
        employees[employee_id]['name'] = name
        employees[employee_id]['shift'] = shift
        employees[employee_id]['active'] = int(active)
        
        print(f"\nUpdated details for Employee ID {employee_id}:")
        display_employee_info(employee_id, employees)
        return employees
    else:
        print(f"\nEmployee ID {employee_id} not found.")
        return employees

def save_employees(employees):
    with open(EMPLOYEE_FILE_PATH, "w") as file:
        json.dump(employees, file, indent=4)
    print("\nEmployee details saved successfully.")

def run_edit():
    employees = load_employees()
    list_active_employees(employees)
    employee_id = input("\nEnter Employee ID to edit: ").strip()
    
    display_employee_info(employee_id, employees)
    updated_employees = edit_employee_details(employee_id, employees)
    save_employees(updated_employees)

    return "Employee details updated.", display_utils.LIGHT_GREEN

if __name__ == "__main__":
    print("ERROR: This script cannot be run directly. Please run through admin.py.")
    input("Press Enter to exit...")
