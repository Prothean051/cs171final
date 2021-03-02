import socket
import threading
import sys
import json
import os
import string
from queue import Queue
from hashlib import sha256
from secrets import choice

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

        elif user_input == "reconstruct":
            reconstruct()

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

#Queue. Stores operations on key-value store until they are added to the blockchain.
ops = Queue()
#example usage: ops.put(("put", "Joe Gaucho", "123-456-7890"))

#Key-Value Store. Using dict for now, but if disk persistency matters could use dbm.
#Key is student netID/name, value is phone number. Access using put/getStudent.
students = {}
def putStudent(key: str, value: str):
    students[key] = value
    ops.put(("put", key, value))
def getStudent(key: str):
    ops.put(("get", key))
    return students[key]

#Blockchain. Append-only chain of blocks.
chain = [] #Using list for now. Access only using appendBlock. Each block is a tuple of size 3.

def convertQueue(): #pass this as target for a thread to automatically empty queue into blockchain
    while True:
        appendBlock()

def appendBlock(): #appendBlock pops the first command from the Queue and converts it
                    #to a block. Access using threading since noncing can take a while!
    op = ops.get() #since this has no timeout, will wait until an element in queue exists
    pointer = ""
    if(len(chain)>0): 
        pointer = blockToString(chain[-1])
    hashpointer = sha256(pointer.encode()).hexdigest()
    accepted = False
    opString = ''.join(op)
    while(accepted == False): #Nonce calculated here. Length is the range of the for loop.
        nonce = ''.join(choice(string.ascii_uppercase+string.digits) for i in range(5))
        s = opString.join(nonce)
        hash = sha256(s.encode()).hexdigest()
        if(hash[-1]=='0' or hash[-1]=='1' or hash[-1]=='2'):
            accepted = True
    print("Appended", op, hashpointer, nonce) #debug print
    chain.append((op, hashpointer, nonce))

def appendBlock(op, hashpointer, nonce): #overloaded append for rebuild
    print("Appended", op, hashpointer, nonce) #debug print
    chain.append((op, hashpointer, nonce))

def blockToString(block: str):
    s = block[0] + " " + block[1] + " " + block[2]
    return s

def reconstruct(): #rebuild blockchain and keyvalue store from file
    file = open("example.txt","r")
    for line in file:
        splitline = line.split(" ")
        if(splitline[0]=="put"):
            op = splitline[0] + " " + splitline[1] + " " + splitline[2]
            students[splitline[1]] = splitline[2]
        if(splitline[0]=="get"):
            op = splitline[0] + " " + splitline[1]
        hashpointer = splitline[-2]
        nonce = splitline[-1]
        appendBlock(op, hashpointer, nonce)
    print("Blockchain rebuilt. Printing blockchain:")
    for i in chain:
        print(blockToString(i))
    print("Printing students key-val store:")
    for i in students:
        print(i, students[i])   

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


