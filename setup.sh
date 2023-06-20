#!/bin/bash

if [ "$(id -u)" -ne 0 ]
    then echo "Please run as root"
    exit
fi

try_echo () {
    if [ -z "$(grep "$1" $2)" ]
    then
        echo "$1" >> "$2"
        echo "Set up $2"
    else
        echo "$2 already set up!"
    fi
}

username=$(logname)

echo "# Setup environment"
sudo apt update && sudo apt upgrade -y
# sudo apt install python3-venv
# python3 -m venv venv
# source venv/bin/activate
sudo pip install -r requirements.txt

echo "# Load the I2C kernel modules"
modprobe i2c_dev
modprobe i2c_bcm2708

echo "# Enable I2C on the Raspberry Pi"
path="/boot/config.txt"
try_echo "dtparam=i2c1=on" $path
try_echo "dtparam=i2c_arm=on" $path

echo "# Add the I2C devices to the modules file"
path="/etc/modules"
try_echo "i2c-dev" $path
try_echo "i2c-bcm2708" $path

echo "# Setup service config"
path="/lib/systemd/system/blink-reset.service"
touch $path
try_echo "\[Unit\]" $path
try_echo "Description=Service to auto flash mb boards that are connected via usb" $path
try_echo "After=multi-user.target" $path
echo "" >> $path
try_echo "\[Service\]" $path
try_echo "Type=idle" $path
try_echo "ExecStart=$PWD/main.py" $path
try_echo "WorkingDirectory=$PWD" $path
try_echo "User=$username" $path
echo "" >> $path
try_echo "\[Install\]" $path
try_echo "WantedBy=multi-user.target" $path

systemctl enable blink-reset.service
systemctl start blink-reset.service

# Restart the Raspberry Pi to apply the changes
read -p "Reboot now? (y/n) " -n 1 -r; echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    reboot
fi
