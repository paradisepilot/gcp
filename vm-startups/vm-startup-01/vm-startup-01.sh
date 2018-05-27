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
#conda install --yes pydot-ng h5py opencv
conda install --yes yaml matplotlib
conda install --yes pandas
conda install --yes scikit-learn
#conda install --yes keras

#anacondaInstaller=Anaconda3-5.1.0-Linux-x86_64.sh
#curl -O https://repo.anaconda.com/archive/${anacondaInstaller}
#bash ${anacondaInstaller} -b -p $HOME/anaconda

source ${myHOME}/.bashrc
touch  ${myHOME}/STARTUP-COMPLETE.txt

