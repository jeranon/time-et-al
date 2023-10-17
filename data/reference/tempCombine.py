import json

# Load data from employees.json
with open("employees.json", "r") as file:
    employees_data = json.load(file)

# Load data from employee_states.json
with open("employee_states.json", "r") as file:
    states_data = json.load(file)

# Combine and update the data
for emp_id, emp_name in employees_data.items():
    if emp_id in states_data:
        states_data[emp_id]["name"] = emp_name
        states_data[emp_id].setdefault("shift", "day")  # Adds the shift "day" only if it doesn't exist
    else:
        states_data[emp_id] = {
            "name": emp_name,
            "state": 0,
            "last_scan": "",
            "shift": "day"
        }

# Save the combined data back to employee_states.json
with open("employee_states.json", "w") as file:
    json.dump(states_data, file, indent=4)
