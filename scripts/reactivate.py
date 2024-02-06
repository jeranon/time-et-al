# reactivate.py
import socket
import json
import os
from scripts import display_utils

SERVER_IP_FILE_PATH = os.path.join("data", "reference", "server_ip.json")

def get_server_ip():
    with open(SERVER_IP_FILE_PATH, "r") as file:
        ip_data = json.load(file)
    return ip_data["ip"]

def display_deactivated_employees():
    with open("data/reference/employees.json", "r") as file:
        employees = json.load(file)
    print("\nDeactivated Employees:")
    for emp_id, details in employees.items():
        if not details.get("active", 0):
            print(f"- ID: {emp_id}, Name: {details['name']}")

def run_reactivate():
    server_ip = get_server_ip()
    display_deactivated_employees()

    while True:
        employee_id = input("\nEnter Employee ID to reactivate or type 'exit' to quit: ").strip()

        if employee_id.lower() == "exit":
            return "Exiting reactivation.", display_utils.RESET_COLOR

        # Send the reactivation request to the server
        data = f"REACTIVATE:{employee_id}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, 8000))
            client_socket.sendall(data.encode())
            response = client_socket.recv(1024).decode().strip()

        if "SUCCESS" in response:
            color = display_utils.LIGHT_GREEN
        else:
            color = display_utils.LIGHT_RED

        return response, color

if __name__ == "__main__":
    # Prevents the script from running directly
    print("ERROR: This script cannot be run directly. Please run through admin.py.")
    input("Press Enter to exit...")
