#!/bin/bash

sudo apt-get -y update
sudo apt-get -y upgrade

myUsername=`whoami`
myHOME=/home/${myUsername}

sudo apt-get -y install git
sudo git clone https://github.com/paradisepilot/gcp

touch ${myHOME}/STARTUP-COMPLETE.txt

