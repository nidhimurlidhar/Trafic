import os
import argparse
import subprocess
import shutil
import time
import sys

from makeDataset import make_fiber_feature
from runStore import run_store
from runClassification import run_classification
start = time.time()
BLUE_BOLD = "\033[1;34m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"

parser = argparse.ArgumentParser()
parser.add_argument('--output_dir', action='store', dest='output_dir', help='Final output file (.vtk or .vtp)',
                    default='/root/work/DeepLearning/Project/Outputs/')
parser.add_argument('--data_file', action='store', dest='data_file', help='Input folder containing fibers to test',
                    default='/root/work/DeepLearning/Project/')
parser.add_argument('--checkpoint_dir', action='store', dest='checkpoint_dir', help='Path to restrore the model '
                                                                         'of the network (must be a .ckpt)',
                    default="/root/work/DeepLearning/Project/Data/CKPT/model3.ckpt")
parser.add_argument('--landmark_file', action='store', dest='landmark_file', help='Landmarks File (.vt[k/p], or .fcsv)',
                    default="")
parser.add_argument('--summary_dir', action='store', dest='summary_dir', help='Summary directory ',
                    default="")
parser.add_argument('--fiber_name', action='store', dest='fiber_name', help='Name of the fiber for the biclassification case ',
                    default="")


def run_pipeline_eval(data_file, output_dir, checkpoint_dir,  summary_dir, landmark_file='', num_landmarks=32, fiber_name="Fiber", is_preprocessed=False):
  sys.stdout.flush()
  currentPath = os.path.dirname(os.path.abspath(__file__))

  src_dir = os.path.dirname(data_file)
  src_name = os.path.basename(data_file)
  tmp_dir = os.path.join(currentPath, 'tmp_dir_eval')
  tmp_file = os.path.join(tmp_dir, src_name)

  if not os.path.isdir(tmp_dir):
      os.makedirs(tmp_dir)

  if is_preprocessed:
    print("---Classifying Dataset...")
    run_classification(data_file, output_dir, checkpoint_dir, summary_dir, fiber_name=data_file)
  else:
    print ("---Creating features...")
    make_fiber_feature(data_file, tmp_file, landmark_file, num_landmarks=num_landmarks)
    print ("---Classifying Dataset...")
    run_classification(tmp_file, output_dir, checkpoint_dir, summary_dir, fiber_name=fiber_name)

  shutil.rmtree(tmp_dir)

def main():
  args = parser.parse_args()
  output_dir = args.output_dir
  data_file = args.data_file
  checkpoint_dir = args.checkpoint_dir
  landmark_file = args.landmark_file
  summary_dir = args.summary_dir
  fiber_name = args.fiber_name

  run_pipeline_eval(data_file, output_dir, checkpoint_dir, summary_dir, landmark_file, 32, fiber_name)

if __name__ == '__main__':
  try:
    main()
  except e:
    print ('ERROR, EXCEPTION CAUGHT')
    print(str(e))
    import traceback
    traceback.print_exc()