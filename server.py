import socket
import os
import json
import select
from datetime import datetime, timedelta

SHIFT_FILE_PATH = os.path.join("data", "reference", "shifts.json")

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
    
config = get_config_data()

# Update the server IP in server_ip.json if it has changed
def update_server_ip():
    current_ip = get_server_ip()
    with open(os.path.join(config["paths"]["reference_dir"], "server_ip.json"), "r") as file:
        stored_ip_data = json.load(file)
    if stored_ip_data["ip"] != current_ip:
        stored_ip_data["ip"] = current_ip
        with open(os.path.join(config["paths"]["reference_dir"], "server_ip.json"), "w") as file:
            json.dump(stored_ip_data, file, indent=4)

# Fetch the current pay period based on the start date and duration
def get_current_pay_period():
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

    # Define the path for employees.json using the config variable
    employees_path = os.path.join(config["paths"]["reference_dir"], "employees.json")

    # If the employees.json file doesn't exist, we don't do anything.
    if not os.path.exists(employees_path):
        return

    with open(employees_path, "r") as file:
        employee_data = json.load(file)

    for emp_id, attributes in employee_data.items():
        employee_info[emp_id] = attributes["name"]
        employee_states[emp_id] = {
            "state": attributes["state"],
            "last_scan": attributes["last_scan"]
        }

# Initialize the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(5)
server_socket.setblocking(0)

