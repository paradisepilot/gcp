#!/bin/bash

sudo apt-get    update
sudo apt-get -y upgrade

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

#myUsername=USERNAME
myUsername=`whoami`
myHOME=/home/${myUsername}
minicondaDIR=${myHOME}/miniconda
echo minicondaDIR=${minicondaDIR}

#minicondaInstaller=Miniconda3-latest-Linux-x86_64.sh
minicondaInstaller=Miniconda3-4.5.1-Linux-x86_64.sh
curl -O https://repo.continuum.io/miniconda/${minicondaInstaller}
bash ${minicondaInstaller} -b -p ${minicondaDIR}
#export PATH="$minicondaDIR/bin:$PATH"

source ${minicondaDIR}/bin/activate
echo >> ${myHOME}/.bashrc
echo PATH="$PATH" >> ${myHOME}/.bashrc
echo >> ${myHOME}/.bashrc

conda update  --yes conda
${minicondaDIR}/bin/pip install --upgrade pip

${minicondaDIR}/bin/pip install google-compute-engine
${minicondaDIR}/bin/pip install matplotlib
${minicondaDIR}/bin/pip install seaborn
${minicondaDIR}/bin/pip install h5py
${minicondaDIR}/bin/pip install pyyaml
${minicondaDIR}/bin/pip install pandas
${minicondaDIR}/bin/pip install scikit-learn
${minicondaDIR}/bin/pip install gensim
${minicondaDIR}/bin/pip install opencv

${minicondaDIR}/bin/pip install pydot-ng
${minicondaDIR}/bin/pip install tensorflow
${minicondaDIR}/bin/pip install keras

#anacondaInstaller=Anaconda3-5.1.0-Linux-x86_64.sh
#curl -O https://repo.anaconda.com/archive/${anacondaInstaller}
#bash ${anacondaInstaller} -b -p $HOME/anaconda
 
# run the following command at the Python prompt to check
# if the packages have been installed properly:
# >>> import matplotlib, seaborn, h5py, yaml, pandas, sklearn, cv2, pydot_ng, tensorflow, keras

chown --recursive ${myUsername} ${minicondaDIR}
chgrp --recursive ${myUsername} ${minicondaDIR}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# The following FOR loop is to avoid the following error:
# E: Could not get lock /var/lib/apt/lists/lock - open (11: Resource temporarily unavailable)
# E: Unable to lock directory /var/lib/apt/lists/
for tempID in `ps -A | egrep 'apt-get' | awk '{print $1}'`
do
    echo starting to kill process ${tempID} ...
    sudo kill -9 ${tempID}
    echo successfully killed process ${tempID}.
done

sleep 2
echo AAA
sudo rm /var/lib/dpkg/lock
echo BBB
sudo dpkg --configure -a
echo CCC
sudo apt-get update
echo DDD

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### install R
echo EEE
sudo dpkg --configure -a
echo FFF
sudo apt-get --yes install r-base r-base-dev
echo GGG

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
touch  ${myHOME}/STARTUP-COMPLETE.txt
chown --recursive ${myUsername} ${myHOME}/STARTUP-COMPLETE.txt
chgrp --recursive ${myUsername} ${myHOME}/STARTUP-COMPLETE.txt

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ${myHOME}/.bashrc

