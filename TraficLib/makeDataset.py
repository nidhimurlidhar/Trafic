import argparse
import subprocess
from os import sys, path
# sys.path.append("/root/work//TRAFIC/src/py/utils/")
# sys.path.append("/root/work/TRAFIC/src/py/")

from fiberfileIO import *
if not hasattr(sys, 'argv'):
    sys.argv  = ['']

    
parser = argparse.ArgumentParser()
parser.add_argument('--input_folder', action='store', dest='input_folder', help='Input directory ',
                    default="")
parser.add_argument('--output_folder', action='store', dest='output_folder', help='Output Directory ',
                    default="")
parser.add_argument('--landmark_file', action='store', dest='landmark_file', help='Landmarks File (.vt[k/p], or .fcsv)',
                    default="")
parser.add_argument('--num_points', action='store', dest='num_points', help='Number of points for the sampling',
                    default=50)
parser.add_argument('--model_fiber', action='store', dest='model_fiber', help='Model Fiber',
                    default="")
parser.add_argument('--num_landmarks', action='store', dest='num_landmarks', help='Number of landmarks',
                    default=5)

# parser.add_argument('-root', action='store', dest='root', help='root',
#                     default="/work/dprince/")
parser.add_argument('--landmarks', action='store_true', dest='landmarksOn', help='Compute landmarks features ',
                    default=True)
parser.add_argument('--curvature', action='store_true', dest='curvatureOn', help='Compute curvature features ',
                    default=True)
parser.add_argument('--torsion', action='store_true', dest='torsionOn', help='Compute torsion features ',
                    default=True)




def run_make_dataset(input_folder, output_folder, landmark_file="", num_landmarks=5, num_points=50, model_fiber=""
, landmarksOn=True, curvatureOn=True, torsionOn=True):

    sys.stdout.flush()
    class_list = os.listdir(check_folder(input_folder, True))
    # print "Input Dir", input_folder
    # print "Input Dir List", input_folder_list
    for _, class_fib in enumerate(class_list):
        class_path = os.path.join(input_folder, class_fib)
        fiber_list = os.listdir(check_folder(class_path, True))
        for _, fiber in enumerate(fiber_list):
            input_fiber = os.path.join(class_path, fiber)
            output_fiber = os.path.join(check_folder(output_folder,True), class_fib)
            output_fiber = os.path.join(output_fiber, fiber)
            while os.path.isfile(output_fiber): # if a fiber already exists with the same name, we simply append a _1 to the new fiber
                name, ext = os.path.splitext(output_fiber)
                output_fiber = name + "_1" + ext
            make_fiber_feature(input_fiber, output_fiber, landmark_file, num_points=num_points, num_landmarks=num_landmarks, model_fiber=model_fiber, lmOn=landmarksOn,torsOn=torsionOn,curvOn=curvatureOn)

def make_fiber_feature(input_fiber, output_fiber, landmark_file, num_points=50, num_landmarks=5, model_fiber="", lmOn=True, torsOn=True, curvOn=True):
    currentPath = os.path.dirname(os.path.abspath(__file__))
    CLI_DIR = os.path.join(currentPath, '/',"cli-modules")
    # CLI_DIR = os.path.join(currentPath, "..","..","cli-modules")

    env_dir = os.path.join(currentPath, "..", "miniconda2")
    fibersampling = os.path.join(CLI_DIR, "fibersampling")
    fiberfeaturescreator = os.path.join(CLI_DIR, "fiberfeaturescreator")

    cmd_sampling = [fibersampling,"--input", check_file(input_fiber), "--output",
             check_path(output_fiber, True), "-N", str(num_points)]

    print (cmd_sampling)
    out, err = subprocess.Popen(cmd_sampling, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print("\nout : " + str(out))
    if err != "":
        print("\nerr : " + str(err))

    cmd_ffc = [fiberfeaturescreator, "--input", check_file(output_fiber), "--output",
                 check_path(output_fiber), "-N", str(num_landmarks), "--landmarksfile", landmark_file]
    
    if model_fiber != '':
        cmd_ffc.append("--model", model_fiber)
    if lmOn:
        cmd_ffc.append("--landmarks")
    if torsOn:
        cmd_ffc.append("--torsion")
    if curvOn:
        cmd_ffc.append("--curvature")
    print (cmd_ffc)
    out, err = subprocess.Popen(cmd_ffc, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print("\nout : " + str(out))
    
    if err != "":
        print("\nerr : " + str(err))
    return

def main():

    args = parser.parse_args()
    # root = args.root
    num_landmarks = int(args.num_landmarks)
    num_points = int(args.num_points)
    model_fiber = args.model_fiber
    landmark_file = args.landmark_file
    output_folder = args.output_folder
    input_folder = args.input_folder
    landmarksOn = args.landmarksOn 
    curvatureOn = args.curvatureOn
    torsionOn = args.torsionOn

    # Avec root
    # run_make_dataset(input_folder, output_folder, landmark_file, root, num_landmarks, num_points, model_fiber, landmarksOn, 
    #     curvatureOn, torsionOn)
    run_make_dataset(input_folder, output_folder, landmark_file,  num_points=num_points, num_landmarks=num_landmarks, model_fiber=model_fiber, landmarksOn=landmarksOn, 
        curvatureOn=curvatureOn, torsionOn=torsionOn)



if __name__ == '__main__':
    main()
