#!/bin/bash

sudo apt-get update
sudo apt-get --yes install r-base r-base-dev

mkdir ./tmp
cd    ./tmp

minicondaInstaller=Miniconda3-latest-Linux-x86_64.sh
curl -O https://repo.continuum.io/miniconda/${minicondaInstaller}
#bash ${minicondaInstaller}

#anacondaInstaller=Anaconda3-5.1.0-Linux-x86_64.sh
#curl -O https://repo.anaconda.com/archive/${anacondaInstaller}
#bash ${anacondaInstaller}

#source ~/.bashrc
#conda install scikit-learn
#conda install keras

