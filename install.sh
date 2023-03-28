#!/bin/sh -e

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root." 1>&2
   exit 1
fi

echo "Installing dependencies..."
apt-get install -y macchanger hostapd dnsmasq apache2 php

echo "Configuring components..."
echo "Setting up HTML Files..."
cp -Rf html /var/www/
chown -R www-data:www-data /var/www/html
chown root:www-data /var/www/html/.htaccess
echo "Copying startup script..."
cp -f PiEvilTwinStart.sh /root/
echo "Setting up permissions..."
chmod +x /root/PiEvilTwinStart.sh
echo "Setting up Apache Config..."
cp -f override.conf /etc/apache2/conf-available/
cd /etc/apache2/conf-enabled
ln -s ../conf-available/override.conf override.conf
cd /etc/apache2/mods-enabled
ln -s ../mods-available/rewrite.load rewrite.load
echo "..."
echo "PiEvilTwin captive portal installed. Credentials will be available here: http://10.1.1.1/usernames.txt"
echo "Run './PiEvilTwinStart.sh' to start the Evil-Twin and './stop.sh' to stop it."
exit 0
