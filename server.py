import socket
import os
import json
from datetime import datetime, timedelta

# Function to get the server's IP address
def get_server_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # We use a dummy IP here to establish a connection in the OS and fetch the local endpoint IP
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

# Function to get configuration data from config.json
def get_config_data():
    with open("data/config/config.json", "r") as file:
        config_data = json.load(file)
    return config_data

# Update the server IP in server_ip.json if it has changed
def update_server_ip():
    current_ip = get_server_ip()
    with open("data/reference/server_ip.json", "r") as file:
        stored_ip_data = json.load(file)
    if stored_ip_data["ip"] != current_ip:
        stored_ip_data["ip"] = current_ip
        with open("data/reference/server_ip.json", "w") as file:
            json.dump(stored_ip_data, file, indent=4)

# Fetch the current pay period based on the start date and duration
def get_current_pay_period():
    config = get_config_data()
    start_date = datetime.strptime(config["pay_period"]["start_date"], "%Y-%m-%d")
    duration = timedelta(days=config["pay_period"]["duration_days"])
    end_date = start_date + duration

    current_date = datetime.now()

    # Adjust the current date based on the work day start hour
    work_day_start_hour = config["work_day"]["start_hour"]
    if current_date.hour < work_day_start_hour:
        current_date -= timedelta(days=1)

    while not start_date <= current_date < end_date:
        start_date += duration
        end_date += duration

    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

# Initialize dictionaries to hold employee states and info.
# State '0' is clocked-out, and '1' is clocked-in.
employee_states = {}
employee_info = {}

def initialize_employee_data():
    global employee_states, employee_info

    # If the employees.json file doesn't exist, we don't do anything.
    if not os.path.exists("data/reference/employees.json"):
        return

    with open("data/reference/employees.json", "r") as file:
        employee_data = json.load(file)

    # Load employee states if the file exists
    if os.path.exists("data/reference/employee_states.json"):
        with open("data/reference/employee_states.json", "r") as state_file:
            saved_states = json.load(state_file)
        for emp_id, state in saved_states.items():
            employee_states[emp_id] = state

    for emp_id, emp_name in employee_data.items():
        employee_info[emp_id] = emp_name

# Initialize the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(5)
print("Listening on 0.0.0.0:8000")

TRANSACTION_COUNTER_FILE = "data/reference/transaction_counter.txt"

def get_transaction_counter():
    """Fetch the current transaction counter. If file doesn't exist, initialize it."""
    if os.path.exists(TRANSACTION_COUNTER_FILE):
        with open(TRANSACTION_COUNTER_FILE, 'r') as file:
            return int(file.read().strip(), 16)  # Convert hex string to integer
    else:
        set_transaction_counter(0)
        return 0

def set_transaction_counter(value):
    """Set the transaction counter to a new value."""
    with open(TRANSACTION_COUNTER_FILE, 'w') as file:
        file.write(format(value, '08X'))  # Convert integer to 8-digit hex string

def increment_transaction_counter():
    """Increment the transaction counter and return its new value in 8-digit hex format."""
    counter = get_transaction_counter() + 1
    set_transaction_counter(counter)
    return format(counter, '08X')

def log_event(event_type, message):
    transaction_id = increment_transaction_counter()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_year = datetime.now().year
    start_date, _ = get_current_pay_period()
    log_path = f"data/logs/{current_year}/{start_date}/{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Ensure directory exists
    if not os.path.exists(os.path.dirname(log_path)):
        os.makedirs(os.path.dirname(log_path))
    
    with open(log_path, 'a') as log_file:
        log_file.write(f"[{timestamp}] [{transaction_id}] [{event_type}] {message}\n")

def write_time_data(employee_id, employee_name, clock_status, client_info):
    start_date, _ = get_current_pay_period()
    year = datetime.now().year
    file_path = f"data/time_scans/{year}/{start_date}.json"
    
    # Ensure directory exists before writing the file
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump({}, file)
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if employee_id not in data:
        data[employee_id] = []
    data[employee_id].append({
        "timestamp": current_timestamp,
        "name": employee_name,
        "status": "in" if clock_status == 1 else "out",
        "client_info": client_info
    })

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def save_employee_states():
    with open("data/reference/employee_states.json", "w") as file:
        json.dump(employee_states, file, indent=4)

def handle_clock_in_out(data, client_address):
    employee_id, employee_name = data.split("|")[:2]
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the employee has a saved state and it's from a previous day
    if employee_id in employee_states and employee_states[employee_id]['last_scan'].split()[0] != current_date:
        employee_states[employee_id]['state'] = 0  # Reset the state to clocked-out

    # The rest of the existing logic follows...
    if employee_id in employee_states:
        if employee_info[employee_id] == employee_name:
            if employee_states[employee_id]['state'] == 0:
                employee_states[employee_id]['state'] = 1
                message = f"SUCCESS: Clocked in employee: {employee_name}."
                log_event("TRANSACTION", f"Employee {employee_name} clocked in.")
            else:
                employee_states[employee_id]['state'] = 0
                message = f"SUCCESS: Clocked out employee: {employee_name}."
                log_event("TRANSACTION", f"Employee {employee_name} clocked out.")
        else:
            message = "ERROR: Employee ID and name mismatch. Check your input."
            log_event("ERROR", f"Failed to process data for employee {employee_name}. Name/ID Mismatch.")
    else:
        employee_states[employee_id] = {"state": 1, "last_scan": current_timestamp}
        employee_info[employee_id] = employee_name
        message = f"SUCCESS: New employee {employee_name} with ID {employee_id} created and clocked in."
        log_event("TRANSACTION", f"Employee {employee_name} with ID {employee_id} created and clocked-in.")

    # Update the last scan time for the employee
    employee_states[employee_id]['last_scan'] = current_timestamp

    client_info = {
        "ip": client_address[0],
        "name": data.split("|")[2] if len(data.split("|")) > 2 else "Unknown"
    }
    
    write_time_data(employee_id, employee_name, employee_states[employee_id]['state'], client_info)
    update_employee_data(employee_id, employee_name)
    update_client_data(client_info)
    save_employee_states()

    client_socket.sendall(f"{message}\n".encode())

def update_employee_data(employee_id, employee_name):
    with open("data/reference/employees.json", "r") as file:
        employees = json.load(file)
    if employee_id not in employees:
        employees[employee_id] = employee_name
        with open("data/reference/employees.json", "w") as file:
            json.dump(employees, file, indent=4)

def update_client_data(client_info):
    with open("data/reference/clients.json", "r") as file:
        clients = json.load(file)
    if client_info["ip"] not in [client["ip"] for client in clients]:
        clients.append(client_info)
        with open("data/reference/clients.json", "w") as file:
            json.dump(clients, file, indent=4)

def handle_job_tracking(data, client_socket):
    # Placeholder for your job tracking logic
    pass

update_server_ip()
initialize_employee_data()

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        data = client_socket.recv(1024).decode().strip()

        if data.startswith("CLOCK:"):
            handle_clock_in_out(data[6:], client_address)  # Pass everything after "CLOCK:"
        elif data.startswith("JOB:"):
            handle_job_tracking(data[4:], client_socket)  # Pass everything after "JOB:"

        client_socket.close()
except KeyboardInterrupt:
    print("\nGracefully shutting down the server...")
    server_socket.close()
    
    print("Server shut down. Goodbye!")
