import socket
import os
import json

os.system('title server.py')

# Check if critical directories and files exist
required_dirs = ["data", "data/reference", "data/logs", "data/time_scans", "data/config"]
required_files = ["data/reference/employees.json", "data/reference/server_ip.json", "data/reference/clients.json", "data/config/config.json"]

for directory in required_dirs:
    if not os.path.exists(directory):
        print(f"Critical directory {directory} is missing. Please run setup.py to initialize the environment.")
        exit()

for file in required_files:
    if not os.path.exists(file):
        print(f"Critical file {file} is missing. Please run setup.py to initialize the environment.")
        exit()

# Load configurations from config.json
with open("data/config/config.json", 'r') as config_file:
    configs = json.load(config_file)

# Initialize dictionaries to hold employee states and info.
# State '0' is clocked-out, and '1' is clocked-in.
employee_states = {}
employee_info = {}

# Initialize the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(5)
print("Listening on 0.0.0.0:8000")

def handle_clock_in_out(data, client_socket):
    employee_id, employee_name = data.split("|")

    if employee_id in employee_states:
        if employee_info[employee_id] == employee_name:
            if employee_states[employee_id] == 0:
                employee_states[employee_id] = 1
                message = f"Employee {employee_name} is now clocked in."
            else:
                employee_states[employee_id] = 0
                message = f"Employee {employee_name} is now clocked out."
        else:
            message = "Employee ID and name mismatch. Check your input."
    else:
        employee_states[employee_id] = 1
        employee_info[employee_id] = employee_name
        message = f"New employee {employee_name} with ID {employee_id} created."

    client_socket.sendall(f"{message}\n".encode())

def handle_job_tracking(data, client_socket):
    # Placeholder for your job tracking logic
    pass

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")

    data = client_socket.recv(1024).decode().strip()

    if data.startswith("CLOCK:"):
        handle_clock_in_out(data[6:], client_socket)  # Pass everything after "CLOCK:"
    elif data.startswith("JOB:"):
        handle_job_tracking(data[4:], client_socket)  # Pass everything after "JOB:"

    client_socket.close()
