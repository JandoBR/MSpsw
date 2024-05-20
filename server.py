import socket
from _thread import start_new_thread
from typing import List, NoReturn
import threading

IP_ADDRESS = "192.168.1.2"
PORT = 8081
MAX_CLIENTS = 10
LIST_OF_CLIENTS: List[socket.socket] = []

SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

SEARCH_RANGE_START, SEARCH_RANGE_END = 0, 256
server_running = True


def client_thread(client_socket: socket.socket, client_address: tuple) -> NoReturn:
    client_socket.send(b"Connection succeeded")
    while True:
        try:
            message = client_socket.recv(2048)
            if message:
                message_str = message.decode('utf-8')
                print(f"<{client_address[0]}> {message_str}")
                if message_str.startswith("password_found"):
                    stop_other_clients(client_socket)
            else:
                remove(client_socket)
                break
        except Exception as e:
            print(f"Error: {e}")
            remove(client_socket)
            break


def stop_other_clients(client_socket: socket.socket):
    message_to_send = "password_found"
    broadcast(message_to_send.encode('utf-8'), client_socket)


def update_search_range() -> None:
    global SEARCH_RANGE_START, SEARCH_RANGE_END
    num_clients = len(LIST_OF_CLIENTS)
    if num_clients == 0:
        print("No clients connected to update the search range.")
        return

    chunk_size = (SEARCH_RANGE_END - SEARCH_RANGE_START) // num_clients
    for i, client_socket in enumerate(LIST_OF_CLIENTS):
        client_start = SEARCH_RANGE_START + i * chunk_size
        client_end = client_start + chunk_size if i < num_clients - 1 else SEARCH_RANGE_END
        client_socket.sendall(
            f"Empieza search_range {client_start} {client_end}".encode('utf-8'))


def broadcast(message: bytes, client_socket: socket.socket) -> NoReturn:
    for client in LIST_OF_CLIENTS:
        if client != client_socket:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error sending message: {e}")
                client.close()
                remove(client)


def remove(client_socket: socket.socket) -> None:
    if client_socket in LIST_OF_CLIENTS:
        LIST_OF_CLIENTS.remove(client_socket)
        print(f"Client {client_socket.getpeername()} removed")


def handle_console_input():
    global server_running
    while True:
        command = input("Enter command: ")
        if command == "update_range":
            update_search_range()
        elif command == "exit":
            print("Shutting down server.")
            stop_other_clients(client_socket)
            server_running = False
            SERVER_SOCKET.close()
            break
        else:
            print("Unknown command.")


print(f"Server started at {IP_ADDRESS}:{PORT} and listening...")

SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER_SOCKET.bind((IP_ADDRESS, PORT))
SERVER_SOCKET.listen(MAX_CLIENTS)

try:
    threading.Thread(target=handle_console_input).start()
    while server_running:
        try:
            client_socket, client_address = SERVER_SOCKET.accept()
            LIST_OF_CLIENTS.append(client_socket)
            print(f"{client_address[0]} connected")
            start_new_thread(client_thread, (client_socket, client_address))
        except socket.error:
            if server_running:
                raise
            break
except KeyboardInterrupt:
    print("Server is shutting down.")
finally:
    for client in LIST_OF_CLIENTS:
        client.close()
    SERVER_SOCKET.close()
