import os
import socket
import json

# ANSI Escape Codes for colors
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
LIGHT_BLUE = "\033[94m"
BUTTER_YELLOW = "\033[38;5;221m"
LIGHT_PURPLE = "\033[38;5;141m"
RESET_COLOR = "\033[0m"

def display_message_and_prompt(message="", prompt=""):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(message)
    print(LIGHT_BLUE + "\nJob Tracking" + RESET_COLOR)
    print(LIGHT_BLUE + "----------------------\n" + RESET_COLOR)
    if prompt:
        print(prompt)

def run_job_tracking():
    message = ""  # Initialize the message
    prompt = "Please scan your employee ID or type 'exit' to quit: "
    
    while True:
        display_message_and_prompt(message, prompt)
        employee_id_scan = input()
        
        if employee_id_scan == "exit":
            message = "" # Clear the message when exiting
            return message # Return the current message when exiting

        # Send the employee ID to the server to check its validity
        response = send_data_to_server(f"JOB:CHECK_EMPLOYEE:{employee_id_scan}")
        if "ERROR" in response:
            message = LIGHT_RED + response + RESET_COLOR
            continue

        # Extract employee name from the response
        employee_name = response.split(":")[-1].strip()
        message = f"{LIGHT_GREEN}Thank you {employee_name}.{RESET_COLOR}"

        # Get job number
        while True:
            display_message_and_prompt(message, "Please scan the job number or type 'exit' to quit: ")
            job_number_scan = input()

            if job_number_scan == "exit":
                message = ""  # Clear the message when exiting
                return message  # Return the current message when exiting

            # Validate the job number scan
            if job_number_scan == employee_id_scan or "|" in job_number_scan:
                message = LIGHT_RED + "ERROR: Invalid job number scan. Please try again." + RESET_COLOR
                continue
            else:
                break  # If valid, break out of the inner loop to process

        # Send the job number to the server for processing
        response = send_data_to_server(f"JOB:PROCESS:{employee_id_scan}|{job_number_scan}")
        if "SUCCESS" in response:
            message = LIGHT_GREEN + response + RESET_COLOR
        else:
            message = LIGHT_RED + response + RESET_COLOR

def get_server_ip():
    """
    Fetch the server IP address from server_ip.json.
    """
    with open("data/reference/server_ip.json", "r") as file:
        ip_data = json.load(file)
    return ip_data["ip"]

def send_data_to_server(data):
    """
    Sends data to the server and awaits a response.
    """
    server_ip = get_server_ip()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, 8000))
        client_socket.sendall(data.encode())
        print(f"Sent to server: {data}")  # Debugging line
        response = client_socket.recv(1024).decode().strip()
        print(f"Received from server: {response}")  # Debugging line
    return response

if __name__ == "__main__":
    os.system('')
    print(LIGHT_RED + "ERROR: This script cannot be run directly. Please run through main_loader.py. Press Enter to exit..." + RESET_COLOR)
    input("")
