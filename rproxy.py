import os
import sys
import socket
import threading

enable_debug = True

# Define this proxy server's listening address and port
PROXY_HOST = '0.0.0.0'  # Listen on all available network interfaces
PROXY_PORT = 80

# Define the list of backend server's addresses and ports
BACKEND_SERVERS = [
    ('192.168.68.136', 80)
]

def handle_client(client_socket : socket.socket) -> None:
    """ 
    Handle incoming client requests.

    This function receives HTTP requests from clients connected to the proxy server.
    It processes the requests by forwarding them to one of the backend servers in 
    the load balancing pool. After receiving the response from the backend server, 
    it sends the response back to the client.

    :param client_socket: The client side endpoint.
    :type client_socket: socket.socket
    :return: None
    """
    # TODO: Change from hard-coded to round-robin load balancing.
    backend_address = BACKEND_SERVERS[0]

    backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    backend_socket.connect(backend_address)

    client_request = client_socket.recv(4096)

     # Debug
    if enable_debug:
        print(f'[Debug] Recieved request from client:')
        print(client_request.decode())

    backend_socket.sendall(client_request)
    
    backend_response = backend_socket.recv(4096)
    
    # Debug
    if enable_debug:
        print(f'[Debug] Recieved response from backend:')
        print(backend_response.decode())

    client_socket.sendall(backend_response)

    client_socket.close()
    backend_socket.close()

def start_proxy() -> None:
    """
    Start the reverse proxy server listening loop.
    
    This function initializes the socket for the proxy server, and starts 
    listening for incoming client connections. When a client connects, it 
    spawns a new thread to handle the client's request.

    :return: None
    """
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((PROXY_HOST, PROXY_PORT))
    proxy_socket.listen(5)

    print(f'[*] Proxy server listening on {PROXY_HOST}:{PROXY_PORT}')

    while True:
        client_socket, client_address = proxy_socket.accept()
        print(f'[*] Accepted connection from {client_address[0]}:{client_address[1]}')

        proxy_thread = threading.Thread(target=handle_client, args=(client_socket,))
        proxy_thread.start()

if __name__ == '__main__':
    # TODO: Write parser to read server pool from cfg file.
    # Run the proxy server with root privileges
    if os.geteuid() != 0:
        print("Please run this script as root")
        sys.exit(1)
    
    start_proxy()
