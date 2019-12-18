# -*- coding:UTF-8 -*-
import threading as t
import socket as s
import sys
import bz2
from copy import *
# from typing import Any, Tuple
from time import sleep


class ChatServer:
    def __init__(self, port, address, server_name):
        self.connect_number = 0
        self.users = []
        self.baned_ip = []
        self.ban_ip = None
        self._lock = t.Lock()
        self.server_name = server_name
        self.address = address
        self.new_message = None
        self._number = 0
        self.port = port
        self.old_message = None

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
                    except ValueError:
                        print("IP isn't in baned ip")
                elif comm[0] == "show_baned":
                    print(self.baned_ip)
            else:
                print("Unknown command")

    def processing_communication(self, socket_):
        """Broadcasting information to users
        user <- data <- server

        """
        self.connect_number += 1
        # active count return active count(len(t.enumerate()))
        while True:
            try:
                if self.new_message != self.old_message:
                    socket_[0].send(bz2.compress(self.new_message.encode("utf-32")))
                    self.old_message = deepcopy(self.new_message)
                if socket_[1][0] == self.ban_ip:
                    try:
                        print(socket_[1][0] + " thread2 closed")
                        socket_[0].send(bz2.compress("友好的中文提示:你已被踢出服务器, 并且在管理员没有取消封杀的情况下无法再次加入".encode("utf-32")))
                        socket_[0].close()
                    except OSError:
                        return
                    return
            except ConnectionResetError:
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
                message = bz2.decompress(socket_[0].recv(102400)).decode("utf-32").strip() + "(" + socket_[1][0] + ")\n"
            except OSError:
                self.connect_number -= 1
                print("INFO:recv the wrong message,from" + socket_[1][0])
                return
            except ConnectionResetError:
                self.connect_number -= 1
                print(socket_[1][0] + "Closed")
                return
            self.new_message = deepcopy(message)

    def processing_connections(self):
        server = s.socket()
        conn_num = int(input("please input max connects(1-999999999):" or "10000"))
        t.Thread(target=self.enter_command).start()
        t.Thread(target=self.radio_broadcast).start()
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
                print(1)
                t.Thread(target=self.processing_communication, args=(data_socket,)).start()
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
            t.Thread(target=self.processing_communication, args=(data_socket,)).start()
            t.Thread(target=self.processing_communication2, args=(data_socket,)).start()


def main():
    radio_address = input("Please enter radio broadcast address:")
    sn = input("Please enter the server name:")
    server = ChatServer(8505, radio_address, sn)
    server.processing_connections()


if __name__ == '__main__':
    main()
