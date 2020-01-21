# -*- coding:UTF-8 -*-
import socket as s
import Client
from random import random
import tkinter.ttk as ttk
import tkinter as tk
from copy import deepcopy


class Client1(Client.Client):
    def __init__(self, username, port=8505, file_transmission_port=8506):
        # super().__init__(username, port, file_transmission_port)
        self.state = None
        self.port = port
        self.data_dict = {}
        self.image_transmission_port = file_transmission_port
        self.files = []
        try:
            data = open("IDENTITY").read()
            if data != "!$##@@#!$#@###":
                raise FileNotFoundError
        except FileNotFoundError:
            self.data = "User"
            self.id = str(random())
        else:
            self.id = "开发者专属中文标识"
            self.data = list("#?*&%^!&$#@$##^!@#$%#@*%@#&@^!$&@#^$@#$!@$!#*@!#&!@#[]:;,.<>")
        try:
            data = open("Language.ini").read()
            data = eval(data)
            try:
                ignored = data["send"]
                ignored = data["message_box"]
                ignored = data["clear message"]
                ignored = data["connect"]
                ignored = data["found"]
                ignored = data["message entry"]
                ignored = data["server ip"]
                ignored = data["upload"]
                ignored = data["download"]
                ignored = data["get"]
                ignored = data["fn"]
                self.data_dict = deepcopy(data)
                del ignored
            except KeyError:
                raise FileNotFoundError
            except Exception:
                raise FileNotFoundError

        except FileNotFoundError:
            data = {"send": "Send", "message_box": "All chat message", "clear message": "Delete all message",
                    "connect": "Connect", "found": "Found server:", "message entry": "Message entry", "server ip":
                        "Server IP:", "upload": "Upload...", "download": "Download...", "get": "Get file...", "save":
                        "Save File", "load": "File load", "change": "Change file..", "fn": "Filename entry:"}
            print("File not found")
            self.data_dict = deepcopy(data)

        self.file = open("C:\\Windows\\ChatMessage.ioi", "a+")
        self.file2 = open("ChatMessage.txt", "a+")
        self.user_identity = ["ID:" + self.id]
        self.find_server_sock = s.socket(type=s.SOCK_DGRAM)
        self.find_server_sock.bind(("0.0.0.0", 13365))
        self.tk = tk.Tk()
        self.top = tk.Toplevel(self.tk)
        self.v = None
        self.sock = None
        ttk.Button(self.tk, command=self.delete_message, text=data["clear message"]).place(x=0, y=250)
        self.message_entry = tk.Text(self.tk, height=10, width=60)
        tk.Label(self.tk, text=data["message entry"]).place(x=0, y=0)
        self.message_entry.place(x=0, y=28)
        self.tk.resizable(False, False)
        self.scrollbar = ttk.Scrollbar(self.tk)
        self.message_box = tk.Text(self.tk, height=20, width=80, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.message_box.yview)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.found_server = tk.Text(self.top, height=25, width=80)
        tk.Label(self.top, text=data["found"]).place(x=0, y=125)
        self.op = None
        self.filename_entry = None
        ttk.Button(self.tk, command=self.loader, text=self.data_dict["upload"]).place(x=450, y=0)
        ttk.Button(self.tk, command=self.loader2, text=self.data_dict["download"]).place(x=450, y=35)
        self.found_server.place(x=0, y=150)
        self.message_box.place(x=0, y=305)
        tk.Label(self.tk, text=data["message_box"]).place(x=0, y=280)
        self.tk.geometry("650x600")
        self.top.geometry("650x510")
        self.image_sock = None
        tk.Label(self.top, text=data["server ip"]).place(x=0, y=0)
        self.server_ip = ttk.Entry(self.top)
        self.server_ip.place(x=100, y=0)
        self.message = ""
        self.old_message = ""
        self.username = username
        self.ignored_char = None
        ttk.Button(self.top, text=data["connect"], command=self.connect_to_server).place(x=250, y=0)
        ttk.Button(self.tk, command=self.process, text=data["send"]).place(x=150, y=0)


def main():
    client = Client1((input("Username:").strip() or "Unknown")[:15])
    client.start_run()


if __name__ == '__main__':
    main()
