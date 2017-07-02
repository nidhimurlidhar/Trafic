"""By using execfile(this_file, dict(__file__=this_file)) you will
activate this virtualenv environment.
This can be used when you must use an existing Python interpreter, not
the virtualenv bin/python
"""
import sys
print sys.maxunicode
# import subprocess
# out, err = subprocess.Popen(["/bin/bash -c"," ldd --version;"] , stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
# print err
# print out
import tensorflow
print("TENSORFLOW VERSION ::: " + str(tensorflow.__version__))