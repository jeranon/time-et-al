import socket
import json
import os
from utilities.id_gen import generate_id

# ANSI Escape Codes for colors
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
LIGHT_BLUE = "\033[94m"
RESET_COLOR = "\033[0m"

SHIFT_FILE_PATH = os.path.join("data", "reference", "shifts.json")
SERVER_IP_FILE_PATH = os.path.join("data", "reference", "server_ip.json")

def get_server_ip():
    """
    Fetch the server IP address from server_ip.json.
    """
    with open(SERVER_IP_FILE_PATH, "r") as file:
        ip_data = json.load(file)
    return ip_data["ip"]

def load_shifts():
    """
    Load the shifts from shifts.json.
    """
    with open(SHIFT_FILE_PATH, 'r') as file:
        return json.load(file)

def display_message_and_prompt(message="", prompt=""):
    """
    Display a message and a prompt for the user.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(message)
    print(LIGHT_BLUE + "\nOnboard Employee" + RESET_COLOR)
    print(LIGHT_BLUE + "----------------------\n" + RESET_COLOR)
    if prompt:
        print(prompt)

def run_onboard():
    """
    Onboard a new employee.
    """
    message = ""  # Initialize the message
    server_ip = get_server_ip()
    shifts = load_shifts()
    
    while True:
        display_message_and_prompt(message, "Enter Employee Number or type 'exit' to quit: ")
        employee_id = input().strip()
        
        if employee_id.lower() == "exit":
            return LIGHT_GREEN + "Exiting onboarding." + RESET_COLOR
        
        display_message_and_prompt(message, "Enter Employee Name or type 'exit' to quit: ")
        employee_name = input().strip()
        
        if employee_name.lower() == "exit":
            return LIGHT_GREEN + "Exiting onboarding." + RESET_COLOR
        
        print("\nAvailable shifts:")
        for shift in shifts:
            print(f"- {shift}")

        shift_choice = input("\nEnter the name of the shift for this employee or type 'exit' to quit: ").strip()
        if shift_choice.lower() == "exit":
            return LIGHT_GREEN + "Exiting onboarding." + RESET_COLOR

        if shift_choice not in shifts:
            message = LIGHT_RED + "ERROR: Invalid shift choice." + RESET_COLOR
            continue

        # Construct the onboarding data string
        data = f"ONBOARD:{employee_id}|{employee_name}|{shift_choice}"

        # Connect to the server and send the onboarding data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, 8000))
            client_socket.sendall(data.encode())
            response = client_socket.recv(1024).decode().strip()  # Get the server's response
            
            if "SUCCESS" in response:
                # On successful onboarding, generate the ID using id_gen.py
                generate_id(employee_id, employee_name)
                message = LIGHT_GREEN + response + RESET_COLOR
            else:
                message = LIGHT_RED + response + RESET_COLOR

if __name__ == "__main__":
    os.system('')
    print(LIGHT_RED + "ERROR: This script cannot be run directly. Please run through admin.py. Press Enter to exit..." + RESET_COLOR)
    input("")
