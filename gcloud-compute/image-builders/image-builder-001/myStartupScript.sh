#!/bin/bash
touch /home/`whoami`/STARTUP-BEGINS.txt
sudo apt-get    update
sudo apt-get -y upgrade
sudo apt-get -y install git
git clone https://github.com/paradisepilot/gcp
touch /home/`whoami`/STARTUP-COMPLETE.txt
