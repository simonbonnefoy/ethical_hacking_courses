#!/usr/bin/env python
import scapy.all as scapy
from scapy.layers import http #you need to pip install scapy_http 

def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)

def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest): #this is because scapy does not have http filter!
        if packet.haslayer(scapy.Raw):
            print(packet[scapy.Raw].load)

sniff("eth0")
