import pytest
import network_tools
from connection_tools import *
import subprocess

# content of test_sample.py


#def test_network_tools():
#    ping = network_tools.get_ping('127.0.0.1')
#    assert (ping == True or ping == False)

def test_ssh_connection_tools():

    #Create the connection object
    connection = ConnectionTools('user', '127.0.0.1', \
            22, 'ssh', 1, "dictionnaries/unit_test_password.txt") 

    #printer start-up baneer
    connection.print_attack()

    t1 = time.time()
    connection.run()

def test_mysql_connection_tools():

    #Create the connection object
    connection = ConnectionTools('user', '127.0.0.1', \
            3306, 'mysql', 1, "dictionnaries/unit_test_password.txt") 

    #printer start-up baneer
    connection.print_attack()

    t1 = time.time()
    connection.run()

def test_bruteforce():
    bruteforce = 'python bruteforce.py -t 127.0.0.1 -u root -f dictionnaries/unit_test_password.txt'
    #os.system(bruteforce)
    process = subprocess.Popen(bruteforce.split(), stdout=subprocess.PIPE)
    #output, error = process.communicate()
