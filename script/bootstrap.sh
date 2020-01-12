#!/usr/bin/env bash

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."

wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh
bash Miniconda3-latest-Linux-armv7l.sh -b -p $HOME/miniconda

echo export PATH=\"/home/pi/miniconda/bin:$PATH\" >> ~/.bashrc
source ~/.bashrc

sudo apt-get update
sudo apt-get install -y build-essential python3-dev python-openssl git

conda env create -f $ROOT/environment.yaml
echo source activate pi_environment >> ~/.bashrc

jupyter notebook --generate-config
jupyter notebook password

# Enable 1-wire interface on GPIO4=header pin 7
echo "sudo dtoverlay w1-gpio gpiopin=4 pullup=0 " >> ~/.bashrc
echo "sudo dtoverlay w1-gpio gpiopin=17 pullup=0 " >> ~/.bashrc