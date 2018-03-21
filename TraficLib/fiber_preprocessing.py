import numpy as np
import argparse
import os
import tensorflow as tf
from os import path, sys
from shutil import rmtree
import subprocess
import csv
import os
import argparse
import subprocess
import shutil
import time
import sys

from makeDataset import make_fiber_feature
from runStore import run_store

TRAFIC_LIB_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), "TraficLib")
sys.path.append(TRAFIC_LIB_DIR)
print path.join(TRAFIC_LIB_DIR)
from envInstallTF import runMaybeEnvInstallTF


flags = tf.app.flags
FLAGS = flags.FLAGS

flags.DEFINE_string('input', '', 'Input fiber to classify')
flags.DEFINE_string('input_csv', '', 'Input csv with each line being "input_fiber, deformation_field, output_fiber"')
flags.DEFINE_string('output', '', 'Output fiber path')
flags.DEFINE_string('displacement', '', 'Displacement field to atlas used for training')
flags.DEFINE_integer('number_points', 50, 'Number of points to sample')
flags.DEFINE_integer('number_landmarks', 32, 'Number of landmarks to use')
flags.DEFINE_boolean('use_landmarks', True, 'Should landmarks be used')
flags.DEFINE_boolean('use_curvature', True, 'Should curvature data be used')
flags.DEFINE_boolean('use_torsion', True, 'Should torsion data be use')


def parse_csv_input(filename):
    with open(filename, 'rb') as csvfile:
        input_list = csv.reader(csvfile)
        array = []
        for row in input_list:
            array.append(row)
        return array

def fiber_preprocessing(input_fiber, deformation_field, output_fiber, parameters ):
    print output_fiber
    runMaybeEnvInstallTF()
    currentPath = os.path.dirname(os.path.abspath(__file__))
    env_dir = os.path.join(currentPath, "..", "miniconda2") #could be fixed paths within docker
    cli_dir = os.path.join(currentPath, "/", "cli-modules")

    polydatatransform = os.path.join(cli_dir, "polydatatransform")
    lm_ped = os.path.join(currentPath,"Resources", "Landmarks", "landmarks_32pts_afprop.fcsv")

    tmp_dir = os.path.join(currentPath, "tmp_dir_lm_class")
    if not os.path.isdir(tmp_dir):
      os.makedirs(tmp_dir)
    new_lm_path = os.path.join(tmp_dir, "lm_class.fcsv")

    if not os.path.isdir(os.path.dirname(output_fiber)) and not os.path.dirname(output_fiber):
      os.makedirs(os.path.dirname(output_fiber))

    cmd_polydatatransform = [polydatatransform, "--invertx", "--inverty", "--fiber_file", lm_ped, "-D", deformation_field, "-o", new_lm_path]
    out, err = subprocess.Popen(cmd_polydatatransform, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    make_fiber_feature(input_fiber, output_fiber, new_lm_path, 
        num_points=parameters['num_points'],
        num_landmarks=parameters['num_landmarks'],
        lmOn=parameters['use_landmarks'],
        torsOn=parameters['use_torsion'],
        curvOn=parameters['use_curvature'])

def main():

    if FLAGS.input_csv != '':
        input_list = logic.parse_csv_input(FLAGS.input_csv)
        for row in input_list:
            fiber_preprocessing(row[0], row[1], row[2])
        return

    parameters = {
        'num_points'   : FLAGS.number_points,
        'num_landmarks': FLAGS.number_landmarks,
        'use_landmarks': FLAGS.use_landmarks,
        'use_curvature': FLAGS.use_curvature,
        'use_torsion'  : FLAGS.use_torsion
    }

    fiber_preprocessing(FLAGS.input,  FLAGS.displacement, FLAGS.output, parameters)
    
    return

if __name__ == '__main__':
    main()
