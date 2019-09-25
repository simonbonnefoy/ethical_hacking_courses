This is a code to perform bruteforce attack on a server.
So far, ssh and mysql protocols have been implemented.
Further protocols will be implemented in the futur (according to personal 
needs or on request)

To make the code work, you will need the following libraries:

pip install paramiko
pip install python-nmap
pip install mysql-connector-python
pip install pytest


#####################################################
Test unit

A unit test has been built to check the functionalities on your machine.
Go to the main folder (server_protocol) and run in a terminal 
$ pytest

This should go through all the test and let you know if something is failing.
