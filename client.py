import socket
import sys
import threading

IP = socket.gethostname()

SERVER_PORT = int(sys.argv[1])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP, SERVER_PORT))


def handle_input():
    while True:
        user_input = input()
        if user_input == "send message":
            sock.send("client message".encode())
            reply = sock.recv(1024).decode()
            print(reply)


threading.Thread(target=handle_input).start()
