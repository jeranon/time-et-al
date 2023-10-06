import socket
import json

# Function to get the server IP from the server_ip.json
def get_server_ip():
    with open("data/reference/server_ip.json", "r") as file:
        ip_data = json.load(file)
    return ip_data["ip"]

# Get the local machine's hostname
def get_machine_name():
    return socket.gethostname()

# Function to send the clock in/out request to the server
def send_clock_request(employee_data, machine_name=None):
    server_ip = get_server_ip()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, 8000))
        if machine_name:
            client_socket.sendall(f"CLOCK:{employee_data}|{machine_name}".encode())
        else:
            client_socket.sendall(f"CLOCK:{employee_data}".encode())
        response = client_socket.recv(1024).decode()
        print(response)

# Placeholder for job tracking request
def send_job_request(data):
    pass  # You can expand this for job tracking later.

if __name__ == "__main__":
    while True:
        employee_data = input("Please scan or enter employee data (format: ####|first surname) or type 'exit' to quit: ")
        if employee_data.lower() == "exit":
            break

        machine_name = get_machine_name()
        send_clock_request(employee_data, machine_name)
