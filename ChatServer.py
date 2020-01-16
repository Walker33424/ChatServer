# -*- coding:UTF-8 -*-
import threading as t
import socket as s
from random import random
import sys
import bz2
from copy import *
# from typing import Any, Tuple
from time import sleep
import time


class ChatServer:
    def __init__(self, port, address, server_name, max_file_size):
        self.connect_number = 0
        self.max_file_size = max_file_size
        self.thread_number = 0
        self.files = []
        self.state = False
        self.file = open("ChatMessages.txt", "a+")
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
        self._number = 0
        self.port = port
        self.old_message = None

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
            t.Thread(target=self.check_connect_timeout, args=(sock,)).start()
            try:
                filename = sock[0].recv(102400)
            except OSError:
                continue
            self.state = True
            print(filename)
            print("filename[8:]:", filename[8:])
            print(filename[:8])
            if filename[:8] == b"REQUEST:":
                try:
                    data = open(".\\data\\" + filename[8:].decode(), "rb").read()
                except FileNotFoundError:
                    sock[0].send(b"ERROR not found")
                else:
                    sock[0].sendall(data + b"-!end!-")
                    sock[0].close()
                    continue
            elif filename[10:17] == b"UPLOAD:":
                if b"-!end of file!-" not in filename:
                    while True:
                        filename += sock[0].recv(102400)
                        if b"-!end of file!-" in filename:
                            break
                if len(filename[17:]) > self.max_file_size:
                    sock[0].send(b"ERROR File size must > " + str(self.max_file_size).encode() + b"B")
                else:
                    message = (time.ctime() + filename[:10].decode() + "(" + sock[1][0] + ")" + "." + filename
                    [:10].
                               decode().split(".")[-1]).strip() + "File"
                    message = message.strip()
                    message = message.replace(":", " ")
                    message = message.replace("(", "I")
                    message = message.replace(")", "P")
                    message = message.replace(" ", "")
                    file = open(".\\data\\0" + message[:-4], "wb")
                    file.write(filename[17:])
                    self._lock.acquire()
                    self.new_message = deepcopy(message + "\n")
                    self._lock.release()
            else:
                sock[0].send(b"ERROR403")
                sock[0].close()
                continue

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
            comm = command.split()
            if comm and comm[0] in ["ban", "un_ban", "show_baned"]:
                if comm[0] == "ban":
                    self.ban_ip = comm[1]
                    self.baned_ip.append(comm[1])
                elif comm[0] == "un_ban":
                    self.ban_ip = None
                    try:
                        self.baned_ip.remove(comm[1])
                    except IndexError:
                        print("IP isn't in baned ip")
                elif comm[0] == "show_baned":
                    print(self.baned_ip)
            else:
                print("Unknown command")

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
                    print(1)
                    print(self.new_message, self.old_message)
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
                    except OSError:
                        self.connect_number -= 1
                        self.send_message_state[index] = True
                        return
                    return
            except ConnectionResetError:
                self.send_message_state[index] = True
                self.connect_number -= 1
                return

    def radio_broadcast(self):
        sock = s.socket(type=s.SOCK_DGRAM)
        sock.bind(("0.0.0.0", 18500))
        print("Start sending broadcast packets")
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
            except Exception as error_data:
                print(type(error_data), error_data)
            else:
                break

        while True:
            try:
                data_socket = server.accept()
                if data_socket[1][0] in self.baned_ip:
                    data_socket[0].send(bz2.compress("You Can't join us".encode("utf-32")))
                    del data_socket
                    continue
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
                print("please input again")
                continue
            except OSError:
                print("Error:Port 8000 is in use")
                input()
                sys.exit()
            self.users.append(data_socket[1][0])
            print("New connect:", data_socket[1][0])
            print("Connection Number:", self.connect_number // 2)
            t.Thread(target=self.processing_communication, args=(data_socket, ran)).start()
            t.Thread(target=self.processing_communication2, args=(data_socket,)).start()


def main():
    radio_address = input("Please enter radio broadcast address:")
    sn = input("Please enter the server name:")[:30]
    file_size = int(input("Please input max upload file size(B):"))
    server = ChatServer(8505, radio_address, sn, file_size)
    server.processing_connections()


if __name__ == '__main__':
    main()
