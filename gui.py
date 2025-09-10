import tkinter as tk
from tkinter import simpledialog
import subprocess

def run_host():
    hword = simpledialog.askstring("Host", "Enter your hostword:")
    if hword:
        # Runs host.py with port as argument
        subprocess.Popen(["python3", "host.py", hword], shell=False)

def run_guest():
    host_ip = simpledialog.askstring("Guest", "Enter host IP:")
    port = simpledialog.askinteger("Guest", "Enter host port:", minvalue=1, maxvalue=65535)
    nick = simpledialog.askstring("Guest", "Enter your nickname: ")
    hword = simpledialog.askstring("Guest", "Enter the hostword: ")
    if host_ip and port and nick:
        subprocess.Popen(["python3", "client.py", host_ip, str(port), nick, hword], shell=False)

root = tk.Tk()
root.title("NowConvo")
root.geometry("300x150")

tk.Button(root, text="Run as Host", width=20, command=run_host).pack(pady=20)
tk.Button(root, text="Run as Guest", width=20, command=run_guest).pack(pady=10)

root.mainloop()
