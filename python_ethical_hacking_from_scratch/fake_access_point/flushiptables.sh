echo 1 > /proc/sys/net/ipv4/ip_forward #allow forwarding
iptables --flush
iptables --table nat --flush
iptables --delete-chain
iptables --table nat --delete-chain
iptables -P FORWARD ACCEPT
