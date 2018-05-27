#!/bin/bash

sudo apt-get update
sudo apt-get upgrade

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### install Anaconda dependencies
sudo apt-get --yes install build-essential cmake unzip pkg-config libopenblas-dev liblapack-dev
sudo apt-get --yes install libhdf5-serial-dev
sudo apt-get --yes install graphviz

### the following is needed for opencv (cv2)
sudo apt-get --yes install libgl1-mesa-glx

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
${minicondaDIR}/bin/pip install --upgrade pip

conda install --yes --channel conda-forge matplotlib
conda install --yes --channel anaconda    seaborn
conda install --yes --channel anaconda    h5py
conda install --yes --channel anaconda    pyyaml
conda install --yes --channel anaconda    pandas
conda install --yes --channel anaconda    scikit-learn
conda install --yes --channel conda-forge opencv

${minicondaDIR}/bin/pip install pydot-ng

${minicondaDIR}/bin/pip install tensorflow
${minicondaDIR}/bin/pip install keras

#anacondaInstaller=Anaconda3-5.1.0-Linux-x86_64.sh
#curl -O https://repo.anaconda.com/archive/${anacondaInstaller}
#bash ${anacondaInstaller} -b -p $HOME/anaconda
 
chown --recursive ${myUsername} ${minicondaDIR}
chgrp --recursive ${myUsername} ${minicondaDIR}
chown --recursive ${myUsername} ${myHOME}/tmp
chgrp --recursive ${myUsername} ${myHOME}/tmp

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### install R
#sudo apt-get --yes install r-base r-base-dev

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
touch  ${myHOME}/STARTUP-COMPLETE.txt
chown --recursive ${myUsername} ${myHOME}/STARTUP-COMPLETE.txt
chgrp --recursive ${myUsername} ${myHOME}/STARTUP-COMPLETE.txt

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ${myHOME}/.bashrc

