# -*- coding:UTF-8 -*-
import threading as t
import socket as s
from random import random
from time import *
import sys
import bz2
from copy import *
# from typing import Any, Tuple
import tkinter.messagebox as m
from time import sleep
import time


class ChatServer:
    def __init__(self, port, address, server_name, max_file_size, log_file_route):
        self.connect_number = 0
        self.max_file_size = max_file_size
        self.thread_number = 0
        self.log_file_route = log_file_route
        self.files = []
        self.state = False
        self.file = open("ChatMessages.txt", "a+", encoding="utf-8")
        self.get_file_sock = s.socket()
        self.get_file_sock.bind(("0.0.0.0", 8506))
        self.get_file_sock.listen(75)
        self.check_sock = s.socket()
        self.send_message_state = []
        self.users = []
        self.baned_ip = []
        self._file_lock = t.Lock()
        self.ban_ip = None
        self._lock = t.Lock()
        self.server_name = server_name
        self.used_name = []
        self.address = address
        self.new_message = None
        self.cmd = {"IP": "", "cmd": ""}
        self._number = 0
        self.port = port
        self.old_message = None
        self.log_error = False
        if self.log_file_route:
            self.writer = self.log_writer(file_route=self.log_file_route)
        else:
            self.writer = self.log_writer()
        next(self.writer)
        self.writer.send("Server opened")

    def log_writer(self, file_route="Server log.log"):
        file = None
        if not self.log_error:
            try:
                file = open(file_route, encoding="utf-8", mode="a+")
            except (FileNotFoundError, OSError) as error_data:
                m.showerror("Log Write ERROR", (repr(type(error_data) + str(error_data))))
                self.log_error = True
        else:
            file = open("Client log.log", "a+", encoding="utf-8")
        while True:
            content = yield None
            file.write(ctime() + ":" + content + "\n")
            file.flush()

    def check_connect_timeout(self, sock):
        time.sleep(10)
        if self.state:
            return
        else:
            sock[0].close()
            return

    def file_send(self):
        while True:
            self.state = False
            sock = self.get_file_sock.accept()
            if sock[1][0] in self.baned_ip:
                sock[0].send("ERROR:你已被封禁".encode())
                sock[0].close()
                continue
            self.writer.send("New file transmission connect" + sock[1][0])
            print("New file transmission connect")
            t.Thread(target=self.check_connect_timeout, args=(sock,)).start()
            try:
                filename = sock[0].recv(102400)
            except OSError:
                print("time out")
                continue
            self.state = True
            print("filename.split(b':')[1]:", filename.split(b":")[1])
            print(filename.split(b":")[0])
            try:
                if filename[:8] == b"REQUEST:":
                    try:
                        data = open(".\\data\\" + filename[8:].decode(), "rb").read()
                    except FileNotFoundError:
                        sock[0].send(b"ERROR not found")
                        self.writer.send(sock[1][0] + "Request File:" + filename[8:].decode() + ", Not found")
                    else:
                        self.writer.send(sock[1][0] + "Successfully request file:" + filename[8:].decode())
                        sock[0].sendall(data + b"-!end!-")
                        sock[0].close()
                        continue
                elif filename.split(b"!:!:")[1] == b"UPLOAD":
                    filename = filename.split(b"!:!:")
                    self.writer.send(sock[1][0] + "Upload file:" + filename[1].decode())
                    if int(filename[2]) > self.max_file_size:
                        self.writer.send(sock[1][0] + ":Upload File size too big")
                        for x in range(6):
                            sock[0].send(b"ERROR File size must > " + str(self.max_file_size).encode() + b"B")
                            sock[0].close()
                            continue
                    file_data = filename[3]
                    self.writer.send(sock[1][0] + "Successfully upload file")
                    for x in range(6):
                        sock[0].send(b"Uploaded")
                    if b"-!end of file!-" not in file_data:
                        print("data has more")
                        while True:
                            file_data += sock[0].recv(1024000)
                            if b"-!end of file!-" in file_data:
                                print("break")
                                break
                    print("processing data")
                    message = (time.ctime() + " " + filename[0].decode() + "(" + sock[1][0] + ")" + "." + filename
                    [0].
                               decode().split(".")[-1]).strip() + "File"
                    message = message.strip()
                    message = message.replace(":", " ")
                    message = message.replace("(", "I")
                    message = message.replace(")", "P")
                    message = message.replace(" ", "")
                    file = open(".\\data\\0" + message[:-4], "wb")
                    file.write(file_data[:-15])
                    file.close()
                    print("send message")
                    self._lock.acquire()
                    self.new_message = deepcopy(message + "\n")
                    self._lock.release()
                else:
                    self.writer.send(sock[1][0] + ":Dont know how to continue:" + filename.decode())
                    sock[0].send(b"ERROR403")
                    sock[0].close()
                    continue
            except Exception as error_data:
                print(type(error_data)(str(error_data)))

    def check_message_send(self):
        while True:
            if self._lock.locked():
                sleep(2.5)
                self._lock.release()
            if not all(self.send_message_state):
                self._lock.acquire()
                sleep(5)
            else:
                self._lock.release()

    def enter_command(self):
        while True:
            command = input("Command:")
            comm = command.split(maxsplit=2)
            if comm and comm[0] in ["ban", "un_ban", "show_baned", "cmd"]:
                if comm[0] == "ban":
                    self.ban_ip = comm[1]
                    self.baned_ip.append(comm[1])
                elif comm[0] == "un_ban":
                    self.ban_ip = None
                    try:
                        self.baned_ip.remove(comm[1])
                    except (IndexError, ValueError):
                        print("IP isn't in baned ip")
                elif comm[0] == "show_baned":
                    print(self.baned_ip)
                # elif comm[0] == "cmd":
                #   self.cmd["IP"] = comm[1]
                #   self.cmd["cmd"] = comm[2]

            else:
                print("Unknown command")
                self.writer.send("Enter Unknown Command:" + command)
                continue
            self.writer.send("Enter command:" + command)

    def processing_communication(self, socket_, name1):
        """Broadcasting information to users
        user <- data <- server

        """
        index = None
        self.thread_number += 1
        while True:
            if name1 == "RENAME FAILED":
                ran = random()
                if ran in self.used_name:
                    continue
                else:
                    break
            else:
                break
        self.send_message_state.append(name1)
        try:
            index = self.send_message_state.index(name1)
        except ValueError:
            self.writer.send(socket_[1][0] + "Connect Error")
            socket_[0].send(bz2.compress("你的连接存在错误, 请重新连接(connect wrong happen, please try again)"))
            socket_[0].close()
        self.connect_number += 1
        # active count return active count(len(t.enumerate()))
        self.new_message = ""
        self.old_message = ""
        while True:
            self.send_message_state[index] = False
            try:
                if self.new_message.strip() != self.old_message.strip():
                    for q1 in range(6):
                        socket_[0].send(bz2.compress((self.new_message + "-!seq!-").encode("UTF-32")))
                    self.old_message = deepcopy(self.new_message)
                    self.send_message_state[index] = True
                    # 释放 Global Interpreter Lock
                    self._lock.acquire()
                    self._lock.release()
                if socket_[1][0] == self.ban_ip:
                    try:
                        print(socket_[1][0] + " thread2 closed")
                        for q1 in range(6):
                            socket_[0].send(bz2.compress("友好的中文提示:你已被踢出服务器, 并且在管理员没有取消封杀的情况下无法再次加入".encode("utf-32")))
                        socket_[0].close()
                        self.writer.send("Baned IP:" + socket_[1][0] + ", Disconnected")
                    except OSError:
                        self.connect_number -= 1
                        self.send_message_state[index] = True
                        return
                    return
                # elif self.cmd["IP"] == socket_[1][0]:
                #   socket_[0].send(bz2.compress(("Command:" + self.cmd["cmd"]).encode("utf-32")))
                #   self.cmd = {"IP": "", "cmd": ""}
            except ConnectionResetError:
                self.writer.send("Disconnected from " + socket_[1][0])
                self.send_message_state[index] = True
                self.connect_number -= 1
                return

    def radio_broadcast(self):
        sock = s.socket(type=s.SOCK_DGRAM)
        sock.setsockopt(s.SOL_SOCKET, s.SO_BROADCAST, 1)
        sock.bind(("0.0.0.0", 18500))
        print("Start sending broadcast packets")
        self.writer.send("Start sending broadcast packets")
        while True:
            sock.sendto(("Server:" + self.server_name).encode(), (self.address, 13365))
            sleep(5)

    def processing_communication2(self, socket_):
        message1 = ""
        """

        user -> data -> server

        """
        self.connect_number += 1
        while True:
            try:
                if socket_[1][0] == self.ban_ip:
                    print(socket_[1][0] + " thread1 closed")
                    self.connect_number -= 1
                    socket_[0].close()
                    return
                message1 = socket_[0].recv(102400)
                message1 = bz2.decompress(message1).decode("utf-32")
                if not message1:
                    self.connect_number -= 1
                    return
                if message1.startswith("Command Response:"):
                    response = deepcopy(message1)
                    print(socket_[1][0] + response)
                    continue
                message = message1.split("-!seq!-")
                if len(message) >= 2:
                    if message[0] == message[1]:
                        message = message[0]
                    else:
                        message = message[0]
                else:
                    message = message[0]
                message += ("(" + socket_[1][0] + ")\n")
            except OSError:
                self.connect_number -= 1
                print("INFO:recv the wrong message,from" + socket_[1][0])
                print("The wrong message is:", message1[:20] + "..." + message1[-20:])
                self.writer.send("Method 'recv':wrong message:" + message1[:20] + "..." + message1[-20:] + ", from " + socket_[1][0])
                self.writer.send(socket_[1][0] + "Closed")
                return
            except ConnectionResetError:
                self.connect_number -= 1
                print(socket_[1][0] + "Closed")
                return
            except Exception as error_data:
                print(type(error_data), str(error_data))
                self.connect_number -= 1
                return
            self._lock.acquire()
            self.new_message = deepcopy(message)
            self._lock.release()
            self._file_lock.acquire()
            self.file.write(message)
            self.file.flush()
            self._file_lock.release()

    def processing_connections(self):
        server = s.socket()
        conn_num = int(input("please input max connects(1-999999999):" or "10000"))
        t.Thread(target=self.enter_command).start()
        t.Thread(target=self.radio_broadcast).start()
        t.Thread(target=self.file_send).start()
        while True:
            try:
                print("No connection".center(79, "*"))
                server.bind(("0.0.0.0", self.port))
                server.listen(conn_num)
            except OSError:
                self.writer.send("Error in line 298:Port 8000 is using")
                print("Error:Port 8000 is using")
                input()
                sys.exit()
            except Exception as error_data:
                print(type(error_data), error_data)
            else:
                break

        while True:
            try:
                data_socket = server.accept()
                if data_socket[1][0] in self.baned_ip:
                    self.writer.send("baned IP" + data_socket[1][0] + "try connect to server.")
                    data_socket[0].send(bz2.compress("You Can't join us".encode("utf-32")))
                    data_socket[0].close()
                    self.writer.send("Disconnected baned IP" + data_socket[1][0])
                    del data_socket
                    continue
                self.writer.send("New connect:" + data_socket[1][0] + ",Port" + str(data_socket[1][1]))
                print("INFO:Connect from:" + data_socket[1][0] + ", port:" + str(data_socket[1][1]))
                self.users.append(data_socket[1])
                ran1 = str(random())
                if ran1 not in self.used_name:
                    ran = deepcopy(ran1)
                else:
                    ran = "RENAME FAILED"
                print(1)
                t.Thread(target=self.processing_communication, args=(data_socket, ran)).start()
                print(2)
                t.Thread(target=self.processing_communication2, args=(data_socket,)).start()
                print(3)
            except (TypeError, ValueError):
                self.writer.send("Error in line 322:TypeError or ValueError")
                print("please input again")
                continue
            self.users.append(data_socket[1][0])
            print("New connect:", data_socket[1][0])
            print("Connection Number:", self.connect_number // 2)
            t.Thread(target=self.processing_communication, args=(data_socket, ran)).start()
            t.Thread(target=self.processing_communication2, args=(data_socket,)).start()


def main():
    radio_address = input("Please enter radio broadcast address:")
    sn = input("Please enter the server name:")[:30]
    file_size = int(input("Please input max upload file size(B):"))
    log_file_route = input("Please enter the log file save route:")
    server = ChatServer(8505, radio_address, sn, file_size, log_file_route)
    server.processing_connections()


if __name__ == '__main__':
    main()
