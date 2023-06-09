#!/bin/bash

# Stop the services
service apache2 stop
service hostapd stop
service dnsmasq stop

# Remove the configuration files
rm /etc/dnsmasq.conf
rm /etc/hostapd/hostapd.conf

# Disable IP forwarding
sysctl net.ipv4.ip_forward=0

# Remove the NAT and forwarding rules
iptables --flush
iptables -t nat --flush

# Remove the bridge interface
ifconfig br0 down
brctl delbr br0

# Restore the original MAC address of your wireless interface
ifconfig wlan0 down
macchanger -p wlan0
ifconfig wlan0 up

# Restart networking
service networking restart

