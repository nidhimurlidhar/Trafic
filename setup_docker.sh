TRAFIC_DIR=/Trafic
TENSORFLOW_DIR="/usr/local/lib/python2.7/dist-packages/tensorflow/"

source $TRAFIC_DIR/miniconda2/bin/activate env_trafic
python -c "import os;os.sys.path.insert(0,'$TENSORFLOW_DIR')"
conda install -y libglu

conda install -y libsm-cos6-x86_64
ln -s $TRAFIC_DIR/miniconda2/envs/env_trafic/x86_64-conda_cos6-linux-gnu/sysroot/usr/lib64/libSM.so.6 $TRAFIC_DIR/miniconda2/envs/env_trafic/lib/libSM.so.6
conda install -y libice-cos6-x86_64
ln -s $TRAFIC_DIR/miniconda2/envs/env_trafic/x86_64-conda_cos6-linux-gnu/sysroot/usr/lib64/libICE.so.6 $TRAFIC_DIR/miniconda2/envs/env_trafic/lib/libICE.so.6
conda install -y libXt-cos6-x86_64
ln -s $TRAFIC_DIR/miniconda2/envs/env_trafic/x86_64-conda_cos6-linux-gnu/sysroot/usr/lib64/libXt.so.6 $TRAFIC_DIR/miniconda2/envs/env_trafic/lib/libXt.so.6
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:$TRAFIC_DIR/miniconda2/envs/env_trafic/lib"

source $TRAFIC_DIR/miniconda2/bin/deactivate

export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:$TRAFIC_DIR/miniconda2/envs/env_trafic/lib"