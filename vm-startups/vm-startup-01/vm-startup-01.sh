#!/bin/bash

sudo apt-get update
sudo apt-get --yes install r-base r-base-dev

mkdir ./tmp
cd    ./tmp

minicondaInstaller=Miniconda3-latest-Linux-x86_64.sh
curl -O https://repo.continuum.io/miniconda/${minicondaInstaller}
bash ${minicondaInstaller} -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
source $HOME/miniconda/bin/activate

conda update  --yes conda
conda install --yes pandas scikit-learn
#conda install --yes keras

#anacondaInstaller=Anaconda3-5.1.0-Linux-x86_64.sh
#curl -O https://repo.anaconda.com/archive/${anacondaInstaller}
#bash ${anacondaInstaller} -b -p $HOME/anaconda

