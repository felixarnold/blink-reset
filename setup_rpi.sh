#!/bin/bash

sudo apt update && sudo apt upgrade -y
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Load the I2C kernel modules
modprobe i2c_dev
modprobe i2c_bcm2708

# Enable I2C on the Raspberry Pi
echo "dtparam=i2c1=on" >> /boot/config.txt
echo "dtparam=i2c_arm=on" >> /boot/config.txt

# Add the I2C devices to the modules file
echo "i2c-dev" >> /etc/modules
echo "i2c-bcm2708" >> /etc/modules

# Restart the Raspberry Pi to apply the changes
reboot
