#!/usr/bin/env python

import scapy.all as scapy
from optparse import OptionParser

def scan(ip):
    arp_request = scapy.ARP(pdst=ip) #creating an ARP packet
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") #creating an Ether packet
    arp_request_broadcast = broadcast/arp_request 
    #send packet with custom Ether (srp)t
    answered_list = scapy.srp(arp_request_broadcast, 
            timeout=1, verbose=False)[0]# to get only the first list 

    #Storing the result of the ARP request in a dictionnary
    clients_list=[]
    for element in answered_list:
        client_dict = {"ip": element[1].psrc, "mac":element[1].hwsrc}
        clients_list.append(client_dict)
    return clients_list

#function to print the result of the ARP request (ip and mac)
def print_result(results_list):
    print("IP\t\t\tMAC Address\n------------------------------------------")
    for client in results_list:
        print(client["ip"]+"\t\t" + client["mac"])

if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-t", "--target", dest="ip_range",
            help="set the ip range you want to scan")
    (options, args) = parser.parse_args()
    scan_result = scan(options.ip_range)
    print_result(scan_result)
