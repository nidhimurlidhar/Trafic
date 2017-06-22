#!/bin/bash

TRAFFIC_DIR=$1

PY_VERSION='2.7'

N_BIT='64'

cd /tmp

# Get the bash installer for linux 64bit python 2.7
echo "I. Conda installation"
if [ -f /tmp/Miniconda2-latest-Linux-x86_64.sh ]; then
	echo "Skipping Downloading of Miniconda installer exists already"
else
	echo "Download Miniconda installer"
	wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
fi
# We install miniconda
bash /tmp/Miniconda2-latest-Linux-x86_64.sh -b -p $TRAFFIC_DIR'/miniconda2/'
echo "===> Conda installed"

# We add the path of
export PATH=$TRAFFIC_DIR'/miniconda2/bin/':$PATH

echo "II. Create environment to run tensorflow"
conda create -y -n env_traffic python=$PY_VERSION
echo "===> environment created"

echo "III. Install tensorflow and libraries into environment"
source activate env_traffic
conda install -y -c conda-forge tensorflow
conda install -y -c anaconda vtk
touch $TRAFFIC_DIR'/miniconda2/envs/env-tensorflow/lib/python2.7/site-packages/google/__init__.py'

if [ -f /tmp/libc6_2.17-0ubuntu5_amd64.deb ]; then
	echo "Skipping Downloading of libc6_2.17-0ubuntu5_amd64.deb exists already"
else
	wget http://launchpadlibrarian.net/137699828/libc6_2.17-0ubuntu5_amd64.deb
fi
if [ -f /tmp/libc6-dev_2.17-0ubuntu5_amd64.deb ]; then
	echo "Skipping Downloading of libc6-dev_2.17-0ubuntu5_amd64.deb exists already"
else
	wget http://launchpadlibrarian.net/137699829/libc6-dev_2.17-0ubuntu5_amd64.deb
fi

cd $TRAFFIC_DIR'/miniconda2/envs/env_traffic/lib/'
mkdir libc6_2.17
cd libc6_2.17
ar p /tmp/libc6_2.17-0ubuntu5_amd64.deb data.tar.gz | tar zx
ar p /tmp/libc6-dev_2.17-0ubuntu5_amd64.deb data.tar.gz | tar zx

source deactivate env_traffic
echo "===> tensorflow and libraries installed"
