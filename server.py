import socket
import os

os.system('server.py')

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
