import numpy as np
import argparse
import os
import tensorflow as tf
from os import path, sys
from shutil import rmtree
import subprocess
import csv

TRAFIC_LIB_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), "TraficLib")
sys.path.append(TRAFIC_LIB_DIR)

# from envInstallTF import runMaybeEnvInstallTF
from PipelineEval import run_pipeline_eval

flags = tf.app.flags
FLAGS = flags.FLAGS

flags.DEFINE_string('input_csv', '', 'Input csv with each line being "input_fiber_file,output_directory,checkpoint_dir,summary_dir,displacement_field". Other parameters will be ignored if ths is set')
flags.DEFINE_string('preprocessed_fiber', '', 'Input fiber with feature informations. The preprocessing pipeline will be skipped')
flags.DEFINE_string('input', '', 'Input fiber to classify')
flags.DEFINE_string('output', '', 'Output directory')
flags.DEFINE_string('summary', '', 'Output summary directory')
flags.DEFINE_string('displacement', '', 'Displacement field to PED_1yr-2yr atlas')
flags.DEFINE_string('checkpoints', '', 'Tensorflow checkpoint directory')

class TraficMultiLogic():
  def parse_csv_input(self, filename):
    with open(filename, 'rb') as csvfile:
        input_list = csv.reader(csvfile)
        array = []
        for row in input_list:
            array.append(row)
        return array

  def runClassification(self, data_file,  model_dir, sum_dir, output_dir, dF_Path='', is_preprocessed=False):
    
    if is_preprocessed:
        run_pipeline_eval(data_file, output_dir, model_dir, sum_dir, is_preprocessed=True)
    else:
        # runMaybeEnvInstallTF()
        currentPath = os.path.dirname(os.path.abspath(__file__))
        env_dir = os.path.join(currentPath, "..", "miniconda2") #could be fixed paths within docker
        cli_dir = os.path.join(currentPath, "..","..","cli-modules")

        polydatatransform = os.path.join(cli_dir, "polydatatransform")
        lm_ped = os.path.join(currentPath,"Resources", "Landmarks", "landmarks_32pts_afprop.fcsv")
        tmp_dir = os.path.join(currentPath, "tmp_dir_lm_class")
        if not os.path.isdir(tmp_dir):
          os.makedirs(tmp_dir)
        new_lm_path = os.path.join(tmp_dir, "lm_class.fcsv")

        cmd_polydatatransform = [polydatatransform, "--invertx", "--inverty", "--fiber_file", lm_ped, "-D", dF_Path, "-o", new_lm_path]
        print(cmd_polydatatransform)
        out, err = subprocess.Popen(cmd_polydatatransform, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print("\nout : " + str(out))
        run_pipeline_eval(data_file, output_dir, model_dir, sum_dir, new_lm_path)
    return

def main():
    logic = TraficMultiLogic()

    summary = FLAGS.summary
    if not summary:
        summary = FLAGS.output

    if FLAGS.preprocessed_fiber:
        logic.runClassification(FLAGS.preprocessed_fiber, FLAGS.checkpoints, summary, FLAGS.output, is_preprocessed=True)
        return

    if FLAGS.input_csv:
        input_list = logic.parse_csv_input(FLAGS.input_csv)
        for row in input_list:
            logic.runClassification(row[0], row[2], row[3], row[1], row[4])
        return

    logic.runClassification(FLAGS.input, FLAGS.checkpoints, FLAGS.summary, FLAGS.output, FLAGS.displacement)
    
    return

if __name__ == '__main__':
    main()
