import socket
import json
import os

# Fetch the server IP address from server_ip.json
def get_server_ip():
    with open("data/reference/server_ip.json", "r") as file:
        ip_data = json.load(file)
    return ip_data["ip"]

# Get the local machine's hostname
def get_machine_name():
    return socket.gethostname()

server_ip = get_server_ip()

while True:
    employee_data = input("Please scan or enter employee data (format: ####|first surname) or type 'exit' to quit: ")
    if employee_data.lower() == "exit":
        break

    machine_name = get_machine_name()
    full_data = f"CLOCK:{employee_data}|{machine_name}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, 8000))
        client_socket.sendall(full_data.encode())
        response = client_socket.recv(1024).decode().strip()
        print(response)
