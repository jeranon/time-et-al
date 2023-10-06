import socket
import json
import os

# ANSI Escape Codes for colors
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
LIGHT_BLUE = "\033[94m"
BUTTER_YELLOW = "\033[38;5;221m"
LIGHT_PURPLE = "\033[38;5;141m"
RESET_COLOR = "\033[0m"

def get_server_ip():
    """
    Fetch the server IP address from server_ip.json.
    """
    with open("data/reference/server_ip.json", "r") as file:
        ip_data = json.load(file)
    return ip_data["ip"]

def get_machine_name():
    """
    Get the local machine's hostname.
    """
    return socket.gethostname()

def display_message_and_prompt(message=""):
    """
    Display a message at the top of the screen followed by the prompt.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(message)
    print(LIGHT_BLUE + "\nClock In/Out" + RESET_COLOR)
    print(LIGHT_BLUE + "----------------------\n" + RESET_COLOR)

def run_clock_in_out():
    """
    Run the Clock In/Out loop.
    """
    server_ip = get_server_ip()
    message = ""  # Initialize the message
    
    while True:
        display_message_and_prompt(message)
        employee_data = input("Please scan employee data or type 'exit' to quit: ")
        
        if employee_data.lower() == "exit":
            message = "" # Clear the message when exiting
            return message # Return the current message when exiting
        
        # Check for the presence of a vertical pipe in the input
        if "|" not in employee_data:
            message = LIGHT_RED + "ERROR: Invalid input format. Please scan again." + RESET_COLOR
            continue
        
        machine_name = get_machine_name()
        full_data = f"CLOCK:{employee_data}|{machine_name}"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, 8000))
            client_socket.sendall(full_data.encode())
            response = client_socket.recv(1024).decode().strip()  # Update the message
            
            if "SUCCESS" in response:
                message = LIGHT_GREEN + response + RESET_COLOR
            elif "ERROR" in response:
                message = LIGHT_RED + response + RESET_COLOR
            
            if "Clocked in" in message:
                message = message.replace("Clocked in", BUTTER_YELLOW + "Clocked in" + LIGHT_GREEN)
            elif "Clocked out" in message:
                message = message.replace("Clocked out", LIGHT_PURPLE + "Clocked out" + LIGHT_GREEN)

if __name__ == "__main__":
    os.system('')
    print(LIGHT_RED + "ERROR: This script cannot be run directly. Please run through main_loader.py. Press Enter to exit..." + RESET_COLOR)
    input("")