#!/usr/bin/env python3
from queue import Queue
from hashlib import sha256
from secrets import choice
from threading import Thread
import string
import time

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

if __name__ == "__main__":
    reconstruct()
    print("Blockchain rebuilt. Printing blockchain:")
    for i in chain:
        print(blockToString(i))
    print("Printing students key-val store:")
    for i in students:
        print(i, students[i])
    
