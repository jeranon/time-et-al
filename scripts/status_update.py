import socket
import json
import os
import time

# ANSI Escape Codes for colors
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
RESET_COLOR = "\033[0m"

def get_server_ip():
    """
    Fetch the server IP address from server_ip.json.
    """
    with open("data/reference/server_ip.json", "r") as file:
        ip_data = json.load(file)
    return ip_data["ip"]

def fetch_status():
    """
    Query the server for the status of all employees.
    """
    server_ip = get_server_ip()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, 8000))
        client_socket.sendall("STATUS".encode())
        response = client_socket.recv(4096).decode()
    return response

def display_status():
    """
    Display the status of employees.
    """
    status_data = fetch_status()
    print(f"Debug: Received status data: {status_data}")  # Debug statement
    in_list = []
    out_list = []

    # Check if status_data is not empty
    if not status_data.strip():
        print("Debug: Status data is empty")
        return
    
    # Parsing the status data
    for entry in status_data.splitlines():
        if "|" in entry:
            name, status = entry.split("|")
            if status == "IN":
                in_list.append(name)
            else:
                out_list.append(name)
        else:
            print(f"Debug: Invalid entry format: {entry}")  # Debug invalid entries

    # Clear the screen and print the status
    os.system('cls' if os.name == 'nt' else 'clear')
    print(LIGHT_GREEN + "IN:" + RESET_COLOR)
    for name in in_list:
        print(LIGHT_GREEN + name + RESET_COLOR)
    print()
    print(LIGHT_RED + "OUT:" + RESET_COLOR)
    for name in out_list:
        print(LIGHT_RED + name + RESET_COLOR)

def periodic_status_update():
    """
    Periodically update the status.
    """
    while True:
        display_status()
        time.sleep(60)

if __name__ == "__main__":
    periodic_status_update()
