import os, sys
import subprocess
import json
import ast


def wrap(cmd_setenv, program, args=0):
    bashCommand = cmd_setenv + " " + program
    for flag,value in args.items():
        bashCommand = bashCommand + " " + flag + " " + value

    command = ["bash", "-c", str(bashCommand)]

    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    print("\nout : " + str(out) + "\nerr : " + str(err))

def config_env():
    # 
    # ----- Virtualenv setup ----- #
    # 
    """ Virtualenv setup with Tensorflow
    1 - install virtualenv if it's not already
    2 - create a virtualenv into slicer temporary path
    3 - install tensorflow into the virtualenv
    """ 
    pathSlicerExec = str(os.path.dirname(sys.exec_prefix))
    print sys.prefix
    if sys.platform == 'win32':
        pathSlicerExec.replace("/","\\")
    currentPath = os.path.dirname(os.path.abspath(__file__))

    if sys.platform == 'win32': 
        dirSitePckgs = os.path.join(pathSlicerExec, "lib", "Python", "Lib", "site-packages")
        pathSlicerPython = os.path.join(pathSlicerExec, "bin", "SlicerPython")
    else: 
        dirSitePckgs = os.path.join(pathSlicerExec, "..", "lib", "Python", "lib",'python%s' % sys.version[:3], "site-packages")
        pathSlicerPython = os.path.join(pathSlicerExec, "..", "bin", "python-real ")
    import pip
    print "pip:", pip.__version__
    # Check virtualenv installation
    print("\n\n I. Virtualenv installation")
    try:
        import virtualenv
        print("===> Virtualenv already installed")
    except Exception as e: 
        venv_install = pip.main(['install', 'virtualenv'])
        import virtualenv
        print("===> Virtualenv now installed with pip.main")


    print("\n\n II. Create environment tensorflowSlicer")
    currentPath = os.path.dirname(os.path.abspath(__file__))
    tempPath = os.path.join(currentPath, '..')
    env_dir = os.path.join(tempPath, "env-tensorflow") 
    if not os.path.isdir(env_dir):
        os.mkdir(env_dir) 

    if not os.path.isfile(os.path.join(env_dir, 'bin', 'activate')):
        virtualenv_py = dirSitePckgs
        if sys.platform == 'linux2':
            env_v = virtualenv.__version__
            python_v = sys.version_info
            virtualenv_py = os.path.join(virtualenv_py, 'virtualenv-'+ env_v+ "-py"+str(python_v[0])+"."+str(python_v[1])+".egg", 'virtualenv.py')
        else:
            virtualenv_py = os.path.join(virtualenv_py, 'virtualenv.py')
        command = ["bash", "-c", pathSlicerPython + " " + virtualenv_py + " --python=" + pathSlicerPython + " " + env_dir]
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err =  p.communicate()
        print("out : " + str(out) + "\nerr : " + str(err))
        print("\n===> Environmnent tensorflowSlicer created")


    print("\n\n\n III. Install tensorflow into tensorflowSlicer")
    """ To install tensorflow in virtualenv, requires:
        - activate environment
        - export PYTHONPATH
        - launch python
            => cmd_setenv
        - add the environment path to sys.path
        - set sys.prefix 
        - pip install tensorflow
      """
    # source path-to-env/bin/activate
    if sys.platform == 'win32': 
        cmd_setenv = os.path.join(env_dir, 'Scripts', 'activate') + "; "
    else:
        cmd_setenv = "source " + os.path.join(env_dir, 'bin', 'activate') + "; "
    # construct python path
    if sys.platform == 'win32': 
        env_pythonpath = os.path.join(env_dir, 'bin') + ":" + os.path.join(env_dir, 'lib', 'Python') + ":" + os.path.join(env_dir, 'lib', 'Python', 'Lib', 'site-packages')
    else:
        env_pythonpath = os.path.join(env_dir, 'bin') + ":" + os.path.join(env_dir, 'lib', 'python%s' % sys.version[:3]) + ":" + os.path.join(env_dir, 'lib', 'python%s' % sys.version[:3], 'site-packages')
    # export python path
    cmd_setenv = cmd_setenv + "export PYTHONPATH=" + env_pythonpath +  "; "
    # export python path
    # cmd_setenv = cmd_setenv + "cd /tmp; "
    # # export python path
    # cmd_setenv = cmd_setenv + "wget http://launchpadlibrarian.net/137699828/libc6_2.17-0ubuntu5_amd64.deb; "
    # # export python path
    # cmd_setenv = cmd_setenv + "wget http://launchpadlibrarian.net/137699829/libc6-dev_2.17-0ubuntu5_amd64.deb; "
    # # export python path
    # cmd_setenv = cmd_setenv + "mkdir libc6_2.17;" + "cd libc6_2.17;"
    #  # export python path
    # cmd_setenv = cmd_setenv + "ar p ../libc6_2.17-0ubuntu5_amd64.deb data.tar.gz | tar zx; " + "ar p ../libc6-dev_2.17-0ubuntu5_amd64.deb data.tar.gz | tar zx;" + "cd -;"
    #  # export python path
    # cmd_setenv = cmd_setenv + "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/tmp/libc6_2.17/lib/x86_64-linux-gnu/:/tmp/libc6_2.17/lib/x86_64-linux-gnu/ld-2.17.so:/tmp/libc6_2.17/usr/lib64;"
    # # cmd_setenv = cmd_setenv + "export PYTHONPATH=" + env_pythonpath +  ":$PYTHONPATH; "
    # cmd_setenv = cmd_setenv + "LD_LIBRARY_PATH=/tmp/libc6_2.17/lib/x86_64-linux-gnu/:/tmp/libc6_2.17/usr/lib64/:/tmp/libc6_2.17/:$LD_LIBRARY_PATH; "

    # cmd_setenv = cmd_setenv + "/tmp/libc6_2.17/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 --library-path $LD_LIBRARY_PATH:/tmp/libc6_2.17/lib:/usr/lib64/:/tmp/libc6_2.17/usr/lib64/"
    # GLIBC_LIB = "/tmp/libc6_2.17/lib/x86_64-linux-gnu"
    # cmd_setenv = cmd_setenv + "/tmp/libc6_2.17/lib/x86_64-linux-gnu/ld-2.17.so "
    # cmd_setenv = cmd_setenv + "ldd /tools/Slicer4/Slicer-4.7.0-2017-05-19-linux-amd64/bin/python-real;"
    cmd_setenv = cmd_setenv + " LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/tmp/libc6_2.17/lib/:/tmp/libc6_2.17/lib/x86_64-linux-gnu /tmp/libc6_2.17/lib/x86_64-linux-gnu/ld-2.17.so "
    # # cmd_setenv = cmd_setenv + "/tmp/libc6_2.17/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 --library-path /tmp/libc6_2.17/lib:$LD_LIBRARY_PATH:/usr/lib64/:/work/jpri "

    # export python path


    # call Slicer python
    cmd_setenv = cmd_setenv + pathSlicerPython

    # construct sys.path
    if sys.platform == 'win32': 
        env_syspath = "sys.path.append(" + os.path.join(env_dir,'lib', 'Python') + "\"); sys.path.append(\"" + os.path.join(env_dir,'lib','Python', 'Lib', 'site-packages') + "\"); sys.path.append(\"" + os.path.join(env_dir,'lib','python%s' % sys.version[:3], 'site-packages','pip','utils') + "\"); "
    else:
        # env_syspath = "sys.path.append(\"" + os.path.join(env_dir,'lib', 'python%s' % sys.version[:3]) + "\"); sys.path.append(\"" + os.path.join(env_dir,'lib','python%s' % sys.version[:3], 'site-packages') + "\"); sys.path.append(\"" + os.path.join(env_dir,'lib','python%s' % sys.version[:3], 'site-packages','pip','utils') + "\"); "
        env_syspath = 'sys.path.append("' + os.path.join(env_dir,'lib', 'python%s' % sys.version[:3]) + '");sys.path.append("' + os.path.join(env_dir,'lib','python%s' % sys.version[:3], 'site-packages') + '");sys.path.append("' + os.path.join(env_dir,'lib','python%s' % sys.version[:3],'site-packages','pip','utils') + '");'

    cmd_virtenv = str(' -c ')
    cmd_virtenv = cmd_virtenv + "\'import sys; " + env_syspath 

    # construct sys.path
    env_sysprefix = "sys.prefix=\"" + env_dir + "\"; "
    cmd_virtenv = cmd_virtenv + env_sysprefix

    # construct install command
    env_install = "import pip; pip.main([\"install\", \"--prefix=" + env_dir + "\", \"https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-1.1.0-cp27-none-linux_x86_64.whl\"]); pip.main([\"install\", \"--prefix=" + env_dir + "\", \"pandas\"])\'"
    cmd_virtenv = cmd_virtenv + env_install

    # print "cmd_setenv:", cmd_setenv

    bashCommand = cmd_setenv + str(cmd_virtenv)
    command = ["bash", "-c", str(bashCommand)]
    # print command
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    print("\nout : " + out + "\nerr : " + err)
    print(command)
    # Tensorflow is now installed but might not work due to a missing file
    # We create it to avoid the error 'no module named google.protobuf'
    # -----
    print("\n\n Create missing __init__.py if doesn't exist yet")
    if sys.platform == 'win32': 
        google_init = os.path.join(env_dir, 'lib', 'Python', 'Lib', 'site-packages', 'google', '__init__.py')
    else:
        google_init = os.path.join(env_dir, 'lib', 'python%s' % sys.version[:3], 'site-packages', 'google', '__init__.py')
    if not os.path.isfile(google_init):
        file = open(google_init, "w")
        file.close()
    

    print("\n\n\n IV. Check tensorflow is well installed")
    test_tf = os.path.join(currentPath,"..","TraficMulti","Testing", "test_TF.py")
    bashCommand = cmd_setenv + " " + test_tf

    command = ["bash", "-c", bashCommand]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    print("\nout : " + str(out) + "\nerr : " + str(err))

    return cmd_setenv

def main():
    cmd_setenv = config_env()

    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-pgm', action='store', dest='program')
    parser.add_argument('-args', action='store', dest='args')

    args = parser.parse_args()
    wrap(cmd_setenv, args.program, ast.literal_eval(args.args))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)