TRANSACTION_COUNTER_FILE = os.path.join(config["paths"]["reference_dir"], "transaction_counter.txt")

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
    log_path = os.path.join(config["paths"]["logs_dir"], str(current_year), start_date, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # Ensure directory exists
    if not os.path.exists(os.path.dirname(log_path)):
        os.makedirs(os.path.dirname(log_path))
    
    with open(log_path, 'a') as log_file:
        log_file.write(f"[{timestamp}] [{transaction_id}] [{event_type}] {message}\n")

def save_employee_states():
    # Load existing employees' data first to preserve the shift values
    with open(os.path.join(config["paths"]["reference_dir"], "employees.json"), "r") as file:
        combined_data = json.load(file)
    
    for emp_id in employee_info:
        if emp_id not in combined_data:
            combined_data[emp_id] = {
                "name": employee_info[emp_id],
                "state": employee_states[emp_id]["state"] if emp_id in employee_states else 0,
                "last_scan": employee_states[emp_id]["last_scan"] if emp_id in employee_states else "",
                "shift": employee_states[emp_id]["shift"] if "shift" in employee_states[emp_id] else "unknown"
            }
        else:
            # If the employee exists, only update the name, state, and last_scan, but not the shift
            combined_data[emp_id]["name"] = employee_info[emp_id]
            combined_data[emp_id]["state"] = employee_states[emp_id]["state"] if emp_id in employee_states else 0
            combined_data[emp_id]["last_scan"] = employee_states[emp_id]["last_scan"] if emp_id in employee_states else ""

    with open(os.path.join(config["paths"]["reference_dir"], "employees.json"), "w") as file:
        json.dump(combined_data, file, indent=4)

def write_time_data(employee_id, employee_name, clock_status, client_info):
    start_date, _ = get_current_pay_period()
    year = datetime.now().year
    file_path = os.path.join(config["paths"]["time_scans_dir"], str(year), f"{start_date}.json")

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

def handle_clock_in_out(data, client_address, client_socket):
    try:
        print("Processing clock in/out request...")
        employee_id, employee_name = data.split("|")[:2]
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if the employee has a saved state and it's from a previous day
        if employee_id in employee_states and employee_states[employee_id]['last_scan'].split()[0] != current_date:
            employee_states[employee_id]['state'] = 0  # Reset the state to clocked-out

        if employee_id in employee_states:
            if employee_info[employee_id] == employee_name:
                if employee_states[employee_id]['state'] == 0:
                    employee_states[employee_id]['state'] = 1
                    message = f"SUCCESS: Clocked in employee: {employee_name}."
                    save_employee_states()
                    log_event("TRANSACTION", f"Employee {employee_name} clocked in.")
                else:
                    # Before we set the state to 0 (clocking out), 
                    # we need to ensure the job tracking for the last job is complete
                    write_job_tracking_data(employee_id, None)
                    
                    employee_states[employee_id]['state'] = 0
                    message = f"SUCCESS: Clocked out employee: {employee_name}."
                    save_employee_states()
                    log_event("TRANSACTION", f"Employee {employee_name} clocked out.")
            else:
                message = "ERROR: Employee ID and name mismatch. Check your input."
                log_event("ERROR", f"Failed to process data for employee {employee_name}. Name/ID Mismatch.")
        else:
            message = f"ERROR: Employee ID {employee_id} not recognized. Please onboard the employee first."
            log_event("ERROR", message)
            # print(f"Sending to client: {message}") # Debugging line
            client_socket.sendall(f"{message}\n".encode())
            return
            
        # Update the last scan time for the employee
        employee_states[employee_id]['last_scan'] = current_timestamp
        save_employee_states()

        client_info = {
            "ip": client_address[0],
            "name": data.split("|")[2] if len(data.split("|")) > 2 else "Unknown"
        }
        
        write_time_data(employee_id, employee_name, employee_states[employee_id]['state'], client_info)
        save_employee_states()
        update_client_data(client_info)

        # print(f"Sending to client: {message}")  # Debugging line
        client_socket.sendall(f"{message}\n".encode())

    except Exception as e:
        error_message = f"ERROR: Failed to process request due to: {str(e)}"
        # print(error_message)  # Debugging line
        log_event("ERROR", error_message)
        client_socket.sendall(f"{error_message}\n".encode())

def update_employee_data(employee_id, employee_name):
    employees_path = os.path.join(config["paths"]["reference_dir"], "employees.json")
    with open(employees_path, "r") as file:
        employees = json.load(file)
    
    if employee_id not in employees:
        employees[employee_id] = {
            "name": employee_name,
            "state": 0,
            "last_scan": ""
        }
    else:
        employees[employee_id]["name"] = employee_name
        employees[employee_id]["state"] = employee_states[employee_id]["state"]
        employees[employee_id]["last_scan"] = employee_states[employee_id]["last_scan"]

    with open(employees_path, "w") as file:
        json.dump(employees, file, indent=4)

def update_client_data(client_info):
    clients_path = os.path.join(config["paths"]["reference_dir"], "clients.json")
    with open(clients_path, "r") as file:
        clients = json.load(file)
    if client_info["ip"] not in [client["ip"] for client in clients]:
        clients.append(client_info)
        with open(clients_path, "w") as file:
            json.dump(clients, file, indent=4)

def handle_check_employee_request(data):
    """
    Check if the provided employee ID is valid and if the employee is clocked in.
    """
    employee_id, employee_name = data.split('|')
    
    if employee_id not in employee_info or employee_info[employee_id] != employee_name:
        log_event("JOB_TRACKING", f"Failed check for {employee_name} ({employee_id}): Invalid ID or Name mismatch.")
        return "ERROR: Invalid Employee ID or Name mismatch."
    if employee_id not in employee_states or employee_states[employee_id]['state'] == 0:
        log_event("JOB_TRACKING", f"Failed check for {employee_name} ({employee_id}): Employee not clocked in.")
        return "ERROR: Employee not clocked in."
    log_event("JOB_TRACKING", f"Successful check for {employee_name} ({employee_id}): Employee is clocked in.")
    return f"SUCCESS: {employee_name} is clocked in. Please proceed below."

def handle_process_request(employee_id, employee_name, job_num):
    """
    Handle the job number processing for the given employee ID.
    """
    write_job_tracking_data(employee_id, job_num)
    response = f"SUCCESS: {employee_name} scanned onto job #: {job_num}"
    log_event("JOB_TRACKING", f"Processed job number for {employee_name}: {response}")
    return response

def handle_onboarding_request(data):
    """
    Handle the onboarding request to add a new employee.
    """
    try:
        # Extract data from the received string
        employee_id, employee_name, shift = data.split("|")
        
        # print(f"Received onboarding request: ID={employee_id}, Name={employee_name}, Shift={shift}")  # Debugging
        
        # Load shifts to validate the provided shift
        shifts = load_shifts()
        # print(f"Loaded shifts: {shifts}")  # Debugging
        # print(f"Checking if {shift} is in shifts...")
        # print(f"Type of shifts: {type(shifts)}")
        # print(f"Content of shifts: {shifts}")
        
        # Check if the employee ID or name already exists
        if employee_id in employee_info:
            message = f"ERROR: Employee ID {employee_id} already exists."
            log_event("ONBOARDING", message)
        elif employee_name in employee_info.values():
            message = f"ERROR: Employee name {employee_name} already exists."
            log_event("ONBOARDING", message)
        elif shift not in shifts:
            message = f"ERROR: Shift {shift} does not exist. Please add the shift first."
            log_event("ONBOARDING", message)
        else:
            # print("Adding new employee...")  # Debugging
            # print(f"Type of employee_info: {type(employee_info)}")
            # print(f"Type of employee_states: {type(employee_states)}")
            # Add employee to the data structures
            employee_info[employee_id] = employee_name
            employee_states[employee_id] = {
                "name": employee_name,
                "state": 0,  # Initial state: Clocked-out
                "last_scan": "",
                "shift": shift
            }
            
            # Save the changes
            # print("Saving changes...")  # Debugging
            save_employee_states()
            message = f"SUCCESS: New employee {employee_name} with ID {employee_id} onboarded."
            log_event("ONBOARDING", message)
            
        return message
    except Exception as e:
        error_message = f"ERROR: Failed to onboard employee due to: {str(e)}"
        # print(error_message)  # Debugging
        log_event("ERROR", error_message)
        return error_message

def load_shifts():
    """
    Load the shifts from shifts.json.
    """
    with open(SHIFT_FILE_PATH, 'r') as file:
        return json.load(file)

def write_job_tracking_data(employee_id, job_num):
    start_date, _ = get_current_pay_period()
    year = datetime.now().year
    current_day = datetime.now().strftime("%Y-%m-%d")
    
    # Using os.path.join() to create the full path
    file_path = os.path.join(config["paths"]["job_scans_dir"], str(year), start_date, f"{current_day}.json")

    # Ensure directory exists before writing the file
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    current_data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            current_data = json.load(file)
    
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if employee_id not in current_data:
        current_data[employee_id] = []
    
    # Check if the employee is already assigned to a job
    if current_data[employee_id] and 'job_end' not in current_data[employee_id][-1]:
        current_data[employee_id][-1]['job_end'] = current_timestamp
        start_time = datetime.strptime(current_data[employee_id][-1]['job_start'], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(current_data[employee_id][-1]['job_end'], "%Y-%m-%d %H:%M:%S")
        duration = (end_time - start_time).total_seconds()
        current_data[employee_id][-1]['total_time'] = duration
    
    # Add the new job scan
    current_data[employee_id].append({
        "job_start": current_timestamp,
        "job_num": job_num
    })

    with open(file_path, 'w') as file:
        json.dump(current_data, file, indent=4)

update_server_ip()
initialize_employee_data()

server_socket.settimeout(1) # 1 second timeout

print("Listening on 0.0.0.0:8000")
inputs = [server_socket]
while True:
    try:
        readable, _, _ = select.select(inputs, [], [], 1)  # 1 second timeout for select
        for s in readable:
            if s is server_socket:
                client_socket, client_address = s.accept()
                print(f"Accepted connection from {client_address}")

                data = client_socket.recv(1024).decode().strip()
                # print(f"Received from client: {data}")  # debugging line

                if data.startswith("CLOCK:"):
                    handle_clock_in_out(data[6:], client_address, client_socket)  # Pass everything after "CLOCK:"
                elif data.startswith("JOB:CHECK_EMPLOYEE:"):
                    response = handle_check_employee_request(data.split(":")[2])
                    log_event("JOB_TRACKING", f"Checked employee status for job tracking: {response}")
                    client_socket.sendall(response.encode())
                    # print(f"Sending to client: {response}")  # debugging line
                elif data.startswith("JOB:PROCESS:"):
                    components = data.split(":")[2].split("|")
                    if len(components) != 3:
                        print("ERROR: Incorrect format received from client.")
                        log_event("ERROR", "Incorrect format received from client for job processing.")
                        continue
                    emp_id, employee_name, job_num = components
                    response = handle_process_request(emp_id, employee_name, job_num)
                    log_event("JOB_TRACKING", f"Processed job number for {employee_name}: {response}")
                    client_socket.sendall(response.encode())
                    # print(f"Sending to client: {response}\n")  # debugging line
                elif data.startswith("ONBOARD:"):
                    # print("ONBOARD request identified!")  # Debugging line
                    response = handle_onboarding_request(data[8:])
                    # print(f"Response from handle_onboarding_request: {response}")  # Debugging
                    client_socket.sendall(response.encode())
                    # print(f"Sending to client: {response}")  # Debugging
                # else:
                    # print(f"Unknown request type: {data}") # Debugging line
                client_socket.close()

    except KeyboardInterrupt:
        print("\nGracefully shutting down the server...")
        server_socket.close()
        print("Server shut down. Goodbye!")
        break
    except Exception as e:
        log_event("ERROR", f"An error occurred: {str(e)}")
        try:
            client_socket.sendall("ERROR: An unexpected error occurred on the server.\n".encode())
        except:
            pass
        client_socket.close()  # Close the client socket if it's still open
