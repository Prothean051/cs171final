import socket
import threading
import sys
import json
import os

CONNECTED = False
IP = socket.gethostname()
PROCESS_ID = sys.argv[1]

# get port numbers from config file
with open('config.json', 'r') as port_file:
    file_data = port_file.read()
all_ports = json.loads(file_data)
other_ports = [all_ports[key] for (key, v) in all_ports.items() if PROCESS_ID != key]
MY_PORT = all_ports[PROCESS_ID]
PORT_1 = other_ports[0]
PORT_2 = other_ports[1]
PORT_3 = other_ports[2]
PORT_4 = other_ports[3]

# create sockets for this server & other servers
my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def handle_client(sock, address):
    print(f"Accepted connection from {address}")
    while True:
        try:
            data = sock.recv(1024).decode()
        except socket.error as e:
            sock.close()
            break
        if not data:
            sock.close()
            break
        print(f"Received: {data}")
        if data[0:6] == 'client':
            sock.send(f"Reply from server {PROCESS_ID}".encode())


def handle_input():
    global CONNECTED

    while True:
        user_input = input()
        if user_input == "exit":
            my_sock.close()
            sock1.close()
            sock2.close()
            sock3.close()
            sock4.close()
            os._exit(0)

        elif not CONNECTED and user_input == "connect":
            CONNECTED = True

            sock1.connect((IP, PORT_1))
            sock2.connect((IP, PORT_2))
            sock3.connect((IP, PORT_3))
            sock4.connect((IP, PORT_4))

        elif CONNECTED and user_input[0:7] == "sendall":  # send all '[message goes in here]'
            m = user_input.split("'")[1]
            message = f"[{m}] from P{PROCESS_ID}"
            sock1.send(message.encode())
            sock2.send(message.encode())
            sock3.send(message.encode())
            sock4.send(message.encode())


# thread working on std input
input_thread = threading.Thread(daemon=True, target=handle_input)
input_thread.start()


my_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_sock.bind((IP, MY_PORT))
my_sock.listen()

while True:

    try:
        stream, addr = my_sock.accept()
        threading.Thread(daemon=True, target=handle_client, args=(
            stream, addr)).start()
    except (KeyboardInterrupt, SystemExit):
        my_sock.close()
        sock1.close()
        sock2.close()
        sock3.close()
        sock4.close()
        os._exit(0)


