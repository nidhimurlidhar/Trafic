import argparse
import subprocess
from os import sys, path
from fiberfileIO import *
import shutil
if not hasattr(sys, 'argv'):
    sys.argv  = ['']


real_py_file = os.path.dirname(os.path.realpath(__file__))
default_paths = []

default_paths.append(real_py_file)
default_paths.append(os.path.normpath(os.path.join(real_py_file, "../../")))

#From the source dir to the build dir
default_paths.append(os.path.normpath(os.path.join(real_py_file, "../../Trafic-build/Trafic-build/bin")))
default_paths.append(os.path.normpath(os.path.join(real_py_file, "../../niral_utilities-install/bin")))
default_paths.append(os.path.normpath(os.path.join(real_py_file, "../../Trafic-build/niral_utilities-install/bin")))

#For the install dir
default_paths.append(os.path.normpath(os.path.join(real_py_file, "../../../../niral_utilities-install/bin")))

#For docker
default_paths.append("/cli-modules")


parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', action='store', dest='input_dir', help='Input directory ',
                    default="")
parser.add_argument('--output_dir', action='store', dest='output_dir', help='Output Directory ',
                    default="")
parser.add_argument('--landmarks', action='store', dest='landmarks', help='Landmarks File (.vt[k/p], or .fcsv)',
                    default="")
parser.add_argument('--number_points', action='store', dest='number_points', help='Number of points for the sampling',
                    default=50)
parser.add_argument('--number_landmarks', action='store', dest='number_landmarks', help='Number of landmarks',
                    default=5)

parser.add_argument('--no_landmarks', action='store_true', dest='no_landmarks', help='Don\'t compute landmarks features')
parser.add_argument('--no_curvature', action='store_true', dest='no_curvature', help='Don\'t compute curvature features')
parser.add_argument('--no_torsion', action='store_true', dest='no_torsion', help='Don\'t compute torsion features')
parser.add_argument('--hints', type=str, nargs='+', help='Path hints to find the executables: fiberfeaturescreator, ', default=default_paths)


def get_executable(name, hints=["."]):
    for h in hints:
        for root, dirs, files in os.walk(h):
            current_file = os.path.join(root, name)
            if name in files and os.path.isfile(current_file):
                return current_file
    return name #Hopefully is in the system path


FIBERSAMPLING = get_executable("fibersampling", default_paths)
FIBERFEATURESCREATOR = get_executable("fiberfeaturescreator", default_paths)


def run_make_dataset(input_dir, output_dir, landmarks="", number_landmarks=5, number_points=50, landmarksOn=True, curvatureOn=True, torsionOn=True):

    sys.stdout.flush()
    class_list = os.listdir(check_folder(input_dir, True))

    for _, class_fib in enumerate(class_list):
        class_path = os.path.join(input_dir, class_fib)
        fiber_list = os.listdir(check_folder(class_path, True))
        for _, fiber in enumerate(fiber_list):
            input_fiber = os.path.join(class_path, fiber)
            output_fiber = os.path.join(check_folder(output_dir,True), class_fib)
            output_fiber = os.path.join(output_fiber, fiber)
            while os.path.isfile(output_fiber): # if a fiber already exists with the same name, we simply append a _1 to the new fiber
                name, ext = os.path.splitext(output_fiber)
                output_fiber = name + "_1" + exists
            make_fiber_feature(input_fiber, output_fiber, landmarks, number_points=number_points, number_landmarks=number_landmarks, landmarksOn=landmarksOn,torsionOn=torsionOn,curvatureOn=curvatureOn)
    shutil.copyfile(landmarks, os.path.join(output_dir, 'landmarks.fcsv'))

def make_fiber_feature(input_fiber, output_fiber, landmarks, number_points=50, number_landmarks=5, landmarksOn=True, torsionOn=True, curvatureOn=True):

    cmd_sampling = [FIBERSAMPLING,"--input", check_file(input_fiber), "--output",
             check_path(output_fiber, True), "-N", str(number_points)]

    print (" ".join(cmd_sampling))
    out, err = subprocess.Popen(cmd_sampling, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print("\nout : " + str(out))
    if err != "":
        print("\nerr : " + str(err))

    cmd_ffc = [FIBERFEATURESCREATOR, "--input", check_file(output_fiber), "--output",
                 check_path(output_fiber), "-N", str(number_landmarks), "--landmarksfile", landmarks]
    if landmarksOn:
        cmd_ffc.append("--landmarks")
    if torsionOn:
        cmd_ffc.append("--torsion")
    if curvatureOn:
        cmd_ffc.append("--curvature")
    print (" ".join(cmd_ffc))
    out, err = subprocess.Popen(cmd_ffc, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print("\nout : " + str(out))
    
    if err != "":
        print("\nerr : " + str(err))
    return

def main():

    args = parser.parse_args()
    # root = args.root
    number_landmarks = int(args.number_landmarks)
    number_points = int(args.number_points)
    landmarks = args.landmarks
    output_dir = args.output_dir
    input_dir = args.input_dir
    landmarksOn = not args.no_landmarks 
    curvatureOn = not args.no_curvature
    torsionOn = not args.no_torsion

    FIBERSAMPLING = get_executable("fibersampling", default_paths)
    FIBERFEATURESCREATOR = get_executable("fiberfeaturescreator", default_paths)

    run_make_dataset(input_dir, output_dir, landmarks,  number_points=number_points, number_landmarks=number_landmarks, landmarksOn=landmarksOn, 
        curvatureOn=curvatureOn, torsionOn=torsionOn)



if __name__ == '__main__':
    main()
