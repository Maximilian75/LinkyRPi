#!/bin/bash
GREEN='\033[0;32m'
GREENL='\033[1;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
echo -e "${GREEN}Starting LinkyRpi installation...${NC}"
echo -e "${GREENL}- Adding sources"
sudo sh -c 'echo "deb http://mirror.ox.ac.uk/sites/archive.raspbian.org/archive/raspbian stretch main contrib non-free rpi" >> /etc/apt/sources.list'
echo -e "${GREENL}- Updating packages${NC}"
apt-get update

echo -e "${GREENL}- Installing Python${NC}"
apt install python3-serial
apt install python3-pip
apt-get install libpq-dev
pip3 install psycopg2
pip3 install psycopg2-binary
apt-get install python3-psycopg2
pip3 install RPi.GPIO
apt-get install python3-tk
pip3 install posix_ipc
pip3 install pyserial
apt-get install xterm
apt-get install libopenjp2-7
pip3 install paho-mqtt

echo -e "${GREENL}- Setting RPi time${NC}"
timedatectl set-timezone Europe/Paris
timedatectl set-ntp true
timedatectl status

echo -e "${GREENL}- Setting screen config${NC}"
echo -e " " >> /boot/config.txt
echo -e "max_usb_current=1" >> /boot/config.txt
echo -e "hdmi_group=2" >> /boot/config.txt
echo -e "hdmi_mode=87" >> /boot/config.txt
echo -e "hdmi_cvt 1024 600 60 6 0 0 0" >> /boot/config.txt
echo -e "hdmi_drive=1" >> /boot/config.txt
apt-get -y install nodm matchbox-window-manager
sudo apt-get install x11-xserver-utils
sudo apt-get install xinit

echo -e " "
read -p "${GREEN}Press ${YELLOW}[ENTER] ${GREEN}to continue...${NC}"

exit 1

#sed
#/lib/systemd/system/nodm.service
#After=plymouth-quit.service systemd-user-sessions.service runlevel2.target, runlevel4.target, multi-user.target

echo -e "${GREENL}- Creating process : Listener${NC}"
cp services/LinkyRPiListen.service /lib/systemd/system
chmod 644 /lib/systemd/system/LinkyRPiListen.service

echo -e "${GREENL}- Creating process : Dispatcher${NC}"
cp services/LinkyRPiDispatch.service /lib/systemd/system
chmod 644 /lib/systemd/system/LinkyRPiDispatch.service

echo -e "${GREENL}- Creating process : UI${NC}"
cp services/LinkyRPiGUI.servicee /lib/systemd/system
chmod 644 /lib/systemd/system/LinkyRPiGUI.service

echo -e "${GREENL}- Creating process : DataBase${NC}"
cp services/LinkyRPiDB.service /lib/systemd/system
chmod 644 /lib/systemd/system/LinkyRPiDB.service

echo -e "${GREENL}- Creating process : MQTT${NC}"
cp services/LinkyRPiMQTT.service /lib/systemd/system
chmod 644 /lib/systemd/system/LinkyRPiMQTT.service

echo -e "${GREENL}- Starting services${NC}"
sudo systemctl daemon-reload
systemctl enable LinkyRPiListen.service
systemctl enable LinkyRPiDispatch.service
systemctl enable LinkyRPiGUI.service
systemctl enable LinkyRPiDB.service
systemctl enable LinkyRPiMQTT

echo -e "${GREENL}- Removing temporary files${NC}"
rm -r services

echo -e "${GREEN}LinkyRPi installation complete${NC}"
echo -e "${GREEN}LinkyRPi is about to be rebooted${NC}"
echo -e " "
read -p "${GREEN}Press ${YELLOW}[ENTER] ${GREEN}to continue...${NC}"
reboot
