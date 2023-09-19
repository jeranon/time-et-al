import socket
import os
# Uncomment the next line if you're going to use threading
# import threading

os.system('test_server.py')

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
    # Your clock in/out logic here
    pass

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
