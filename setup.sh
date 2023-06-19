#!/bin/bash

if [ "$(id -u)" -ne 0 ]
    then echo "Please run as root"
    exit
fi

try_echo () {
    if [ -z "$(grep $1 $2)" ]
    then
        echo "$1" >> "$2"
        echo "Set up $2"
    else
        echo "$2 already set up!"
    fi
}

echo "Setup environment"
sudo apt update && sudo apt upgrade -y
# sudo apt install python3-venv
# python3 -m venv venv
# source venv/bin/activate
sudo pip install -r requirements.txt

echo "Load the I2C kernel modules"
modprobe i2c_dev
modprobe i2c_bcm2708

echo "Enable I2C on the Raspberry Pi"
setting1="dtparam=i2c1=on"
setting2="dtparam=i2c_arm=on"
path="/boot/config.txt"
try_echo "dtparam=i2c1=on" $path
# echo "dtparam=i2c1=on" >> /boot/config.txt
try_echo "dtparam=i2c_arm=on" $path
# echo "dtparam=i2c_arm=on" >> /boot/config.txt

echo "Add the I2C devices to the modules file"
path="/etc/modules"
try_echo "i2c-dev" $path
# echo "i2c-dev" >> /etc/modules
try_echo "i2c_bcm2708" $path
# echo "i2c-bcm2708" >> /etc/modules

echo "Setup udev config"
text="SUBSYSTEM==\"usb\", ACTION==\"add\", RUN+=\"$HOME/blink-reset/run-blink-reset.sh\""
path="/etc/udev/rules.d/99-reset-device.rules"
try_echo "$text" $path
# echo 'SUBSYSTEM=="usb", ACTION=="add", RUN+="$HOME/blink-reset/run-blink-reset.sh"' >> /etc/udev/rules.d/99-reset-device.rules

# Restart the Raspberry Pi to apply the changes
read -p "Reboot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    reboot
fi
