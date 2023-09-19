import socket

# Initialize a dictionary to hold employee states. Here, the state '0' represents clocked-out, and '1' represents clocked-in.
employee_states = {}
employee_info = {}  # To hold the employee names associated with their IDs

# Initialize the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(5)
print("Listening on 0.0.0.0:8000")

def handle_clock_in_out(data, client_socket, employee_states, employee_info):
    employee_id, employee_name = data.split("|")

    # Check if the employee ID already exists
    if employee_id in employee_states:
        # Validate if the name matches the ID
        if employee_info[employee_id] == employee_name:
            if employee_states[employee_id] == 0:
                employee_states[employee_id] = 1
                message = f"Employee {employee_name} is now clocked in."
            else:
                employee_states[employee_id] = 0
                message = f"Employee {employee_name} is now clocked out."
        else:
            message = f"Employee ID and name mismatch. Check your input."
    else:
        # Create a new employee record
        employee_states[employee_id] = 1
        employee_info[employee_id] = employee_name
        message = f"New employee {employee_name} with ID {employee_id} created."

    # Send a response back to the client
    client_socket.sendall(f"{message}\n".encode())

while True:
    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")

    # Read data from the client
    data = client_socket.recv(1024).decode().strip()

    # Call the function to handle the clock-in/out logic
    handle_clock_in_out(data, client_socket, employee_states, employee_info)

    # Close the client socket
    client_socket.close()
