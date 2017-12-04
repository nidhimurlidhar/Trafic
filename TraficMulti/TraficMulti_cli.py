import numpy as np
import argparse
import os
import tensorflow as tf
from os import path, sys
from shutil import rmtree
import subprocess


TRAFIC_LIB_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), "TraficLib")
sys.path.append(TRAFIC_LIB_DIR)
print path.join(TRAFIC_LIB_DIR)
from envInstallTF import runMaybeEnvInstallTF


flags = tf.app.flags
FLAGS = flags.FLAGS

flags.DEFINE_string('input', '', 'Input fiber to classify')
flags.DEFINE_string('output', '', 'Output directory')
flags.DEFINE_string('summary', '', 'Output summary directory')
flags.DEFINE_string('displacement', '', 'Displacement field to PED_1yr-2yr atlas')
flags.DEFINE_string('checkpoints', '', 'Tensorflow checkpoint directory')

class TraficMultiLogic():
  def runClassification(self, data_file,  model_dir, sum_dir, output_dir, dF_Path):
    runMaybeEnvInstallTF() ### todo : block while the installation is running. no point in executing the rest of the function while installing at the same time
    currentPath = os.path.dirname(os.path.abspath(__file__))
    env_dir = os.path.join(currentPath, "..", "miniconda2")
    cli_dir = os.path.join(currentPath, "..","cli-modules")

    # polydatatransform = os.path.join(cli_dir, "polydatatransform")
    polydatatransform = "/work/boucaud/builds/niral_utilities/bin/polydatatransform"
    lm_ped = os.path.join(currentPath,"Resources", "Landmarks", "landmarks_32pts_afprop.fcsv") ###CHANGED HERE
    tmp_dir = os.path.join(currentPath, "tmp_dir_lm_class")
    if not os.path.isdir(tmp_dir):
      os.makedirs(tmp_dir)
    new_lm_path = os.path.join(tmp_dir, "lm_class.fcsv")

    cmd_polydatatransform = [polydatatransform, "--invertx", "--inverty", "--fiber_file", lm_ped, "-D", dF_Path, "-o", new_lm_path]
    print(cmd_polydatatransform)
    out, err = subprocess.Popen(cmd_polydatatransform, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print("\nout : " + str(out))

    pipeline_eval_py = os.path.join(TRAFIC_LIB_DIR, "PipelineEval.py")
    cmd_py = str(pipeline_eval_py) + ' --data_file ' + str(data_file) + ' --multiclass --summary_dir ' + str(sum_dir)+ ' --checkpoint_dir ' + str(model_dir) + ' --output_dir ' + str(output_dir) + ' --landmark_file ' + str(new_lm_path)
    cmd_virtenv = 'ENV_DIR="'+str(env_dir)+'";'
    cmd_virtenv = cmd_virtenv + 'export PYTHONPATH=$ENV_DIR/envs/env_trafic/lib/python2.7/site-packages:$ENV_DIR/lib/:$ENV_DIR/lib/python2.7/lib-dynload/:$ENV_DIR/lib/python2.7/:$ENV_DIR/lib/python2.7/site-packages/:$PYTHONPATH;'
    cmd_virtenv = cmd_virtenv + 'export PATH=$ENV_DIR/bin/:$PATH;'
    cmd_virtenv = cmd_virtenv + 'source activate env_trafic;'
    cmd_virtenv = cmd_virtenv + 'LD_LIBRARY_PATH=$ENV_DIR/envs/env_trafic/lib/libc6_2.17/lib/:$ENV_DIR/envs/env_trafic/lib/libc6_2.17/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH $ENV_DIR/envs/env_trafic/lib/libc6_2.17/lib/x86_64-linux-gnu/ld-2.17.so `which python` '
    cmd_pipeline_class = cmd_virtenv + str(cmd_py) + ';'
    print(str(cmd_pipeline_class))
    cmd = ["bash", "-c", str(cmd_pipeline_class)]
    log_dir = os.path.join(sum_dir,"Logs")
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    out = open(os.path.join(log_dir,"training_out.txt"), "wb")
    err = open(os.path.join(log_dir,"training_err.txt"), "wb")
    proc = subprocess.Popen(cmd, stdout=out, stderr=err)
    proc.wait()
    print("\nout : " + str(out) + "\nerr : " + str(err))    
    rmtree(tmp_dir)
    return

def main():
    print FLAGS.input
    print FLAGS.output
    print FLAGS.summary
    print FLAGS.displacement
    print FLAGS.checkpoints
    logic = TraficMultiLogic()
    logic.runClassification(FLAGS.input, FLAGS.checkpoints, FLAGS.summary, FLAGS.output, FLAGS.displacement)
    
    return

if __name__ == '__main__':
    main()
