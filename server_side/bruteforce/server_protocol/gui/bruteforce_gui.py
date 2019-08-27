import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.uic import loadUi
#sys.path.insert(1, '../')
from network_tools import *
from connection_tools import *
import logging

    
class MainPage(QDialog):
    def __init__(self):
        super(MainPage, self).__init__()

        #loading the main gui
        loadUi('main.ui', self)

        #define action of run attack button
        self.RunAttack.clicked.connect(self.run_attack)

        #define action of open dictionnary button
        self.open_dictionnary.clicked.connect(self.retrieve_password_file)

        #define action of Quit button
        self.quit.clicked.connect(QApplication.instance().quit)


    def retrieve_password_file(self):
        '''method used to open the file browser and
        retrieve the dictionnary'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            self.password_file.setText(fileName)

    def run_attack(self):
        '''Running the attack.
        Retrieving all the value, and setting the appropriate objects'''
        logging.debug('test')
        username = self.user.text()
        target = self.target.text()
        cores = self.cores.text()
        port = int(self.port.text())
        password_file = self.password_file.text()
        protocol = self.protocol.itemText(self.protocol.currentIndex())
        network_check = self.network_check.itemText(self.network_check.currentIndex())

        ####################################
        #Creating a NetworkTools object, to inspect
        #if the network request is consistent
        if network_check == 'yes':
            network_info = NetworkTools(target, \
                 port, protocol)

            #Checking if the server can be pinged and 
            #if the protocol is consistent
            network_info.get_ping()
            network_info.get_nmap()

            if (not network_info.get_network_status()):
                print('Exiting the program due to network problem')
                exit(0)
        
        
        #Create the connection object
        connection = ConnectionTools(username, target, \
                port, protocol, cores,\
                password_file) 

        #printer start-up baneer
        connection.print_attack()

        t1 = time.time()
        connection.run()

        print("Execution time: " + str (time.time() - t1))
        

app = QApplication(sys.argv)
widget = MainPage()
widget.show()

sys.exit(app.exec_())
