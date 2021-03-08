import socket
import threading
import json
import time
import os

IP = socket.gethostname()

# get port numbers from config file
with open('config.json', 'r') as port_file:
    file_data = port_file.read()
PORT_OBJ = json.loads(file_data)
SERVER_PORTS = [PORT_OBJ[key] for (key, v) in PORT_OBJ.items()]


sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock5 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock1.connect((IP, SERVER_PORTS[0]))
sock2.connect((IP, SERVER_PORTS[1]))
sock3.connect((IP, SERVER_PORTS[2]))
sock4.connect((IP, SERVER_PORTS[3]))
sock5.connect((IP, SERVER_PORTS[4]))


def talk_to_server(sock, msg):
    time.sleep(2)
    sock.send(msg.encode())
    reply = sock.recv(1024).decode()
    print(reply)


def handle_input():

    while True:
        try:
            user_input = input()

            if user_input == "exit":
                sock1.close()
                sock2.close()
                sock3.close()
                sock4.close()
                os._exit(0)

            elif user_input[0:4] == "send":
                text = user_input.split("'")[1]
                message = f"client message: [{text}]"
                if user_input[-1] == '1':
                    talk_to_server(sock1, message)
                elif user_input[-1] == '2':
                    talk_to_server(sock2, message)
                elif user_input[-1] == '3':
                    talk_to_server(sock3, message)
                elif user_input[-1] == '4':
                    talk_to_server(sock4, message)
                elif user_input[-1] == '5':
                    talk_to_server(sock5, message)
        except (KeyboardInterrupt, SystemExit):
            sock1.close()
            sock2.close()
            sock3.close()
            sock4.close()
            os._exit(0)


threading.Thread(target=handle_input).start()
