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
socks = [sock1, sock2, sock3, sock4, sock5]

sock1.connect((IP, SERVER_PORTS[0]))
sock2.connect((IP, SERVER_PORTS[1]))
sock3.connect((IP, SERVER_PORTS[2]))
sock4.connect((IP, SERVER_PORTS[3]))
sock5.connect((IP, SERVER_PORTS[4]))


def talk_to_server(sock, msg):
    time.sleep(5)
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

            elif user_input[0:9] == "Operation": #Operation(put/get, key, val(only for put))
                operation = user_input[9:].split(',')
                op = operation[0].strip('(').strip()
                if op == "get" or op == "put":
                    key = operation[1].strip(')').strip()
                    if len(operation)>2:
                        val = operation[2].strip(')').strip()
                        message = f"{op} {key} {val}"
                    else: message = f"{op} {key}"
                    #At this point, can send message to server. INCOMPLETE, currently sending manually for testing
                else:
                    print("Command is used as follows: Operation(put, key, value) or Operation(get, key).")

            elif user_input[0:4] == "send": #send 'message' PID - can send to all with .
                text = user_input.split("'")[1]
                # message = f"client message: [{text}]"
                message = text
                print(f"Sending {message} to target server(s).")
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
                elif user_input[-1] == '.':
                    for sock in socks:
                        talk_to_server(sock, message)
        except (KeyboardInterrupt, SystemExit):
            sock1.close()
            sock2.close()
            sock3.close()
            sock4.close()
            os._exit(0)


threading.Thread(target=handle_input).start()
