import socket

def send_data_to_server(data, header):
    # Initialize the client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect(('127.0.0.1', 8000))  # Replace with your server's IP and port

    # Concatenate header and data
    full_data = f"{header}:{data}\n"

    # Send the data to the server
    client_socket.sendall(full_data.encode())

    # Receive data from the server
    received_data = client_socket.recv(1024)
    print(f"Received: {received_data.decode().strip()}")

    # Close the socket
    client_socket.close()

# Ask for input from the user
user_input = input("Please enter employee data (format as '####|First Surname'): ")

# Specify the header (CLOCK or JOB, for example)
header = "CLOCK"  # Change this based on what you're testing

# Send data to the server
send_data_to_server(user_input, header)
