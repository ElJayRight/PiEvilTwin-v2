#!/bin/bash

cp -r dnsmasq.conf /etc/dnsmasq.conf
cp -r hostapd.conf /etc/hostadp/hostapd.conf

service apache2 start
sleep 1
ifconfig wlxc01c301fecff down
macchanger --mac=aa:bb:cc:dd:ee:ff wlan0
sleep 1 
ifconfig wlxc01c301fecff up
sleep 1
hostapd -B /etc/hostapd/hostapd.conf
sleep 2
ifconfig br0 up
sleep 2
ifconfig br0 10.1.1.1 netmask 255.255.255.0
sysctl net.ipv4.ip_forward=1
iptables --flush
iptables -t nat --flush
iptables -t nat -A PREROUTING -i br0 -p udp -m udp --dport 53 -j DNAT --to-destination 10.1.1.1:53
iptables -t nat -A PREROUTING -i br0 -p tcp -m tcp --dport 80 -j DNAT --to-destination 10.1.1.1:80
iptables -t nat -A PREROUTING -i br0 -p tcp -m tcp --dport 443 -j DNAT --to-destination 10.1.1.1:80
iptables -t nat -A POSTROUTING -j MASQUERADE
sleep 2
service dnsmasq start
sleep 2
service dnsmasq restart
sleep 4
exit 0
