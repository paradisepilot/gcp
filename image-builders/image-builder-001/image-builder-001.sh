#!/bin/bash

sudo apt-get    update
sudo apt-get -y upgrade

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### install Anaconda dependencies
sudo apt-get --yes install build-essential cmake unzip pkg-config libopenblas-dev liblapack-dev
sudo apt-get --yes install libhdf5-serial-dev
sudo apt-get --yes install graphviz

### install R dependencies
sudo apt-get --yes install default-jre
sudo apt-get --yes install openjdk-11-jdk
sudo apt-get --yes install libgl1-mesa-glx
sudo apt-get --yes install libxml2-dev
sudo apt-get --yes install libssl-dev libcurl4-openssl-dev
sudo apt-get --yes install libcairo2-dev

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
sudo rm /var/lib/dpkg/lock
sudo dpkg --configure -a
sudo apt-get update

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
### install R
echo starting to install r-basse, r-base-dev ...
sudo dpkg --configure -a
sudo apt-get --yes install r-base r-base-dev
echo successfully installed r-base, r-base-dev

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
rpackagesFILE=Rpackages-desired.txt
myRscript=install_R_packages.R

outputDIR=./output.`basename ${myRscript} .R`
if [ ! -d ${outputDIR} ]; then
        mkdir -p ${outputDIR}
fi

stdoutFile=${outputDIR}/stdout.R.`basename ${myRscript} .R`
stderrFile=${outputDIR}/stderr.R.`basename ${myRscript} .R`
sudo R --no-save --args ${outputDIR} ${rpackagesFILE} < ${myRscript} > ${stdoutFile} 2> ${stderrFile}

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
touch  ${myHOME}/STARTUP-COMPLETE.txt
chown --recursive ${myUsername} ${myHOME}/STARTUP-COMPLETE.txt
chgrp --recursive ${myUsername} ${myHOME}/STARTUP-COMPLETE.txt

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
source ${myHOME}/.bashrc

