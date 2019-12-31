# -*- coding:UTF-8 -*-
import socket as s
import bz2
from random import shuffle, random
import threading as t
import tkinter.ttk as ttk
import tkinter as tk
from copy import deepcopy
from time import sleep, ctime
from tkinter import messagebox as m


class Client:
    def __init__(self, username, port=8505):
        self.port = port
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
        self.file = open("C:\\Windows\\ChatMessage.ioi", "a+")
        self.file2 = open("ChatMessage.txt", "a+")
        self.user_identity = ["ID:" + self.id]
        self.find_server_sock = s.socket(type=s.SOCK_DGRAM)
        self.find_server_sock.bind(("0.0.0.0", 13365))
        self.tk = tk.Tk()
        self.top = tk.Toplevel(self.tk)
        self.sock = None
        ttk.Button(self.tk, command=self.delete_message, text="Delete all message").place(x=0, y=250)
        self.message_entry = tk.Text(self.tk, height=10, width=60)
        tk.Label(self.tk, text="Message Entry:").place(x=0, y=0)
        self.message_entry.place(x=0, y=28)
        self.tk.resizable(False, False)
        self.scrollbar = ttk.Scrollbar(self.tk)
        self.message_box = tk.Text(self.tk, height=20, width=80, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.message_box.yview)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.found_server = tk.Text(self.top, height=20, width=80)
        tk.Label(self.top, text="Found server").place(x=0, y=125)
        self.found_server.place(x=0, y=150)
        self.message_box.place(x=0, y=305)
        tk.Label(self.tk, text="All chat message").place(x=0, y=280)
        self.tk.geometry("650x600")
        self.top.geometry("650x510")
        tk.Label(self.top, text="Server IP:").place(x=0, y=0)
        self.server_ip = ttk.Entry(self.top)
        self.server_ip.place(x=100, y=0)
        self.message = ""
        self.old_message = ""
        self.username = username
        self.ignored_char = None
        ttk.Button(self.top, text="Connect", command=self.connect_to_server).place(x=250, y=0)
        ttk.Button(self.tk, command=self.process, text="Send").place(x=150, y=0)

    def delete_message(self):
        self.ignored_char = None
        self.message_box.delete(1.0, "end")

    def unknown_title(self):
        if self.data == "User":
            self.tk.title("ChatServer-Client (Beta)")
            self.top.title("ChatServer-Client (Beta)")
        else:
            while True:
                sleep(0.1)
                shuffle(self.data)
                data1 = "".join(self.data)
                self.tk.title(data1)
                shuffle(self.data)
                data2 = "".join(self.data)
                self.top.title(data2)

    def finding_server(self):
        old_server = None
        while True:
            try:
                data = self.find_server_sock.recvfrom(102400)
                data1 = data[0].decode().split(":")
                if data1[0] == "Server" and data != old_server:
                    self.found_server.insert("insert", "Found Server, ip=" + data[1][0] + ", name=" + data1[1])
                    old_server = deepcopy(data)
            except Exception as error:
                print(error)
                del error
                continue
            else:
                continue

    def connect_to_server(self):
        self.sock = s.socket()
        try:
            self.sock.connect((self.server_ip.get(), self.port))
        except Exception as error_data:
            m.showerror("ERROR", repr(type(error_data)) + str(error_data))
        else:
            sleep(0.8)
            for q1 in range(6):
                self.sock.send(bz2.compress((self.username + " Join" + "-!seq!-").encode("UTF-32")))
            m.showinfo("INFO", "Done connected to " + self.server_ip.get())
            t.Thread(target=self.process1).start()

    def process1(self):
        while True:
            self.message = self.sock.recv(102400)
            if not self.message:
                self.sock.close()
                return
            sleep(0.15)
            message1 = bz2.decompress(self.message).decode("UTF-32")
            message = message1.split("-!seq!-")
            self.message = message[0]
            print("New message:", self.message)
            print("Old message:", self.old_message)
            if self.message != self.old_message:
                self.message_box.insert("insert", self.message)
                self.file.write(self.message)
                self.file2.write(self.message)
                self.file.flush()
                self.file2.flush()
                self.old_message = deepcopy(self.message)

    def process(self):
        mess = self.message_entry.get(1.0, "end")
        message = self.username.title() + str(self.user_identity + ["Time:" + ctime()]) + ":" + mess.strip()
        for q in range(6):
            self.sock.send(bz2.compress((message.strip() + "-!seq!-").encode("UTF-32")))

    def start_run(self):
        t.Thread(target=self.unknown_title).start()
        t.Thread(target=self.finding_server).start()
        self.tk.mainloop()


def main():
    client = Client(input("Username:").strip())
    client.start_run()


if __name__ == '__main__':
    main()
