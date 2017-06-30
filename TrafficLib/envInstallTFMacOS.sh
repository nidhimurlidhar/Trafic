#!/bin/bash

help_display () {
	echo -e " Need 2 arguments : "
	echo -e "- directory where miniconda will be installed"
	echo "- python version (only supports 2.7 and 3.6)"
	echo "Only supports 64-bit"
}
check_args(){

	dir=$1
	py_version=$2

	test ! -d $dir && echo -e "Directory $dir dosen't exist $NC" && exit
	if [ $py_version != '2.7' ] && [ $py_version != '3.6' ]
	then
		echo "Version of Python non valid"
		help_display
		exit
	fi

}
envInstall () {

	TRAFFIC_DIR=$1
	PY_VERSION=$2

	if [ $PY_VERSION == '2.7' ];then
		py_v='2'
	elif [ $PY_VERSION == '3.6' ];then
		py_v='3'
	fi

	cd /tmp

	# Get the bash installer for linux 64bit python 2.7
	echo "I. Conda installation"
	if [ -f Miniconda"$py_v"-latest-MacOSX-x86_64.sh ]; then
		echo "Skipping Downloading of Miniconda installer exists already"
	else
		echo "Download Miniconda installer"
		curl -O https://repo.continuum.io/miniconda/Miniconda"$py_v"-latest-MacOSX-x86_64.sh
	fi
	# We install miniconda
	bash /tmp/Miniconda"$py_v"-latest-MacOSX-x86_64.sh -b -p $TRAFFIC_DIR'/miniconda/'
	echo "===> Conda installed"

	# We add to path miniconda/bin directory
	export PATH=$TRAFFIC_DIR'/miniconda/bin/':$PATH

	echo "II. Create environment to run tensorflow"
	conda create -y -n env_traffic python=$PY_VERSION
	echo "===> environment created"

	echo "III. Install tensorflow and libraries into environment"
	source activate env_traffic
	conda install -y -c conda-forge tensorflow
	conda install -y -c anaconda vtk
	touch $TRAFFIC_DIR'/miniconda/envs/env_traffic/lib/python2.7/site-packages/google/__init__.py'
	source deactivate env_traffic
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