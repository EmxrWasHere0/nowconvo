# host.py
import socket
import threading
from encryptor import encrypt, decrypt

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000
connections = []
hostword = input("Set your hostword: ")

def handle_client(conn, addr):
    conn.send("Enter hostword: ".encode())
    entered = conn.recv(1024).decode().strip()
    if entered != hostword:
        conn.send("Wrong hostword. Disconnecting.".encode())
        conn.close()
        return
    conn.send("Connected to host!\n".encode())
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            msg = decrypt(data)                  # Decrypt guest message
            print(f"[Guest {addr}]: {msg}")      # Display on host CLI
            chat_log.append(f"[Guest {addr}]: {msg}")  # Add to host chat log
            broadcast(data, conn)                # Send encrypted message to other clients
        except:
            break
    conn.close()


def broadcast(message, sender_conn):
    for conn in connections:
        if conn != sender_conn:
            try:
                conn.send(message.encode())
            except:
                pass

def accept_connections():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Hosting chat on port {PORT}...")
    while True:
        conn, addr = server.accept()
        connections.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

threading.Thread(target=accept_connections, daemon=True).start()

chat_log = []

print("Type your messages below. /end to close chat.")
# inside the main loop for host input
while True:
    msg = input()
    if msg == "/end":
        for conn in connections:
            try:
                conn.send("Session ended by host.".encode())
                conn.close()
            except:
                pass
        with open("chat_log.txt", "w") as f:
            for m in chat_log:
                f.write(m + "\n")
        print("Session ended. Chat saved to chat_log.txt")
        break

    full_msg = f"[Host]: {msg}"          # Add header
    encrypted = encrypt(full_msg)        # Encrypt full message
    chat_log.append(full_msg)            # Add to log
    broadcast(encrypted, None)           # Send to all clients

