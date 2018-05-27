#!/bin/bash

sudo apt-get update
sudo apt-get upgrade

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### install R
#sudo apt-get --yes install r-base r-base-dev

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### install Anaconda dependencies
sudo apt-get --yes install build-essential cmake unzip pkg-config libopenblas-dev liblapack-dev
sudo apt-get --yes install libhdf5-serial-dev
sudo apt-get --yes install graphviz

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### install miniconda
mkdir ./tmp
cd    ./tmp

myUsername=USERNAME
myHOME=/home/${myUsername}
minicondaDIR=${myHOME}/miniconda
echo minicondaDIR=${minicondaDIR}

minicondaInstaller=Miniconda3-latest-Linux-x86_64.sh
curl -O https://repo.continuum.io/miniconda/${minicondaInstaller}
bash ${minicondaInstaller} -b -p ${minicondaDIR}
#export PATH="$minicondaDIR/bin:$PATH"

source ${minicondaDIR}/bin/activate
echo >> ${myHOME}/.bashrc
echo PATH="$PATH" >> ${myHOME}/.bashrc
echo >> ${myHOME}/.bashrc

conda update  --yes conda

conda install --yes --channel anaconda    h5py
#conda install --yes --channel conda-forge opencv
#conda install --yes --channel anaconda    pydot-ng

#conda install --yes --channel anaconda    yaml
#conda install --yes --channel conda-forge matplotlib
#conda install --yes --channel anaconda    pandas
#conda install --yes --channel anaconda    scikit-learn
#conda install --yes --channel anaconda    keras-gpu

#anacondaInstaller=Anaconda3-5.1.0-Linux-x86_64.sh
#curl -O https://repo.anaconda.com/archive/${anacondaInstaller}
#bash ${anacondaInstaller} -b -p $HOME/anaconda
 
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
chown --recursive ${myUsername} ${minicondaDIR}
chgrp --recursive ${myUsername} ${minicondaDIR}

chown --recursive ${myUsername} ${myHOME}/tmp
chgrp --recursive ${myUsername} ${myHOME}/tmp

source ${myHOME}/.bashrc
touch  ${myHOME}/STARTUP-COMPLETE.txt

