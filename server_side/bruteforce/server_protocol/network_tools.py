import subprocess
import nmap

class NetworkTools:
    def __init__(self, host, port, protocol):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.ping = False 
        self.nmap = False

    def get_ping(self):
        try:
            ping = subprocess.check_output(["ping", "-c", "1", self.host]) 
            print("The server at " + self.host + " could be pinged")
            self.ping = True 
            return self.ping

        except subprocess.CalledProcessError:
            print("The server at " + self.host + " cannot be pinged - Aborting")
            return self.ping
            
    def get_nmap(self):
        print('Checking the host at {} on port {} with protocol {}'.format(self.host, self.port, self.protocol))

        #Creating a nmap scanner object 
        nmScan = nmap.PortScanner()

        #Scanning the ports of the host 
        nmScan.scan(self.host, '20-5000')

        #Try to get the protocol on the requested port
        try:
            #check if the host has the required port listening
            protocol = nmScan[self.host]['tcp'][self.port]['name']

            if protocol == self.protocol:
                self.nmap = True
            else:
                print('The port {} is listening for another protocol ({})'.format(self.port, protocol))
                print('which is different than what you required!')

        except:
            print('{} NOT listening for {} on port {} '.format(self.host, self.protocol, self.port))



        #if the protocol was not good, check if we can find
        #it on an other port
        if self.nmap == False:
            #search if the protocol is listening on another port
            try:
                for port in nmScan['127.0.0.1']['tcp']:
                    protocol = nmScan['127.0.0.1']['tcp'][port]['name'] 

                    #if a new port is found with consistent protocol
                    #the user is asked to change port
                    if protocol == self.protocol:
                       print('Port {} has been found to listen for {}'.format(port, protocol)) 
                       answer = raw_input("Do you want to use that port?[y/n] ")
                       if answer =='y':
                           self.port = port
                           print('Running the attack on the new select port ({})'.format(self.port))
                           self.nmap = True
                       else:
                           self.nmap = False
            except:
                print('No other port corresponding to your request could be found!')

    def get_network_status(self):
        return (self.ping and self.nmap)











