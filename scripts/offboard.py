import socket
import json
import os
try:
    from scripts import display_utils
    can_run_directly = False
except ImportError:
    can_run_directly = True

SERVER_IP_FILE_PATH = os.path.join("data", "reference", "server_ip.json")

def get_server_ip():
    """Fetch the server IP address from server_ip.json."""
    with open(SERVER_IP_FILE_PATH, "r") as file:
        ip_data = json.load(file)
    return ip_data["ip"]

def run_offboard():
    """Offboard an existing employee."""
    message = ""  # Initialize the message
    server_ip = get_server_ip()

    while True:
        display_utils.display_header("Offboard Employee", message)
        employee_id = input("Enter Employee Number or type 'exit' to quit: ").strip()

        if employee_id.lower() == "exit":
            return "Exiting offboarding.", display_utils.RESET_COLOR

        # Construct the offboarding data string
        data = f"OFFBOARD:{employee_id}"

        # Connect to the server and send the offboarding data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((server_ip, 8000))
                client_socket.sendall(data.encode())
                response = client_socket.recv(1024).decode().strip()  # Get the server's response

                if "SUCCESS" in response:
                    message = response
                    color = display_utils.LIGHT_GREEN
                else:
                    message = response
                    color = display_utils.LIGHT_RED

                return message, color

            except Exception as e:
                message = f"ERROR: Failed to connect to the server: {str(e)}"
                return message, display_utils.LIGHT_RED

if __name__ == "__main__":
    if can_run_directly:
        print("ERROR: This script cannot be run directly. Please run through admin.py.")
        input("Press Enter to exit...")
    else:
        display_utils.print_colored("ERROR: This script cannot be run directly. Please run through admin.py.", display_utils.LIGHT_RED)
        input("Press Enter to exit...")
