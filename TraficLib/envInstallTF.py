import os, sys, subprocess

def envIsInstalled():
    currentPath = os.path.dirname(os.path.abspath(__file__))
    if os.path.isdir(os.path.join(currentPath,"..","..", "miniconda2")):
        return True
    return False

def envInstall():
    currentPath = os.path.dirname(os.path.abspath(__file__))
    dir_install = os.path.join(currentPath,"..","..")
    py_version = str(sys.version_info.major)+"."+str(sys.version_info.minor)
    os_type = sys.platform 
    if os_type == "linux2": #Linux
        import struct
        nbit = struct.calcsize("P") * 8
        path_env_install = os.path.join(currentPath,"..","TraficLib","envInstallTFLinux.sh")
        cmd_env_install = path_env_install + " " + str(dir_install) + " " + str(py_version) + " " + str(nbit)
    elif os_type == "darwin":
        path_env_install = os.path.join(currentPath,"..","TraficLib","envInstallTFMacOS.sh") #MacOS
        cmd_env_install = path_env_install + " " + str(dir_install) + " " + str(py_version)
    cmd = ["bash", "-c", str(cmd_env_install)]
    subprocess.Popen(cmd)

def runMaybeEnvInstallTF():
    if not envIsInstalled():
        envInstall()

if __name__ == '__main__':
    runMaybeEnvInstallTF()