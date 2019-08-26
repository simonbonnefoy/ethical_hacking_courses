#!/usr/bin/env python
import netfilterqueue

#iptables -I FORWARD -j NFQUEUE --queue-num 0
#iptables --flush

#To test on local machine
#iptables -I OUTPUT -j NFQUEUE --queue-num 0
#iptables -I INPUT -j NFQUEUE --queue-num 0

def process_packet(packet):
    print(packet)
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()

