import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from toga import dialogs
import setproctitle
import sys
import socket
import threading
import os
from pathlib import Path
import nowconvo
import importlib.resources as pkg_resources

def encrypt(text):
    encrypted = ""
    for c in text:
        if c.isalpha():
            # Shift character to a Unicode symbol starting from 0x2600 (☀)
            offset = 0x2600
            encrypted += chr(offset + ord(c.lower()) - ord('a') + (0 if c.islower() else 26))
        elif c.isdigit():
            # Numbers start at 0x1F100
            encrypted += chr(0x1F100 + int(c))
        else:
            # Keep punctuation/space as-is
            encrypted += c
    return encrypted

def decrypt(text):
    decrypted = ""
    for c in text:
        code = ord(c)
        # Letters lowercase 0x2600-0x2619
        if 0x2600 <= code <= 0x2619:
            decrypted += chr((code - 0x2600) + ord('a'))
        # Letters uppercase 0x261A-0x2633
        elif 0x261A <= code <= 0x2633:
            decrypted += chr((code - 0x261A) + ord('A'))
        # Numbers 0x1F100-0x1F109
        elif 0x1F100 <= code <= 0x1F109:
            decrypted += str(code - 0x1F100)
        else:
            decrypted += c
    return decrypted

connections = []
chat_log = []
server_thread = None
client_thread = None
client_socket = None
nickname = ""
hostword = ""
host_username = ""
chat_display = None
app_instance = None

def handle_client(conn, addr):
    global connections, chat_log
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
            msg = decrypt(data)
            full_msg = f"[{addr}]: {msg}"
            chat_log.append(full_msg)
            broadcast(data, conn)
            if app_instance and chat_display:
                app_instance.loop.call_soon_threadsafe(lambda: setattr(chat_display, 'value', chat_display.value + full_msg + "\n"))
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
    global connections
    HOST = '0.0.0.0'
    PORT = 5000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    while True:
        conn, addr = server.accept()
        connections.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def receive():
    global client_socket
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg == "":
                continue
            try:
                print(decrypt(msg))
            except:
                pass
        except:
            break

def open_chat_window(app, mode):
    global chat_display, app_instance
    app_instance = app
    chat_window = toga.Window(title=f"Chat - {mode}", size=(600,400))
    box = toga.Box(style=Pack(direction=COLUMN, margin=10))
    chat_display = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))
    msg_input = toga.TextInput(placeholder="Type your message...", style=Pack(flex=0))
    def send_msg(_):
        msg = msg_input.value
        if msg:
            if mode == "Host":
                full_msg = f"[{host_username}]: {msg}"
                encrypted = encrypt(full_msg)
                chat_log.append(full_msg)
                broadcast(encrypted, None)
                chat_display.value += full_msg + "\n"
            else:
                full_msg = f"[{nickname}]: {msg}"
                client_socket.send(encrypt(full_msg).encode())
                chat_display.value += full_msg + "\n"
            msg_input.value = ""
    send_button = toga.Button("Send", on_press=send_msg, style=Pack(width=100))
    input_box = toga.Box(style=Pack(direction="row"))
    input_box.add(msg_input)
    input_box.add(send_button)
    box.add(chat_display)
    box.add(input_box)
    chat_window.content = box
    app.windows.add(chat_window)
    chat_window.show()


if sys.platform in ["win32","linux","darwin"]:
    setproctitle.setproctitle("NowConvo")
else:
    pass

def host(widget):
    global hostword, server_thread
    popup = toga.Window(title=("Host a Room"),size=(400,200))
    box = toga.Box(style=Pack(direction=COLUMN, margin=10, align_items="center"))
    txt = toga.Label("Hostword",style=Pack(margin=5, text_align="center"))
    inp = toga.TextInput(placeholder="Enter your hostword...",width=150,margin=5)
    txu = toga.Label("Username",style=Pack(margin=5, text_align="center"))
    usr = toga.TextInput(placeholder="Enter your username...",value=socket.gethostname(),width=150,margin=5)
    def submit(_):
        global hostword, server_thread, host_username
        hostword = inp.value
        host_username = usr.value
        server_thread = threading.Thread(target=accept_connections, daemon=True)
        server_thread.start()
        open_chat_window(widget.app, "Host")
        popup.close()
    butt = toga.Button("Start Hosting",on_press=submit,style=Pack(width=150,margin=5))
    box.add(txt)
    box.add(inp)
    box.add(txu)
    box.add(usr)
    box.add(butt)
    popup.content = box
    widget.app.windows.add(popup)
    popup.show()

def jn(widget):
    global client_thread, client_socket, nickname, hostword
    popup = toga.Window(title=("Join a Room"),size=(400,300))
    box = toga.Box(style=Pack(direction=COLUMN, margin=10, align_items="center"))
    txt1 = toga.Label("Host IP",style=Pack(margin=5, text_align="center"))
    inp1 = toga.TextInput(placeholder="Enter host IP...",width=150,margin=5)
    txt2 = toga.Label("Host Port",style=Pack(margin=5, text_align="center"))
    inp2 = toga.TextInput(placeholder="Enter host port...",value="5000",width=150,margin=5)
    txt3 = toga.Label("Username",style=Pack(margin=5, text_align="center"))
    inp3 = toga.TextInput(placeholder="Enter your username...",value=socket.gethostname(),width=150,margin=5)
    txt4 = toga.Label("Hostword",style=Pack(margin=5, text_align="center"))
    inp4 = toga.TextInput(placeholder="Enter hostword...",width=150,margin=5)
    def submit(_):
        global client_thread, client_socket, nickname, hostword
        HOST = inp1.value
        PORT = int(inp2.value)
        nickname = inp3.value
        hostword = inp4.value
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        client_socket.send(hostword.encode())
        client_thread = threading.Thread(target=receive, daemon=True)
        client_thread.start()
        open_chat_window(widget.app, "Client")
        popup.close()
    butt = toga.Button("Connect",on_press=submit,style=Pack(width=150,margin=5))
    box.add(txt1)
    box.add(inp1)
    box.add(txt2)
    box.add(inp2)
    box.add(txt3)
    box.add(inp3)
    box.add(txt4)
    box.add(inp4)
    box.add(butt)
    popup.content = box
    widget.app.windows.add(popup)
    popup.show()

def end(widget):
    sys.exit()

class NowConvo(toga.App):
    def startup(self):
        main_box = toga.Box(style=Pack(direction=COLUMN, margin=10, align_items="center"))

        # Add a button instead of a menu command
        img = toga.Image("resources/nowconvo.png")
        imgs = toga.ImageView(img,style=Pack(width=200,height=200))
        main_box.add(imgs)

        create = toga.Button("Host a Room",on_press=host,style=Pack(width=150, margin=5))
        main_box.add(create)

        join = toga.Button("Join a Room",on_press=jn,style=Pack(width=150, margin=5))
        main_box.add(join)

        ext = toga.Button("Exit",on_press=end,style=Pack(width=150,margin=25))
        main_box.add(ext)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

def main():
    ICON = pkg_resources.files(nowconvo) / "icon.png"
    return NowConvo(
        icon=ICON
    )
