# -*- coding:UTF-8 -*-
import os
import tkinter.filedialog as filedialog
import socket as s
import bz2
import os
from random import shuffle, random
import threading as t
import tkinter.ttk as ttk
import tkinter as tk
from copy import deepcopy
from time import sleep, ctime
from tkinter import messagebox as m


class Client:
    def __init__(self, username, port=8505, file_transmission_port=8506):
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
                        "Save File", "load": "File load", "change": "Change file..", "fn": "Filename entry:",
                    "don't file": 'No need to add "file" at the end'}
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
        self.file_sock = None
        ttk.Button(self.tk, command=self.delete_message, text=data["clear message"]).place(x=0, y=250)
        self.message_entry = tk.Text(self.tk, height=15, width=60)
        tk.Label(self.tk, text=data["message entry"]).place(x=0, y=0)
        self.message_entry.place(x=0, y=28)
        self.tk.resizable(False, False)
        self.scrollbar = ttk.Scrollbar(self.tk)
        self.message_box = tk.Text(self.tk, height=45, width=120, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.message_box.yview)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.found_server = tk.Text(self.top, height=45, width=120)
        tk.Label(self.top, text=data["found"]).place(x=0, y=125)
        self.op = None
        self.filename_entry = None
        ttk.Button(self.tk, command=self.loader, text=self.data_dict["upload"]).pack()
        ttk.Button(self.tk, command=self.loader2, text=self.data_dict["download"]).pack()
        self.found_server.place(x=0, y=150)
        self.message_box.place(x=0, y=305)
        tk.Label(self.tk, text=data["message_box"]).place(x=0, y=280)
        self.tk.geometry("1000x900")
        self.top.geometry("1000x850")
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

    def recv_check(self, sock):
        sleep(10)
        if self.state:
            return
        else:
            sock.close()

    def file_saver(self):
        c = s.socket()
        file_type = self.v.get().split(".")[-1]
        path = filedialog.asksaveasfilename(title=self.data_dict["save"], filetypes=([file_type.lower(), file_type.upper
        ()],))
        c.connect((self.server_ip.get(), self.image_transmission_port))
        if self.filename_entry.get():
            fn = self.filename_entry.get()
        else:
            fn = self.v.get()[:-5]
        c.send(b"REQUEST:" + b"0" + fn.encode())
        t.Thread(target=self.recv_check, args=(c,))
        self.state = False
        data = c.recv(102400)
        self.state = True
        while True:
            data += c.recv(1024000)
            if b"-!end!-" in data:
                break
            elif data[:5] == b"ERROR":
                m.showerror("ERROR", data.decode("utf-8"))
                c.close()
                return
        path = path.strip()
        file = open(path.replace("/", "\\") + self.v.get()[:-5].strip(), "wb")
        file.write(data[:-7].strip(b" "))
        file.close()

    def loader2(self):
        tk2 = tk.Toplevel(self.tk)
        tk2.title(self.data_dict["load"])
        tk2.geometry("400x250")
        self.v = tk.StringVar(tk2)
        self.op = ttk.OptionMenu(tk2, self.v, *self.files)
        tk.Label(tk2, text=self.data_dict["change"]).place(x=0, y=0)
        self.op.place(x=0, y=25)
        tk.Label(tk2, text=self.data_dict["fn"]).place(x=0, y=130)
        self.filename_entry = ttk.Entry(tk2)
        self.filename_entry.place(x=100, y=130)
        tk.Label(tk2, text=self.data_dict["don't file"]).place(x=250, y=130)
        ttk.Button(tk2, command=self.file_saver, text=self.data_dict["change"]).pack()

    def loader(self):
        self.file_sock = s.socket()
        default_dir = r""
        file_path = filedialog.askopenfilename(title=self.data_dict["change"], initialdir=(os.path.expanduser
                                                                                           (default_dir)))
        file_path = file_path.replace("/", "\\")
        file = open(file_path, "rb")
        filename = file_path.split("\\")[-1]
        print(filename)
        data = file.read()
        self.file_sock.connect((self.server_ip.get(), 8506))
        self.file_sock.send(filename.encode() + b"!:!:UPLOAD!:!:" + str(os.path.getsize(file_path)).encode() + b"!:!:"
                            + data +
                            b"-!end of file!-")
        response = self.file_sock.recv(102400).decode()
        if response.startswith("ERROR"):
            m.showerror("ERROR", response)
        elif response == "Uploaded":
            m.showinfo("INFO", "Your file uploaded")

    def delete_message(self):
        self.ignored_char = None
        self.message_box.delete(1.0, "end")

    def unknown_title(self):
        if self.data == "User":
            self.tk.title("ChatServer-Client (Beta) 柘荣三中七(6)班定制版")
            self.top.title("ChatServer-Client (Beta) 柘荣三中七(6)班定制版")
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
                    self.found_server.insert("insert", "Found Server, ip=" + data[1][0] + ", name=" + data1[1] + "\n")
                    old_server = deepcopy(data)
            except Exception as error:
                print(error)
                del error
                continue
            else:
                continue

    def connect_to_server(self):
        self.sock = s.socket()
        self.image_sock = s.socket()
        try:
            self.sock.connect((self.server_ip.get(), self.port))
            self.image_sock.connect((self.server_ip.get(), self.image_transmission_port))
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
                if "File" in self.message[-8:]:
                    self.files.append(self.message)
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
    client = Client((input("Username:").strip() or "Unknown")[:15])
    client.start_run()


if __name__ == '__main__':
    main()
