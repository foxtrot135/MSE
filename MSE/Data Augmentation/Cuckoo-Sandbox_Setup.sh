

sudo apt update
sudo apt upgrade
sudo apt-get install python python-pip python-dev libffi-dev libssl-dev -y
sudo apt-get install python-virtualenv python-setuptools -y
sudo apt-get install libjpeg-dev zlib1g-dev swig -y
sudo apt-get install mongodb -y
sudo apt-get install postgresql libpq-dev -y
sudo apt install virtualbox -y
sudo apt-get install tcpdump apparmor-utils -y


sudo adduser --disabled-password --gecos "" cuckoo

sudo groupadd pcap
sudo usermod -a -G pcap cuckoo
sudo chgrp pcap /usr/sbin/tcpdump
sudo setcap cap_net_raw,cap_net_admin=eip /usr/sbin/tcpdump

getcap /usr/sbin/tcpdump
sudo aa-disable /usr/sbin/tcpdump

sudo apt-get install swig
sudo pip install m2crypto

sudo usermod -a -G vboxusers cuckoo

sudo su cuckoo


-----------------------------------------
#!/usr/bin/env bash

# NOTES: Run this script as: sudo -u <USERNAME> cuckoo-setup-virtualenv.sh

# install virtualenv
sudo apt-get update && sudo apt-get -y install virtualenv

# install virtualenvwrapper
sudo apt-get -y install virtualenvwrapper

echo "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh" >> ~/.bashrc

# install pip for python3
sudo apt-get -y install python3-pip

# turn on bash auto-complete for pip
pip3 completion --bash >> ~/.bashrc

# avoid installing with root
pip3 install --user virtualenvwrapper

echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc

echo "source ~/.local/bin/virtualenvwrapper.sh" >> ~/.bashrc

export WORKON_HOME=~/.virtualenvs

echo "export WORKON_HOME=~/.virtualenvs" >> ~/.bashrc

echo "export PIP_VIRTUALENV_BASE=~/.virtualenvs" >> ~/.bashrc 

---------------------------------

sudo -u *current user* cuckoo-setup-virtualenv.sh

source ~/.bashrc

mkvirtualenv -p python2.7 cuckoo-test

pip install -U pip setuptools
pip install -U cuckoo


----------setup virtual machine--------
sudo wget https://cuckoo.sh/win7ultimate.iso
sudo mkdir /mnt/win7
sudo chown cuckoo:cuckoo /mnt/win7/
sudo mount -o ro,loop win7ultimate.iso /mnt/win7

sudo apt-get -y install build-essential libssl-dev libffi-dev python-dev genisoimage
sudo apt-get -y install zlib1g-dev libjpeg-dev
sudo apt-get -y install python-pip python-virtualenv python-setuptools swig

pip install -U vmcloak

vmcloak-vboxnet0

vmcloak init --verbose --win7x64 win7x64base --cpus 2 --ramsize 2048

vmcloak clone win7x64base win7x64cuckoo

vmcloak list deps

vmcloak install win7x64cuckoo ie11

vmcloak snapshot --count 1 win7x64cuckoo 192.168.56.101

vmcloak list vms

--------------interacting with cuckoo--------
cuckoo init
cuckoo community

while read -r vm ip; do cuckoo machine --add $vm $ip; done < <(vmcloak list vms)

sudo sysctl -w net.ipv4.conf.vboxnet0.forwarding=1
sudo sysctl -w net.ipv4.conf.*your interface name*.forwarding=1

sudo iptables -t nat -A POSTROUTING -o *your interface name* -s 192.168.56.0/24 -j MASQUERADE
sudo iptables -P FORWARD DROP
sudo iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -s 192.168.56.0/24 -j ACCEPT

cuckoo rooter --sudo --group opensecure

cuckoo web --host 127.0.0.1 --port 8080