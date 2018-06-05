import numpy as np
import argparse
import os
from os import path, sys
from shutil import rmtree
import subprocess
import csv

TRAFIC_LIB_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), "TraficLib")
sys.path.append(TRAFIC_LIB_DIR)

from runClassification import run_classification
from fiber_preprocessing import fiber_preprocessing

parser = argparse.ArgumentParser()
parser.add_argument('--input_csv', action='store', dest='input_csv', help='Input csv with each line being "input,output,summary,checkpoint,displacement_field,landmarks". If displacement and landmarks are not specified, the fiber will be assumed to have been preprocessed', default='')
parser.add_argument('--preprocessed_fiber', action='store', dest='preprocessed_fiber', help='Input fiber with feature informations. The preprocessing pipeline will be skipped', default='')
parser.add_argument('--input', action='store', dest='input', help='Input fiber to classify', default='')
parser.add_argument('--output_dir', action='store', dest='output_dir', help='Output directory', default='')
parser.add_argument('--summary', action='store', dest='summary', help='Output summary directory. If not specified, will be set as the same as the output directory', default='')
parser.add_argument('--displacement', action='store', dest='displacement', help= 'Displacement field to reference atlas', default='')
parser.add_argument('--landmarks', action='store', dest='landmarks', help='landmarks file (.fcsv) for reference atlas', default='')
parser.add_argument('--checkpoint_dir', action='store', dest='checkpoint_dir', help='Tensorflow checkpoint directory', default='')

def parse_csv_input(filename):
    with open(filename, 'r') as csvfile:
        input_list = csv.reader(csvfile)
        array = []
        for row in input_list:
            array.append(row)
        return array

def runClassification(input_fiber,  output_dir, summary_dir, checkpoint_dir, deformation_field='', landmarks_file='', is_preprocessed=False):
    if is_preprocessed:
        run_classification(input_fiber, output_dir, checkpoint_dir, summary_dir, fiber_name=input_fiber)
    else:

        default_parameters = {
            'num_points'   : 50,
            'num_landmarks': 32,
            'use_landmarks': True,
            'use_curvature': True,
            'use_torsion'  : True
        }

        currentPath = os.path.dirname(os.path.abspath(__file__))

        tmp_dir = os.path.join(currentPath, "tmp_dir_fiber")
        if not os.path.isdir(tmp_dir):
          os.makedirs(tmp_dir)

        tmp_fiber_file = os.path.join(tmp_dir, os.path.basename(input_fiber))

        fiber_preprocessing(input_fiber=input_fiber, output_fiber=tmp_fiber_file, deformation_field=deformation_field, landmarks=landmarks_file, parameters=default_parameters)
        run_classification(tmp_fiber_file, output_dir, checkpoint_dir, summary_dir, fiber_name=input_fiber)

    return

def main():
    args = parser.parse_args()


    if args.input_csv:
        input_list = parse_csv_input(args.input_csv)
        for row in input_list:
            print (row)
            print (len(row))
            if len(row) == 4:
                runClassification(input_fiber=row[0], output_dir=row[1], summary_dir=row[3], checkpoint_dir=row[2], is_preprocessed=True)
            elif len(row) == 6:
                runClassification(input_fiber=row[0], output_dir=row[1], summary_dir=row[3], checkpoint_dir=row[2], deformation_field=row[4], landmarks_file=row[5], is_preprocessed=False)
            else:
                print('Invalid number of parameters in csv line, skipping...')
        return
    
    
    summary = args.summary
    if not summary:
        summary = args.output
    
    if args.preprocessed_fiber:
        runClassification(input_fiber=args.preprocessed_fiber, output_dir=args.output_dir, summary_dir=summary, checkpoint_dir=args.checkpoint_dir, is_preprocessed=True)
        return
    
    runClassification(input_fiber=args.input, output_dir=args.output_dir, summary_dir=args.summary, checkpoint_dir=args.checkpoint_dir, deformation_field=args.displacement, landmarks_file=args.landmarks, is_preprocessed=False)

    return

if __name__ == '__main__':
    main()
