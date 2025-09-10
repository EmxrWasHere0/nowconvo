# guest.py
import socket
import threading
from encryptor import encrypt, decrypt

HOST = input("Enter host IP: ")
PORT = int(input("Enter host port: "))
nickname = input("Enter your nickname: ")

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

hostword = input("Enter hostword: ")
client.send(hostword.encode())

while True:
    msg = input()
    if msg == "/quit":
        client.close()
        break
    full_msg = f"[{nickname}]: {msg}"
    client.send(encrypt(full_msg).encode())
