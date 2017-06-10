#include <vtkPolyData.h>
#include <vtkSmartPointer.h>
#include <vtkIdList.h>
#include <vtkCell.h>
vtkSmartPointer<vtkPolyData> sampling_fibers(int nbSample, std::string inputfilename);