import socket
import json
import os
import threading
import time

# ANSI Escape Codes for colors
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
LIGHT_BLUE = "\033[94m"
BUTTER_YELLOW = "\033[38;5;221m"
LIGHT_PURPLE = "\033[38;5;141m"
RESET_COLOR = "\033[0m"

# Global variable to store the current time
current_time = "XX:XX"
status_display = ""

def set_current_time(new_time):
    global current_time
    current_time = new_time

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

def fetch_status():
    """
    Query the server for the status of all employees.
    """
    server_ip = get_server_ip()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, 8000))
            client_socket.sendall("STATUS".encode())
            response = client_socket.recv(4096).decode()
            return response
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return ""

def get_status_display():
    """
    Fetch and format the status display.
    """
    status_data = fetch_status()
    in_list = []
    out_list = []

    # Check if status_data is not empty
    if not status_data.strip():
        return "Status data is empty"

    # Parsing the status data
    for entry in status_data.splitlines():
        if "|" in entry:
            name, status = entry.split("|")
            if status == "IN":
                in_list.append(name)
            else:
                out_list.append(name)

    # Sort the lists alphabetically
    in_list.sort()
    out_list.sort()

    # Calculate the number of lines needed for each column
    max_lines = max(len(in_list), len(out_list))

    # Create formatted strings for each column
    in_column = LIGHT_GREEN + "IN" + RESET_COLOR + "\n" + LIGHT_GREEN + "--------------" + RESET_COLOR + "\n"
    out_column = LIGHT_RED + "OUT" + RESET_COLOR + "\n" + LIGHT_RED + "--------------" + RESET_COLOR + "\n"

    for i in range(max_lines):
        in_column += LIGHT_GREEN + (in_list[i] if i < len(in_list) else "") + RESET_COLOR + "\n"
        out_column += LIGHT_RED + (out_list[i] if i < len(out_list) else "") + RESET_COLOR + "\n"

    # Combine the columns side by side
    in_lines = in_column.splitlines()
    out_lines = out_column.splitlines()

    status_display_lines = [in_line.ljust(40) + out_line for in_line, out_line in zip(in_lines, out_lines)]
    status_display = "\n".join(status_display_lines)

    return status_display

def display_message_and_prompt(message="", status_display=""):
    """
    Display a message at the top of the screen followed by the prompt and status display.
    """
    clear_screen()
    print(message)
    # Create the line with "Clock In/Out" and current time aligned to the right
    title = "Clock In/Out"
    separator = " " * (40 - len(title))
    title_line = LIGHT_BLUE + title + separator + current_time + RESET_COLOR
    print(title_line)
    print(LIGHT_BLUE + "---------------------------------------------\n" + RESET_COLOR)
    print(status_display)
    print("\nPlease scan employee ID:")

def set_console_buffer_size(lines=1000):
    """
    Set the console buffer size to handle more lines.
    """
    if os.name == 'nt':
        os.system(f'mode con: cols=120 lines={lines}')

def clear_screen():
    """
    Clear the console screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def periodic_status_update():
    """
    Periodically update the status.
    """
    global status_display
    while True:
        status_display = get_status_display()
        display_message_and_prompt(status_display=status_display)
        time.sleep(15)

def run_clock_in_out():
    """
    Run the Clock In/Out loop.
    """
    global status_display
    status_display = get_status_display()  # Initialize the status display
    server_ip = get_server_ip()
    message = ""  # Initialize the message

    # Initially display the status
    display_message_and_prompt(message, status_display)
    
    while True:
        employee_data = input()
        
        if employee_data.lower() == "exit":
            message = "" # Clear the message when exiting
            return message # Return the current message when exiting
        
        # Check for the presence of a vertical pipe in the input
        if "|" not in employee_data:
            message = LIGHT_RED + "ERROR: Invalid input format. Please scan again." + RESET_COLOR
            display_message_and_prompt(message, status_display)
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
            
            # Immediate status update after a short delay
            time.sleep(0.25)
            status_display = get_status_display()
            display_message_and_prompt(message, status_display)

if __name__ == "__main__":
    os.system('')  # Initialize ANSI escape codes on Windows
    set_console_buffer_size(lines=1000)  # Set console buffer size to handle more lines
    clear_screen()
    status_display = "Initializing status display..."
    run_clock_in_out()
