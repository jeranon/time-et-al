import socket
import threading

def handle_client(client_socket):
    data = "Hello, World!"
    client_socket.send(data.encode())
    client_socket.close()

host = "0.0.0.0"  # Listen on all available interfaces
port = 8000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)  # Max 5 queued connections

print(f"Listening on {host}:{port}")

while True:
    client_socket, address = server_socket.accept()
    print(f"Accepted connection from {address}")
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
