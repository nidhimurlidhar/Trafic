import sys
import os
import vtk
BLUE = "\033[0;34m"
BLUE_BOLD = "\033[1;34m"
RED = "\033[0;31m"
RED_BOLD = "\033[1;31m"
GREEN = "\033[0;32m"
GREEN_BOLD = "\033[1;32m"
YELLOW = "\033[0;33m"
YELLOW_BOLD = "\033[1;33m"
CYAN = "\033[0;36m"
CYAN_BOLD =  "\033[1;36m"
NC = "\033[0m"
NC_BOLD = "\033[1m"


# Convert time, return h, m, s - Hours, minutes and seconds corresponding to the time
def convert_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return h, m, s


# Check if a file already exists, and create another file in the format "[filename]_i.[extension_file]
#           is increment is true.
def check_file_inc(filename, increment=False):
    i = 1
    name, ext = os.path.splitext(filename)
    if increment:
        while os.path.isfile(filename):
            filename = name+"_"+str(i)+ext
            i += 1
    return filename


# Check if a file exists
def check_file(filename):
    if not os.path.isfile(filename):
        raise Exception("Unknown file %s" %filename)
    return filename


# Check if a folder exists and create it if force=True
def check_folder(folder, force=False):
    if not os.path.isdir(folder):
        if force:
            print RED, "---Folder %s created" % folder, NC
            sys.stdout.flush()
            os.makedirs(folder)
        else:
            raise Exception("No such directory: %s " % folder)
    return folder


# Check if the path of the file name exists and create it if force=True
def check_path(filename, force=False):
    directory = os.path.dirname(filename)
    check_folder(directory, force)
    return filename


# Check if the file with the root throw in parameter exists
def check_file_root(filename, root):
    if not os.path.isfile(filename) and filename:
        filename = os.path.join(root, filename)
        if not os.path.isfile(filename):
            raise Exception("No such file as %s" %filename)
    return filename


# Check if the directory of the file with the root throw in parameter exists
def check_dir_root(filename, root):
    directory = os.path.dirname(filename)
    name = os.path.basename(filename)
    if not os.path.isdir(directory) and directory:
        directory = os.path.join(root, directory)
        if not os.path.isdir(directory):
            raise Exception("No such directory as %s" % directory)
    return os.path.join(directory, name)


# Display the loading of a process
def display_loading(index, complete, old_process):
    progress = (100*index)/(complete-1)
    if progress%5==0 and progress != old_process:
        print "..%d%%"%progress,
        sys.stdout.flush()
        old_process = progress
    return old_process


# Read a .vtk or a .vtp file and return a Polydata
def read_vtk_data(fiber_filename):
    print "---Reading file ", fiber_filename
    sys.stdout.flush()
    try:
        if not os.path.isfile(fiber_filename):
            raise Exception('%s is not a file' % fiber_filename)
        if fiber_filename.rfind(".vtk") != -1:
            reader = vtk.vtkPolyDataReader()
            reader.SetFileName(fiber_filename)
            reader.Update()
            return reader.GetOutput()
        elif fiber_filename.rfind(".vtp") != -1:
            reader = vtk.vtkXMLPolyDataReader()
            reader.SetFileName(fiber_filename)
            reader.Update()
            return reader.GetOutput()
        else:
            raise Exception('Unkmown File Format for %s' % fiber_filename)
    except IOError as e:
        print('Could not read:', fiber_filename, ':', e)
        exit(0)


# Write a .vtk or a .vtp file and taking a Polydata in parameter
def write_vtk_data(vtk_file, fiber_filename):
    print "---Writing file ", GREEN, fiber_filename, NC
    sys.stdout.flush()
    try:
        if fiber_filename.rfind(".vtk") != -1:
            writer = vtk.vtkPolyDataWriter()
            writer.SetFileName(fiber_filename)
            if vtk.VTK_MAJOR_VERSION >5:
                writer.SetInputData(vtk_file)
            else:
                writer.SetInput(vtk_file)
            del vtk_file
            writer.Update()
        elif fiber_filename.rfind(".vtp") != -1:
            writer = vtk.vtkXMLPolyDataWriter()
            writer.SetFileName(fiber_filename)
            if vtk.VTK_MAJOR_VERSION >5:
                writer.SetInputData(vtk_file)
            else:
                writer.SetInput(vtk_file)
            del vtk_file
            writer.Update()
        else:
            raise Exception('Unknown File Format for %s' % fiber_filename)
    except IOError as e:
        print('Could not write:', fiber_filename, ':', e)
        exit(0)


# Extract the fibers whose the indexes are in the parameter ids from the bundle, and return a vtkPolydata containing
# those fibers
def extract_fiber(bundle, ids):
    print "ids selected: ", ids.GetNumberOfTuples()
    sys.stdout.flush()
    selectionNode = vtk.vtkSelectionNode()
    selectionNode.SetFieldType(vtk.vtkSelectionNode.CELL)
    selectionNode.SetContentType(vtk.vtkSelectionNode.INDICES)
    selection = vtk.vtkSelection()
    extractSelection = vtk.vtkExtractSelection()
    vtu2vtkFilter = vtk.vtkDataSetSurfaceFilter()

    selectionNode.SetSelectionList(ids)
    selection.AddNode(selectionNode)
    if vtk.VTK_MAJOR_VERSION > 5:
        extractSelection.SetInputData(0, bundle)
        del bundle
        extractSelection.SetInputData(1, selection)
        del selection
        extractSelection.Update()
        vtu2vtkFilter.SetInputData(extractSelection.GetOutput())
        del extractSelection
    else :
        extractSelection.SetInput(0, bundle)
        del bundle
        extractSelection.SetInput(1, selection)
        del selection
        extractSelection.Update()
        vtu2vtkFilter.SetInput(extractSelection.GetOutput())
        del extractSelection
    vtu2vtkFilter.Update()
    extract = vtk.vtkPolyData()
    extract = vtu2vtkFilter.GetOutput()
    del vtu2vtkFilter
    del selectionNode
    return extract