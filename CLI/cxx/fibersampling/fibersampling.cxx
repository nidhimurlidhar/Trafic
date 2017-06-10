#include "fibersampling.h"
#include "../utils/fiberfileIO.hxx"
#include "fibersamplingCLP.h"
#define E(X) ((int)X)  //We define the integer part of a variable X

int main (int argc, char* argv[])
{
    PARSE_ARGS;

    if(argc < 3)
    {
        std::cerr << "Required: [Executable] -- input [inputfilename] --output [outputfilename] -N [Number of Samples - (30 by default)]" << std::endl;
        return EXIT_FAILURE;
    }
    if(nbSample<1)
    {
        throw itk::ExceptionObject("Number of Samples must be > 1");
    }

    //input = readVTKFile(inputFiber);
    vtkSmartPointer<vtkPolyData> output = vtkSmartPointer<vtkPolyData>::New();
    output = sampling_fibers(nbSample, inputFiber.c_str());
    writeVTKFile(outputFiber,output);

    return EXIT_SUCCESS;
}

vtkSmartPointer<vtkPolyData> sampling_fibers(int nbSample, std::string inputfilename)
{
    vtkSmartPointer<vtkPolyData> input = vtkSmartPointer<vtkPolyData>::New();
    input = readVTKFile(inputfilename);

    puts("---Processing Sampling of Fibers");

    vtkSmartPointer<vtkPolyData> output = vtkPolyData::New();

    output->Allocate();

    vtkSmartPointer<vtkPoints> outputPts = vtkSmartPointer<vtkPoints>::New();

    output->SetPoints(outputPts);

    vtkSmartPointer<vtkIdList> ids(vtkIdList::New());

    int NbFibers = input->GetNumberOfCells();
    float step;
    for (int i = 0; i<NbFibers; i++)
    {

        int nbPtOnFiber = input->GetCell(i)->GetNumberOfPoints();
        vtkIdType currentId = ids->GetNumberOfIds();
        if(nbSample > 1)
            step = (float) (nbPtOnFiber-1)/(nbSample-1);
        else
            step = 0;
        for (int k = 0; k<nbSample; k++)
        {
            vtkIdType id;
            vtkPoints* pts = input->GetCell(i)->GetPoints();
            double new_p[3], p0[3], p1[3];
            double t = k*step - E((k*step));

            if(E((k*step))<(nbPtOnFiber-1)) // If we are not at the end
            {
                p0[0] = pts->GetPoint(E((k*step)))[0]   ;   p1[0] = pts->GetPoint(E((k*step))+1)[0];
                p0[1] = pts->GetPoint(E((k*step)))[1]   ;   p1[1] = pts->GetPoint(E((k*step))+1)[1];
                p0[2] = pts->GetPoint(E((k*step)))[2]   ;   p1[2] = pts->GetPoint(E((k*step))+1)[2];
                new_p[0]    =   (1-t)*p0[0]  + t*p1[0];
                new_p[1]    =   (1-t)*p0[1]  + t*p1[1];
                new_p[2]    =   (1-t)*p0[2]  + t*p1[2];
            }
            else
            {
                new_p[0]    =   pts->GetPoint(E((k*step)))[0];
                new_p[1]    =   pts->GetPoint(E((k*step)))[1];
                new_p[2]    =   pts->GetPoint(E((k*step)))[2];
            }
            id = outputPts->InsertNextPoint(new_p[0], new_p[1], new_p[2]);
            ids->InsertNextId(id);
        }
        output->InsertNextCell(VTK_POLY_LINE, nbSample, ids->GetPointer(currentId));
    }
    puts("---Sampling finished");

    return output;

}
