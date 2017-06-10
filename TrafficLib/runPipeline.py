import os
import argparse
import subprocess
import shutil
import time
import sys
from fiberfileIO import *
start = time.time()
BLUE_BOLD = "\033[1;34m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"

parser = argparse.ArgumentParser()
parser.add_argument('-output_folder', action='store', dest='output_folder', help='Final output file (.vtk or .vtp)',
                    default='/root/work/DeepLearning/Project/Outputs/')
parser.add_argument('-num_points', action='store', dest='num_points', help='Number of points on each fiber',
                    default='50')
parser.add_argument('-num_landmarks', action='store', dest='num_landmarks', help='Number of landmarks',
                    default='5')
parser.add_argument('-model_fiber', action='store', dest='model_fiber', help='Model Fiber',
                    default="")
# parser.add_argument('-outputTest', action='store', dest='testPickle', help='filepath for the output testing file (.pickle)',
#                     default='DeepLearning/Project/TestData.pickle')
parser.add_argument('-input_folder', action='store', dest='input_folder', help='Input folder containing fibers to test',
                    default='/root/work/DeepLearning/Project/')
parser.add_argument('-trainModel', action='store', dest='trainModel', help='Path to restrore the model '
                                                                         'of the network (must be a .ckpt)',
                    default="/root/work/DeepLearning/Project/Data/CKPT/model3.ckpt")
# parser.add_argument('-trainParam', action='store', dest='trainParam', help='Path to restrore the parameters '
#                                                                          'of the network (must be a .pickle)',
#                     default="/root/work/DeepLearning/Project/Data/TrainParam.pickle")
# parser.add_argument('-atlas', action='store', dest='atlas', help='Atlas of the input fibers'
#                                                                    '(must be a .nrrd)', default="")
parser.add_argument('-landmark_file', action='store', dest='landmark_file', help='Landmarks File (.vt[k/p], or .fcsv)',
                    default="")
parser.add_argument('-root', action='store', dest='root', help='root',
                    default="/work/dprince/")
parser.add_argument('-landmarks', action='store_true', dest='landmarksOn', help='Compute landmarks features ',
                    default=False)
parser.add_argument('-curvature', action='store_true', dest='curvatureOn', help='Compute curvature features ',
                    default=False)
parser.add_argument('-torsion', action='store_true', dest='torsionOn', help='Compute torsion features ',
                    default=False)
parser.add_argument('-store_dir', action='store', dest='store_dir', help='Folder of the test.tfrecords ',
                    default="FibersFeatured")



args = parser.parse_args()
root = args.root
output_folder = check_dir_root(args.output_folder, root)
input_folder = check_dir_root(args.input_folder, root)
num_points = int(args.num_points)
num_landmarks = int(args.num_landmarks)
# testPickle = check_dir_root(args.testPickle, root)
# trainModel = check_file_root(args.trainModel, root)
trainModel = check_dir_root(args.trainModel, root)
# trainParam = check_file_root(args.trainParam, root)
# atlas = args.atlas
landmark_file = check_file_root(args.landmark_file, root)
model_fiber = check_file_root(args.model_fiber, root)
store_dir = args.store_dir

intermediate_folder = "FibersFeatured"

landmarksOn = args.landmarksOn
curvatureOn = args.curvatureOn
torsionOn = args.torsionOn
old_proc = 200

# with open(trainParam, 'rb') as f:
#     save = pickle.load(f)
#     num_labels = save['num_labels']
#     num_points = save['num_points']
#     num_features = save['num_features']
#     name_labels = save['name_labels']

num_features = num_landmarks

if curvatureOn:
    num_features += 1
if torsionOn:
    num_features += 1

make_dataset_py = check_file_root("TRAFIC/src/py/PreProcess/make_dataset.py", root)
make_fiber_feature_py = check_file_root("TRAFIC/src/py/PreProcess/make_fiber_features.py", root)
store_data_py = check_file_root("TRAFIC/src/py/Multiclassification/storeRecords.py", root)
test_network_py = check_file_root("TRAFIC/src/py/Multiclassification/runClassification2.py", root)
fiberfeaturescreator = check_file_root("TRAFIC/src/cxx/fiberfeaturescreator/bin/bin/fiberfeaturescreator", root)

NULL = open(os.devnull, 'w')

# intermediate_folder = "FibersFeatured"


class_list = os.listdir(check_folder(input_folder, True))



cmd_store = ["python", store_data_py, "--test_dir", intermediate_folder, "--num_points", str(num_points),
             "--num_landmarks", str(num_landmarks), "--original_dir", input_folder]


cmd_ffc = ["python", make_fiber_feature_py, "-input", input_folder + "/"+ str(class_list[0]), "-output", intermediate_folder+ "/"+ str(class_list[0]),
                      "-num_points", str(num_points), "-root", root, "-landmark_file", landmark_file, "-model_fiber", model_fiber,
                      "-num_landmarks", str(num_landmarks)]

if landmarksOn:
    cmd_ffc.append("-landmarks")
    cmd_store.append("--landmarks")
if torsionOn:
    cmd_ffc.append("-torsion")
    cmd_store.append("--torsion")
if curvatureOn:
    cmd_ffc.append("-curvature")
    cmd_store.append("--curvature")

print ""
print BLUE_BOLD, "---Preprocessing Dataset...", NC
subprocess.call(cmd_ffc)
step1 = time.time()
print YELLOW, "Preprocessing Dataset took %dh%02dm%02ds" % (convert_time(step1-start)), NC
print ""

print BLUE_BOLD, "---Storing Dataset...", NC
subprocess.call(cmd_store)
step2 = time.time()
print YELLOW, "Storing Dataset took %dh%02dm%02ds" % (convert_time(step2-step1)), NC
print ""
print BLUE_BOLD, "---Testing Dataset...", NC
subprocess.call(["python", test_network_py, "--data_dir", intermediate_folder, "--output_dir", output_folder,
                      "--checkpoint_dir", trainModel ])
                 # "-num_features", str(num_features),
                 # "-num_points", str(num_points), "-num_labels", str(num_labels), "-num_models", str(num_models), "-name_labels", ])

# subprocess.call([fiberfeaturescreator, "--input", output, "--output", output, "-N", str(num_landmarks),
#                   "--landmarksfile", landmark_file, "--model", model_fiber, "--landmarks", "--torsion","--curvature" ], stdout=NULL)
step3 = time.time()
print YELLOW, "Testing Dataset took %dh%02dm%02ds" % (convert_time(step3-step2)), NC
print ""


# print BLUE_BOLD, "---Computing Final Results...", NC
# subprocess.call(["python", fiber_merge_py, "-input", intermediate_folder_2, "-output", output], stdout=NULL)

print RED, "---Copying test.tfrecords", intermediate_folder, NC
shutil.copy(intermediate_folder+"/test.tfrecords", store_dir)
print RED, "---Removing Folder", intermediate_folder, NC
shutil.rmtree(intermediate_folder)
# print RED, "---Removing Folder",intermediate_folder_2, NC
# shutil.rmtree(intermediate_folder_2)



end = time.time()
print YELLOW, "All Process took %dh%02dm%02ds" % (convert_time(end-start)), NC
