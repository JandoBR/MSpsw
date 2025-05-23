import socket
import sys
from Crypto.Hash import SHA3_512
import threading
import logging

stop_flag = False
logging.basicConfig(filename='contrasenas.log', level=logging.INFO)
logging.info('Script started executing...')


def busqueda(salt: str, pwd: str, start: int, end: int, socket1: socket.socket):
    logging.info("Function initialized")
    logging.info(start)
    logging.info(end)
    global stop_flag
    salt_b = bytes.fromhex(salt)
    with open("rockyou.txt", "r", encoding='latin-1') as file:
        read_lines = file.readlines()


    for i in range(start, end):
        password = read_lines[i]
        print(password)
        if stop_flag:
            break
        password = password.strip()
        password_b = bytes(password, "latin-1")

        for pepper in range(0, 256):
            H = SHA3_512.new()

            H.update(password_b)

            pepper_b = pepper.to_bytes(1, "big")
            H.update(pepper_b)

            H.update(salt_b)

            pwd_h = H.hexdigest()

            if pwd == pwd_h:
                message = f"password_found, {password}"
                socket1.send(bytes(message, "latin-1"))
                sys.stdout.write(message)
                sys.stdout.flush()
                print(password)
                stop_flag = True
                logging.info('Script finished executing.')
                break


username, salt, pwd = ('ballestasaj', "13ce5d97af743ba0b8f211b9c31e3f8f",
                       "a45ee47e64c9bd1210c444124ee183befc26085f7eb9c0cc927dca7f09d017edcfa6bcd0be1630b08dea659dd2d30866647175a4d69fac4a688438213244d2a0")

SERVER_IP_ADDRESS = "192.168.1.8"
SERVER_PORT = 8081

socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_.connect((SERVER_IP_ADDRESS, SERVER_PORT))

try:
    while True:
        stream_list = [sys.stdin, socket_]
        for stream in stream_list:
            if stream == socket_:
                try:
                    message = socket_.recv(2048)
                    if not message:
                        raise ConnectionResetError

                    # Decode the received bytes to a string
                    message = message.decode('latin-1')
                    if message.startswith("Empieza"):
                        parts = message.split()
                        if len(parts) == 4 and parts[1] == "search_range":
                            start = int(parts[2])
                            end = int(parts[3])
                            threads = []
                            chunk_size = (end - start) // 4

                            for i in range(4):
                                client_start = start + i * chunk_size
                                client_end = client_start + chunk_size if i < 3 else end
                                thread = threading.Thread(target=busqueda, args=(
                                    salt, pwd, client_start, client_end, socket_))
                                threads.append(thread)
                                thread.start()

                    if message.startswith("password_found"):
                        stop_flag = True
                        
                except ConnectionResetError:
                    stop_flag = True
                    print("Server connection was closed. Stopping client.")
                    socket_.close()
                    break
except KeyboardInterrupt:
    stop_flag = True
    print("Client interrupted and stopped.")
    socket_.close()
