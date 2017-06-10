

#include "distancemapfilterCLP.h"
#include "../../utils/fiberfileIO.h"
#include "distancemapfilter.h"
#include "time.h"
#include <fstream>
#include <pthread.h>
#define NUM_POINTS 32

struct thread_data{
    int t_id;
    std::string atlas_filename;
    std::string outputDir;
    double lm[3];
};

void *process(void *t_arg)
{

    struct thread_data *my_data;
    my_data = (struct thread_data *) t_arg;
    int my_id = my_data->t_id;
    double* my_lm = my_data->lm;
    std::string my_atlas = my_data->atlas_filename;
    std::string my_outputDir = my_data->outputDir;

    typedef unsigned short PixelType;    
    typedef itk::Image< double, 3> ImageType;
    typedef itk::DistanceMapFilter<ImageType> FilterType;

    itk::ImageFileReader<ImageType>::Pointer reader = itk::ImageFileReader<ImageType>::New();
    ImageType::Pointer img;

    FilterType::Pointer mapFilter = FilterType::New();

    reader->SetFileName(my_atlas.c_str());
    reader->Update();
    img = reader->GetOutput();
    mapFilter->SetInputData(img);
    ImageType::IndexType index;
    // cout << "Index "<<my_lm[0]<<my_lm[1]<<my_lm[2]<<std::endl;
    // itk::Point <double, 3> ijk;
    // ijk[0] = - my_lm[0];
    // ijk[1] = - my_lm[1];
    // ijk[2] = my_lm[2];
    index[0] = abs(my_lm[0] + img->GetOrigin()[0]);
    index[1] = abs(my_lm[1] + img->GetOrigin()[1]);
    index[2] = abs(my_lm[2] - img->GetOrigin()[2]);
    // img->TransformPhysicalPointToIndex(ijk ,index);

    // cout << "Index "<<index<<std::endl;
    mapFilter->Init(index);
    mapFilter->Update();
    std::string id_char = static_cast<std::ostringstream*>( &( std::ostringstream() << my_id) )->str();

    itk::ImageFileWriter<ImageType>::Pointer writer = itk::ImageFileWriter<ImageType>::New();
    writer->SetFileName(my_outputDir+"/distanceMap"+id_char+".nrrd");
    writer->SetInput(mapFilter->GetOutput());
    writer->Update();

    pthread_exit(NULL);
}
int main (int argc, char *argv[])
{
	PARSE_ARGS;
    
    time_t start, end;
    time(&start);

    // typedef unsigned short PixelType;    
    // typedef itk::Image< float, 3> ImageType;
    // typedef itk::DistanceMapFilter<ImageType> FilterType;

    // itk::ImageFileReader<ImageType>::Pointer reader = itk::ImageFileReader<ImageType>::New();
    // ImageType::Pointer img;

    // FilterType::Pointer mapFilter = FilterType::New();

    // reader->SetFileName(atlasFile.c_str());
    // reader->Update();
    // img = reader->GetOutput();

    pthread_t threads[NUM_POINTS];
    int rc;
    pthread_attr_t attr;
    void *status;
    std::ofstream csvfile;
    std::string csv_filename = outputDir + "/distanceMap.csv";
    csvfile.open(csv_filename.c_str());
    // Initialize and set thread joinable
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);


    // itk::NrrdImageIO::Pointer io = itk::NrrdImageIO::New();
    // io->SetNrrdVectorType( nrrdKindList );
    // io->SetFileType( itk::ImageIOBase::ASCII );
    // io->SetInputData( "itk::ImageIOBase::ASCII" );

    // mapFilter->SetInputData(img);


    vtkSmartPointer<vtkPolyData> landmarks = readFCSVFile(landmarkFile.c_str());
    vtkPoints* lm_pts = landmarks->GetPoints();

    struct thread_data td[NUM_POINTS];

    // for (int i = 0; i<1; i++)
    // {
    //     index[0] = abs(lm_pts->GetPoint(i)[0] + img->GetOrigin()[0]);
    //     index[1] = abs(lm_pts->GetPoint(i)[1] + img->GetOrigin()[1]);
    //     index[2] = abs(lm_pts->GetPoint(i)[2] - img->GetOrigin()[2]);

    //     std::cout<<"...Computing distance Map "<<i+1<<"/"<<NbPts<<std::endl;

    //     std::string i_char = static_cast<std::ostringstream*>( &( std::ostringstream() << i) )->str();

    //     mapFilter->Init(index);
    //     mapFilter->Update();

    //     itk::ImageFileWriter<ImageType>::Pointer writer = itk::ImageFileWriter<ImageType>::New();
    //     writer->SetFileName(outputDir+"/distanceMap"+i_char+".nrrd");
    //     writer->SetInput(mapFilter->GetOutput());
    //     writer->Update();

    // }
    for (int i=0; i<NUM_POINTS; ++i)
    {

        td[i].atlas_filename = atlasFile;
        td[i].outputDir = outputDir;
        td[i].t_id = i;
        td[i].lm[0] = lm_pts->GetPoint(i)[0];
        td[i].lm[1] = lm_pts->GetPoint(i)[1];
        td[i].lm[2] = lm_pts->GetPoint(i)[2];
        // cout << "Index "<<td[i].lm[0]<<td[i].lm[1]<<td[i].lm[2]<<std::endl;
        cout << "Creating thread to compute distance Map "<<i<< endl;
        rc = pthread_create(&threads[i], &attr, process, (void *)&td[i]);
        if (rc){
         cout << "Error:unable to create thread," << rc << endl;
         exit(-1);
        }
        std::string i_char = static_cast<std::ostringstream*>( &( std::ostringstream() << i) )->str();
        csvfile << outputDir+"/distanceMap"+i_char+".nrrd,";
    }
    for (int i=0; i<NUM_POINTS; ++i)
    {

        rc = pthread_join(threads[i], &status);
        if (rc){
            cout << "Error:unable to join," << rc << endl;
            exit(-1);
        }

        cout << "Completed thread for distance Map "<<i<< endl;
    }
 //    else
 //    {
 //        Filter->Update();
 //    }

 //    writeVTKFile(outputFiber.c_str(),Filter->GetOutput());




    time(&end);
    int sec = difftime(end, start);
    int min = sec/60;
    int hours = min/60;
    std::cout<<"Process took "<<hours<<"h"<<min%60<<"m"<<sec%60<<"s"<<std::endl;
    csvfile.close();
    pthread_exit(NULL);

    return EXIT_SUCCESS;

}