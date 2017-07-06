#!/bin/bash

help_display () {
	echo -e " Need 3 arguments : "
	echo -e "- directory where miniconda will be installed"
	echo "- python version (only supports 2.7 and 3.6)"
	echo "- Number of bits (64 or 32)"
}
check_args(){

	dir=$1
	py_version=$2
	n_bit=$3

	test ! -d $dir && echo -e "Directory $dir dosen't exist $NC" && exit
	if [ $py_version != '2.7' ] && [ $py_version != '3.6' ]
	then
		echo "Version of Python non valid"
		help_display
		exit
	fi
	if [ $n_bit != '64' ] && [ $n_bit != '32' ]
	then
		echo "Number of bit non valid"
		help_display
		exit
	fi

}
envInstall () {

	TRAFIC_DIR=$1
	PY_VERSION=$2

	N_BIT=$3

	if [ $PY_VERSION == '2.7' ];then
		py_v='2'
	elif [ $PY_VERSION == '3.6' ];then
		py_v='3'
	fi

	if [ $N_BIT == '64' ];then
		n_bit='_64'
	elif [ $N_BIT == '32' ];then
		n_bit=''
	fi

	# Get the bash installer for linux 64bit python 2.7
	echo "I. Conda installation"
	if [ -f Miniconda"$py_v"-latest-Linux-x86"$n_bit".sh ]; then
		echo "Skipping Downloading of Miniconda installer exists already"
	else
		echo "Download Miniconda installer"
		wget https://repo.continuum.io/miniconda/Miniconda"$py_v"-latest-Linux-x86"$n_bit".sh
	fi
	# We install miniconda
	bash Miniconda"$py_v"-latest-Linux-x86"$n_bit".sh -b -p $TRAFIC_DIR'/miniconda2/'
	echo "===> Conda installed"

	# We add the path of

	if [ $py_v == '2' ];then
		PY_V='2.7'

	if [ $py_v == '3' ];then
		PY_V='3.6'
	export PATH=$TRAFIC_DIR'/miniconda2/bin/':$PATH
	export PYTHONPATH=$TRAFIC_DIR'/miniconda2/lib/':$TRAFIC_DIR'/miniconda2/lib/python'$PY_V'/site-packages/':$PYTHONPATH

	echo "II. Create environment to run tensorflow"
	conda create -y -n env_trafic python=$PY_VERSION
	echo "===> environment created"

	echo "III. Install tensorflow and libraries into environment"
	source activate env_trafic
	conda install -y -c conda-forge tensorflow
	conda install -y -c anaconda vtk
	touch $TRAFIC_DIR'/miniconda2/envs/env_trafic/lib/python2.7/site-packages/google/__init__.py'

	if [ -f libc6_2.17-0ubuntu5_amd64.deb ]; then
		echo "Skipping Downloading of libc6_2.17-0ubuntu5_amd64.deb exists already"
	else
		wget http://launchpadlibrarian.net/137699828/libc6_2.17-0ubuntu5_amd64.deb
	fi
	if [ -f libc6-dev_2.17-0ubuntu5_amd64.deb ]; then
		echo "Skipping Downloading of libc6-dev_2.17-0ubuntu5_amd64.deb exists already"
	else
		wget http://launchpadlibrarian.net/137699829/libc6-dev_2.17-0ubuntu5_amd64.deb
	fi

	cd $TRAFIC_DIR'/miniconda2/envs/env_trafic/lib/'
	mkdir libc6_2.17
	cd libc6_2.17
	ar p /tmp/libc6_2.17-0ubuntu5_amd64.deb data.tar.gz | tar zx
	ar p /tmp/libc6-dev_2.17-0ubuntu5_amd64.deb data.tar.gz | tar zx
	rm Miniconda"$py_v"-latest-Linux-x86"$n_bit".sh
	rm libc6_2.17-0ubuntu5_amd64.deb
	rm libc6-dev_2.17-0ubuntu5_amd64.deb
	source deactivate env_trafic
	echo "===> tensorflow and libraries installed"
}

case $# in 
	
	3)
	check_args $1 $2 $3
	envInstall $1 $2 $3
	;;

	*)
	help_display
	;;
esac
