import os
import argparse
import subprocess
import shutil
import time
import sys
# from fiberfileIO import *
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
parser.add_argument('--multiclass', action='store_true', dest='multiclass', help='Enable the multiclassification training',
                    default=False)
parser.add_argument('--biclass', action='store_true', dest='biclass', help='Enable the biclassification training',
                    default=False)
parser.add_argument('--summary_dir', action='store', dest='summary_dir', help='Summary directory ',
                    default="")
parser.add_argument('--fiber_name', action='store', dest='fiber_name', help='Summary directory ',
                    default="")


def run_pipeline_eval(data_file, output_dir, landmark_file, checkpoint_dir, summary_dir, num_landmarks, fiber_name="Fiber"):
  print "---Preprocessing Dataset..."
  sys.stdout.flush()
  currentPath = os.path.dirname(os.path.abspath(__file__))
  make_dataset_py = os.path.join(currentPath, 'makeDataset.py')
  store_py = os.path.join(currentPath, 'runStore.py')
  classification_py = os.path.join(currentPath, 'runClassification.py')
  env_dir = os.path.join(currentPath, "..", "miniconda2")
  prefix = os.path.join(env_dir,"envs","env-tensorflow","lib","libc6_2.17","lib","x86_64-linux-gnu","ld-2.17.so")
  pythonPath = os.path.join(env_dir,"bin","python")

  src_dir = os.path.dirname(data_file)
  src_name = os.path.basename(data_file)
  tmp_dir = os.path.join(currentPath, 'tmp_dir_eval')
  tmp_file = os.path.join(tmp_dir, src_name)
  make_fiber_feature(data_file, tmp_file, landmark_file, num_landmarks=num_landmarks, classification=True)
  # print subprocess.Popen(cmd_make_dataset, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

  print "---Storing Dataset..."
  sys.stdout.flush()
  cmd_store = [prefix, pythonPath, store_py, "--test_dir", tmp_dir, "--original_dir", src_dir,"--num_landmarks",str(num_landmarks)]
  out, err = subprocess.Popen(cmd_store, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
  print("\nout : " + str(out) + "\nerr : " + str(err))

  # run_store(test_dir=tmp_dir, original_dir=src_dir, num_landmarks=num_landmarks)

  print "---Classifying Dataset..."
  cmd_class = [prefix, pythonPath, classification_py, "--data_dir",tmp_dir,"--output_dir",output_dir,"--checkpoint_dir",checkpoint_dir,"--summary_dir",summary_dir, "--fiber_name", fiber_name]
  if num_landmarks == 32:
    cmd_class.append("--multiclass")
  out, err = subprocess.Popen(cmd_class, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
  print("\nout : " + str(out) + "\nerr : " + str(err))

  shutil.rmtree(tmp_dir)

def main():
  args = parser.parse_args()
  output_dir = args.output_dir
  data_file = args.data_file
  checkpoint_dir = args.checkpoint_dir
  landmark_file = args.landmark_file
  multiclass = args.multiclass
  biclass = args.biclass
  summary_dir = args.summary_dir
  fiber_name = args.fiber_name
  if multiclass:
    run_pipeline_eval(data_file, output_dir, landmark_file, checkpoint_dir, summary_dir, 32, fiber_name)
  elif biclass:
    run_pipeline_eval(data_file, output_dir, landmark_file, checkpoint_dir, summary_dir, 5, fiber_name)


if __name__ == '__main__':
  try:
    main()
  except Exception, e:
    print ('ERROR, EXCEPTION CAUGHT')
    print str(e)
    import traceback
    traceback.print_exc()