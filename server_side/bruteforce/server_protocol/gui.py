import sys
from PyQt5.QtWidgets import (QWidget, QToolTip, 
    QPushButton, QApplication, QMessageBox, QDesktopWidget,QInputDialog,
    QComboBox, QFileDialog)
from PyQt5.QtGui import QFont    
from PyQt5.QtWidgets import (QLabel, QLineEdit,
    QTextEdit, QGridLayout )
from PyQt5.QtCore import Qt
from network_tools import *
from connection_tools import *

class Gui(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):

        #objects to retrieve 
        
        #target and username
        target = QLabel('Target')
        username = QLabel('Username')
        self.target_Edit = QLineEdit()
        self.username_Edit = QLineEdit()

        #Ask number of cores to use
        cores_num = QLabel('Number or cores')
        self.cores_num_Edit = QLineEdit()

        #ask for the protocol required
        protocol_lbl = QLabel("Protocol", self)

        self.protocol_combo = QComboBox(self)
        self.protocol_combo.addItem('ssh')
        self.protocol_combo.addItem('mysql')
        self.protocol_combo.move(50, 50)
        protocol_lbl.move(50, 150)
        
        #Ask port to attack
        port_num = QLabel('Port')
        self.port_num_Edit = QLineEdit()
        self.port_Edit = QLineEdit()
        
        #Button to browse and get dictionnary
        self.dictionnary_btn = QPushButton('Open dictionnary', self)
        self.dictionnary_btn.move(20, 20)
        self.dictionnary_btn.clicked.connect(self.openFileNameDialog)
        self.dictionnary_Edit = QLineEdit()

        #Ask for network checks
        network_checks_lbl = QLabel("Network checks", self)

        self.network_checks_combo = QComboBox(self)
        self.network_checks_combo.addItem("yes")
        self.network_checks_combo.addItem("no")
        self.network_checks_combo.move(50, 50)
        network_checks_lbl.move(50, 150)

        #Create a Run attack button
        self.attack_btn = QPushButton('Run attack', self)
        self.attack_btn.move(20, 20)
        self.attack_btn.clicked.connect(self.set_attack_parameters)

        #Create a quit button
        self.quit_btn = QPushButton('Quit', self)
        self.quit_btn.move(20, 20)
        self.quit_btn.clicked.connect(QApplication.instance().quit)

        #Set the grid and add the objects

        #Set the grid
        grid = QGridLayout()
        grid.setSpacing(7)

        #Add target
        grid.addWidget(target, 1, 0)
        grid.addWidget(self.target_Edit, 1, 1)

        #Add username
        grid.addWidget(username, 2, 0)
        grid.addWidget(self.username_Edit, 2, 1)

        #Add cores
        grid.addWidget(cores_num, 3, 0)
        grid.addWidget(self.cores_num_Edit, 3, 1)

        #Add protocol
        grid.addWidget(protocol_lbl, 4, 0)
        grid.addWidget(self.protocol_combo, 4, 1)

        #Add port
        grid.addWidget(port_num, 5, 0)
        grid.addWidget(self.port_num_Edit, 5, 1)

        #Add dictionnary
        grid.addWidget(self.dictionnary_btn, 6, 0)
        grid.addWidget(self.dictionnary_Edit, 6, 1)

        #Add network checks
        grid.addWidget(network_checks_lbl, 7, 0)
        grid.addWidget(self.network_checks_combo, 7, 1)

        #Add buttons to quit or attack 
        grid.addWidget(self.quit_btn, 8, 0)
        grid.addWidget(self.attack_btn, 8, 1)

        #Set layout of the main widget
        self.setLayout(grid) 
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Review')    
        self.show()



    def set_attack_parameters(self):
        '''method used to retrieve all the parameters
        and launch the attack'''
        username = self.username_Edit.text()
        target = self.target_Edit.text()
        cores = self.cores_num_Edit.text()
        protocol = self.protocol_combo.itemText(self.protocol_combo.currentIndex())
        port = int(self.port_num_Edit.text())
        network_checks = self.network_checks_combo.itemText(self.protocol_combo.currentIndex())
        password_file = self.dictionnary_Edit.text()
        print(username, target, cores, protocol, port, network_checks, password_file)
        
        ####################################
        #Creating a NetworkTools object, to inspect
        #if the network request is consistent
        if network_checks == 'yes':
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
    
    def openFileNameDialog(self):
        '''method used to open the file browser and
        retrieve the dictionnary'''
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            self.dictionnary_Edit.setText(fileName)


    def closeEvent(self, event):
        '''This defines the behavior when clicking on 
        the cross to close the window'''
        reply = QMessageBox.question(self, 'Message',"Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        '''centers the window in the middle of the screen'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
def main():
    app = QApplication(sys.argv)
    ex = Gui()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()    

