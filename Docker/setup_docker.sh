TRAFIC_DIR=/Trafic
TENSORFLOW_DIR="/usr/local/lib/python2.7/dist-packages/tensorflow/"

source $TRAFIC_DIR/miniconda2/bin/activate env_trafic
export PYTHONPATH=$TENSORFLOW_DIR
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:$TRAFIC_DIR/miniconda2/envs/env_trafic/lib"
