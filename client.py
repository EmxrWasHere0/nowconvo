# guest.py
import socket
import threading
from encryptor import encrypt, decrypt
import sys

try:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    nickname = sys.argv[3]
except:
    HOST = input("Enter host IP: ")
    PORT = int(input("Enter host port: "))
    nickname = input("Enter your nickname")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        try:
            msg = client.recv(1024).decode()
            if msg == "":
                continue
            # Decrypt everything
            try:
                print(decrypt(msg))
            except:
                print(msg)
        except:
            break


threading.Thread(target=receive, daemon=True).start()
try:
    hostword = sys.argv[4]
except:
    hostword = input("Enter hostword: ")
client.send(hostword.encode())

while True:
    msg = input()
    if msg == "/quit":
        client.close()
        break
    full_msg = f"[{nickname}]: {msg}"
    client.send(encrypt(full_msg).encode())
