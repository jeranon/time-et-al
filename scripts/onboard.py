import socket
import json
import os
try:
    from scripts.id_gen import generate_id
    from scripts import display_utils
    can_run_directly = False
except ImportError:
    can_run_directly = True

SHIFT_FILE_PATH = os.path.join("data", "reference", "shifts.json")
SERVER_IP_FILE_PATH = os.path.join("data", "reference", "server_ip.json")

def get_server_ip():
    """Fetch the server IP address from server_ip.json."""
    with open(SERVER_IP_FILE_PATH, "r") as file:
        ip_data = json.load(file)
    return ip_data["ip"]

def load_shifts():
    """Load the shifts from shifts.json."""
    with open(SHIFT_FILE_PATH, 'r') as file:
        return json.load(file)

def run_onboard():
    """Onboard a new employee."""
    message = ""  # Initialize the message
    server_ip = get_server_ip()
    shifts = load_shifts()
    
    while True:
        display_utils.display_header("Onboard Employee", message)
        employee_id = input("Enter Employee Number or type 'exit' to quit: ").strip()
        
        if employee_id.lower() == "exit":
            return "Exiting onboarding."
        
        employee_name = input("Enter Employee Name or type 'exit' to quit: ").strip()
        if employee_name.lower() == "exit":
            return "Exiting onboarding."
        
        print("\nAvailable shifts:")
        for shift in shifts:
            print(f"- {shift}")

        shift_choice = input("\nEnter the name of the shift for this employee or type 'exit' to quit: ").strip()
        if shift_choice.lower() == "exit":
            return "Exiting onboarding."

        if shift_choice not in shifts:
            message = "ERROR: Invalid shift choice."
            with open("debug_log.txt", "a") as debug_file:
                debug_file.write(f"Debug: Color code set to red: {repr(display_utils.LIGHT_RED)}\n")
            display_utils.print_colored(message, display_utils.LIGHT_RED)
            continue

        # Construct the onboarding data string
        data = f"ONBOARD:{employee_id}|{employee_name}|{shift_choice}"

        # Connect to the server and send the onboarding data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, 8000))
            client_socket.sendall(data.encode())
            response = client_socket.recv(1024).decode().strip()  # Get the server's response
            
            print("Debug: message before print_colored:", repr(message))
            
            if "SUCCESS" in response:
                generate_id(employee_id, employee_name)
                message = response
                print("Debug: Color code for success:", repr(display_utils.LIGHT_GREEN))
                display_utils.print_colored(message, display_utils.LIGHT_GREEN)
            else:
                message = response
                print("Debug: Color code for error:", repr(display_utils.LIGHT_RED))
                display_utils.print_colored(message, display_utils.LIGHT_RED)

if __name__ == "__main__":
    if can_run_directly:
        print("ERROR: This script cannot be run directly. Please run through admin.py.")
        input("Press Enter to exit...")
    else:
        display_utils.print_colored("ERROR: This script cannot be run directly. Please run through admin.py.", display_utils.LIGHT_RED)
        input("Press Enter to exit...")