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
            self.id = str(random())
        else:
            self.id = "开发者专属中文标识"
        self.user_identity = ["ID:" + self.id]
        self.find_server_sock = s.socket(type=s.SOCK_DGRAM)
        self.find_server_sock.bind(("0.0.0.0", 13365))
        self.tk = tk.Tk()
        self.top = tk.Toplevel(self.tk)
        self.sock = None
        self.message_entry = tk.Text(self.tk, height=15, width=60)
        tk.Label(self.tk, text="Message Entry:").place(x=0, y=0)
        self.message_entry.place(x=0, y=28)
        self.message_box = tk.Text(self.tk, height=90, width=120)
        self.found_server = tk.Text(self.top, height=50, width=130)
        tk.Label(self.top, text="Found server").place(x=0, y=125)
        self.found_server.place(x=0, y=150)
        self.message_box.place(x=0, y=305)
        tk.Label(self.tk, text="All chat message").place(x=0, y=280)
        self.tk.geometry("1000x700")
        self.top.geometry("1000x700")
        tk.Label(self.top, text="Server IP:").place(x=0, y=0)
        self.server_ip = ttk.Entry(self.top)
        self.server_ip.place(x=100, y=0)
        self.message = None
        self.old_message = None
        self.username = username
        ttk.Button(self.top, text="Connect", command=self.connect_to_server).place(x=250, y=0)
        ttk.Button(self.tk, command=self.process, text="Send").place(x=150, y=0)

    def unknown_title(self):
        data = list("#?*&%^!&$#@$##^!@#$%#@*%@#&@^!$&@#^$@#$!@$!#*@!#&!@#[]:;,.<>")
        while True:
            sleep(0.01)
            shuffle(data)
            data1 = "".join(data)
            self.tk.title(data1)
            shuffle(data)
            data2 = "".join(data)
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
            m.showinfo("INFO", "Done connected to " + self.server_ip.get())
            t.Thread(target=self.process1).start()

    def process1(self):
        while True:
            self.message = self.sock.recv(102400)
            if not self.message:
                self.sock.close()
                return
            if self.message != self.old_message:
                self.message_box.insert("insert", bz2.decompress(self.message).decode("utf-32"))
                self.old_message = deepcopy(self.message)

    def process(self):
        mess = self.message_entry.get(1.0, "end")
        message = self.username.title() + str(self.user_identity + ["Time:" + ctime()]) + ":" + mess
        self.sock.send(bz2.compress(message.encode("utf-32")))

    def start_run(self):
        t.Thread(target=self.unknown_title).start()
        t.Thread(target=self.finding_server).start()
        self.tk.mainloop()


def main():
    client = Client(input("Username:"))
    client.start_run()


if __name__ == '__main__':
    main()
