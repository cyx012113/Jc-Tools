import socket
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkFont
import time
import os

class ChatServer:
    def __init__(self, master):
        self.master = master
        self.master.title("服务器 Server")
        self.setup_widgets()
        self.sock = None
        self.start = False
        self.clients = []
        self.client_names = {}  # 新增：存储客户端名称

    def setup_widgets(self):
        font = tkFont.Font(family="华文楷体", size=12)  # 设置字体和字号

        self.messages = tk.Text(self.master, state='disabled', font=font)
        self.messages.grid(row=0, column=0, columnspan=2)

        self.client_listbox = tk.Listbox(self.master, font=font)
        self.client_listbox.grid(row=0, column=2, rowspan=2)

        self.input_server = tk.Entry(self.master, font=font)
        self.input_server.grid(row=2, column=0)

        self.send_button = tk.Button(self.master, text="发送 Send", command=self.send_server_message, font=font)
        self.send_button.grid(row=3, column=0)

        self.kick_button = tk.Button(self.master, text="打开 0x13", command=self._18_plus, font=font)
        self.kick_button.grid(row=3, column=1)

        tk.Label(self.master, text="服务器IP地址 Server IP address: " + str(socket.gethostbyname(socket.gethostname())), font=font).grid(row=1, column=2)

        self.start_button = tk.Button(self.master, text="启动服务器 Start server", command=self.start_server, font=font)
        self.start_button.grid(row=1, column=0)

        self.master.bind("<Return>", self.send_server_message_event)

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_server(self):
        if self.start:
            messagebox.showerror("服务器已启动 The server is up", "服务器已启动，请勿重复启动服务器！The server has been started, do not start the server repeatedly!")
            return
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(('0.0.0.0', 8888))
            self.sock.listen(1000)
            self.start = True
            threading.Thread(target=self.accept_connections, daemon=True).start()
            self.start = True
        except OSError as e:
            messagebox.showerror("启动错误 Start Error", f"无法启动服务器: {e}")

    def accept_connections(self):
        while True:
            if not self.start:
                os._exit(0)
            client, addr = self.sock.accept()
            self.clients.append(client)
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
            self.update_client_list()

    def handle_client(self, client):
        # 无限循环，持续处理客户端消息
        while True:
            try:
                # 从客户端接收最多1024字节的数据
                data = client.recv(1024)
                # 将接收到的字节数据解码为UTF-8字符串
                message = data.decode('utf-8')
                # 如果接收到的消息不为空
                if message.startswith("/name:"):
                    # 将客户端名称添加到客户端名称字典中
                    self.client_names[client] = message[6:]
                    # 更新客户端列表显示
                    self.update_client_list()
                elif message:
                    # 将消息框设置为可编辑状态
                    self.messages.configure(state='normal')
                    # 在消息框的末尾插入接收到的消息，并添加换行符
                    self.messages.insert(tk.END, message + '\n')
                    # 将消息框设置为不可编辑状态
                    self.messages.configure(state='disabled')
                    # 滚动消息框到最底部，显示最新消息
                    self.messages.yview(tk.END)
                    with open("log.txt", "a+") as f:
                        f.write(message + '\n')
            except socket.error as e:
                # 如果发生socket错误，从客户端列表中移除该客户端
                self.clients.remove(client)
                # 如果客户端在客户端名称字典中，删除该客户端的条目
                if client in self.client_names:
                    del self.client_names[client]
                # 更新客户端列表显示
                self.update_client_list()
                # 退出循环，结束当前客户端的处理
                break

    def update_client_list(self):
        self.client_listbox.delete(0, tk.END)
        for name in self.client_names.values():
            self.client_listbox.insert(tk.END, name)

    def send_server_message_event(self, event=None):
        self.send_server_message()

    def send_server_message(self):
        message = self.input_server.get()
        if message.startswith("/cmd"):
            select_user = self.get_selected_user()
            for client, name in self.client_names.items():
                if name == select_user:
                    client.sendall(message.encode('utf-8'))
            self.messages.configure(state='normal')
            self.messages.insert(tk.END, message + '\n')
            self.messages.configure(state='disabled')
            self.messages.yview(tk.END)
            self.input_server.delete(0, tk.END)
            return
        message = f"server: {message}"
        for client in self.clients:
            client.sendall(message.encode('utf-8'))
        self.messages.configure(state='normal')
        self.messages.insert(tk.END, message + '\n')
        self.messages.configure(state='disabled')
        self.messages.yview(tk.END)
        self.input_server.delete(0, tk.END)

    def _18_plus(self):
        # 调用 get_selected_user 方法获取当前选定的用户
        selected_user = self.get_selected_user()  # 假设有一个方法获取选定的用户
        for client, name in self.client_names.items():
            if name == selected_user:
                client.sendall(f"{selected_user} 已被18+。{selected_user} ,you have been 18+ed.".encode('utf-8'))

    def on_close(self):
        if self.sock:
            self.start = False  # 新增：标记服务器已停止
            for client in self.clients:
                client.sendall(b"/quit")
                client.close()
        self.master.destroy()
        os._exit(0)

    def get_selected_user(self):
        try:
            # 获取当前选定的用户
            selected_index = self.client_listbox.curselection()
            if selected_index:
                return self.client_listbox.get(selected_index)
            else:
                messagebox.showwarning("选择错误", "请先选择一个用户！")
                return None
        except Exception as e:
            messagebox.showerror("错误", f"获取选定用户时出错: {e}")
            return None

if __name__ == '__main__':
    root = tk.Tk()
    server = ChatServer(root)
    root.mainloop()
