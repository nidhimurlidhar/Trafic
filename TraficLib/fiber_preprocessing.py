import numpy as np
import os
from os import path, sys
import subprocess
import csv
import sys
import argparse
import shutil

from makeDataset import make_fiber_feature
from runStore import run_store

TRAFIC_LIB_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), "TraficLib")
sys.path.append(TRAFIC_LIB_DIR)
print (path.join(TRAFIC_LIB_DIR))

parser = argparse.ArgumentParser()
parser.add_argument('--input_csv', action='store', dest='input_csv', help='Input csv with each line being "input_fiber, output_fiber, deformation_field, landmarks file"', default='')
parser.add_argument('--input', action='store', dest='input', help='Input fiber to preprocess', default='')
parser.add_argument('--output', action='store', dest='output', help='Output preprocessed fiber file', default='')
parser.add_argument('--displacement', action='store', dest='displacement', help= 'Displacement field to reference atlas', default='')
parser.add_argument('--landmarks', action='store', dest='landmarks', help='landmarks file (.fcsv)', default='')

parser.add_argument('--number_points', type=int, action='store', dest='number_points', help='Number of points to sample', default=50)
parser.add_argument('--number_landmarks', type=int, action='store', dest='number_landmarks', help='Number of landmarks to use', default=32)

parser.add_argument('--no_landmarks', action='store_true', dest='no_landmarks', help='Should landmarks be used (true if flag not specified). Note that the training needs to be done with the same parameters')
parser.add_argument('--no_curvature', action='store_true', dest='no_curvature', help='Should curvature be used (true if flag not specified). Note that the training needs to be done with the same parameters')
parser.add_argument('--no_torsion', action='store_true', dest='no_torsion', help='Should torsion be used (true if flag not specified). Note that the training needs to be done with the same parameters')

def parse_csv_input(filename):
    with open(filename, 'r') as csvfile:
        input_list = csv.reader(csvfile)
        array = []
        for row in input_list:
            array.append(row)
        return array

def fiber_preprocessing(input_fiber, output_fiber, deformation_field, landmarks, parameters ):
    currentPath = os.path.dirname(os.path.abspath(__file__))
    env_dir = os.path.join(currentPath, "..", "miniconda2") #could be fixed paths within docker
    cli_dir = os.path.join(currentPath, "/", "cli-modules")

    if landmarks == '':
        print('No landmark file specified, exiting...')
        return

    tmp_dir = os.path.join(currentPath, "tmp_dir_lm_class")
    if not os.path.isdir(tmp_dir):
      os.makedirs(tmp_dir)
    new_lm_path = os.path.join(tmp_dir, "lm_class.fcsv")
    
    if not os.path.isdir(os.path.dirname(output_fiber)) and not os.path.dirname(output_fiber):
      os.makedirs(os.path.dirname(output_fiber))

    if deformation_field == '':
        print('No def field specified.. Using landmarks as is')
        shutil.copyfile(landmarks, new_lm_path)
    else:
        polydatatransform = os.path.join(cli_dir, "polydatatransform")
        
        cmd_polydatatransform = [polydatatransform, "--invertx", "--inverty", "--fiber_file", landmarks, "-D", deformation_field, "-o", new_lm_path]
        out, err = subprocess.Popen(cmd_polydatatransform, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    make_fiber_feature(input_fiber, output_fiber, new_lm_path, 
        number_points=parameters['num_points'],
        number_landmarks=parameters['num_landmarks'],
        landmarksOn=parameters['use_landmarks'],
        torsionOn=parameters['use_torsion'],
        curvatureOn=parameters['use_curvature'])

def main():
    args = parser.parse_args()
    parameters = {
        'num_points'   : args.number_points,
        'num_landmarks': args.number_landmarks,
        'use_landmarks': not args.no_landmarks,
        'use_curvature': not args.no_curvature,
        'use_torsion'  : not args.no_torsion
    }

    if args.input_csv != '':
        input_list = parse_csv_input(args.input_csv)
        for row in input_list:
            if len(row) != 4:
                print('Unable to read csv line, skipping...')
                continue
            fiber_preprocessing(input_fiber=row[0], output_fiber=row[1], deformation_field=row[2],  landmarks=row[3], parameters=parameters)
        return

    fiber_preprocessing(input_fiber=args.input,  output_fiber=args.output, deformation_field=args.displacement, landmarks=args.landmarks, parameters=parameters)

    
    return

if __name__ == '__main__':
    main()
