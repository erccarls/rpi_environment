#!/usr/bin/env bash

ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."

wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh
bash Miniconda3-latest-Linux-armv7l.sh -b
source ~/.bashrc

conda install -f $ROOT/environment.yaml