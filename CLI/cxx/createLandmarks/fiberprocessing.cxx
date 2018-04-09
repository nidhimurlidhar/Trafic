#include <string>
#include <cmath>
#include <memory>
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <math.h>
#include <algorithm>

#include <itkSpatialObjectReader.h>
#include <itkSpatialObjectWriter.h>

#include <vtkPolyData.h>
#include <vtkPointData.h>
#include <vtkPolyDataReader.h>
#include <vtkXMLPolyDataReader.h>
#include <vtkPolyDataWriter.h>
#include <vtkXMLPolyDataWriter.h>
#include <vtkSmartPointer.h>
#include <vtkCell.h>
#include <vtkDoubleArray.h>
#include <vtkFloatArray.h>
#include <vtkCellData.h>

#include "fiberprocessing.h"

fiberprocessing::fiberprocessing()
{
    plane_origin.Fill(0);plane_normal.Fill(0);
    m_Bandwidth = 0.0 ;
    closest_d = 0 ;
    m_WorldSpace = true ;
    m_scalarName = "NoScalar";
    m_Bandwidth = 2.0;
}

fiberprocessing::~fiberprocessing()
{}

void fiberprocessing::fiberprocessing_main( std::string& input_file  ,
                                            bool planeautoOn ,
                                            std::string auto_plane_origin,
                                            int num_landmarks
                                          )
{
    try{
        GroupType::Pointer group = readFiberFile(input_file) ;
        m_Spacing = group->GetSpacing();
        m_Offset = group->GetObjectToParentTransform()->GetOffset();

        if (planeautoOn)
        {
            cout<<"Finding the plane origin and normal automatically\n\n";
            find_plane(group , auto_plane_origin);
        }

        arc_length_parametrization( group ) ;
        landmarks_processing(group, num_landmarks);
    }catch(itk::ExceptionObject e){
        std::cout << "An error occured. Skipping " << input_file << std::endl;
    }

}

std::vector<parametrized_distance_struct> fiberprocessing::get_landmarks(){
    return m_landmarks;
}

bool compare_parametrized_distance_structs (parametrized_distance_struct i,parametrized_distance_struct j) { return (i.dist<j.dist); }
void fiberprocessing::landmarks_processing(GroupType::Pointer group, int num_landmarks){

    ChildrenListType* children = group->GetChildren(0);
    ChildrenListType::iterator it;

    std::vector<parametrized_distance_struct> sample_positions [num_landmarks]; //all the selected points

    for(int i = 0; i < parametrized_position.size(); i++) //iterate over all fibers
    {
        
        std::vector<parametrized_distance_struct> fiber_struct = parametrized_position[i]; //interm. var
        std::sort(fiber_struct.begin(), fiber_struct.end(), compare_parametrized_distance_structs);
        
        int min = 0, max = parametrized_position[i].size(); //interm. vars
        double step = (double) (max) / (double) (num_landmarks - 1);
        if(max == min) //in case the vector is empty
            continue;


        for(int j = 0; j < num_landmarks; j++){ //iterate over number of samples to take
            int sample_index = (int)  (j * step); //get index
            if(sample_index == max) sample_index -= 1;
            sample_positions[j].push_back(fiber_struct[sample_index]); //get sample at index
        }
    }

    //then average the samples over all fibers
    parametrized_distance_struct sums[num_landmarks];
    parametrized_distance_struct average_landmarks[num_landmarks];

    for(int i = 0; i < num_landmarks; i++){
        sums[i].x = 0; sums[i].y = 0; sums[i].z = 0; //init

        for(int j = 0; j < sample_positions[i].size(); j++){ //sum all positions
            sums[i].x += sample_positions[i][j].x;
            sums[i].y += sample_positions[i][j].y;
            sums[i].z += sample_positions[i][j].z;
        }
        //average
        average_landmarks[i].x = sums[i].x / sample_positions[i].size(); 
        average_landmarks[i].y = sums[i].y / sample_positions[i].size();
        average_landmarks[i].z = sums[i].z / sample_positions[i].size();
        m_landmarks.push_back(average_landmarks[i]);
    }
}

itk::Point< double , 3> fiberprocessing::SpatialPosition( itk::Point<double, 3> position )
{
    typedef DTIPointType::PointType PointType;
    if (m_WorldSpace)
    {
        position[0] = (position[0] * m_Spacing[0]) + m_Offset[0];
        position[1] = (position[1] * m_Spacing[1]) + m_Offset[1];
        position[2] = (position[2] * m_Spacing[2]) + m_Offset[2];
    }
    return position ;
}

double fiberprocessing::DistanceToPlane(itk::Point<double , 3> point)
{
    itk::Vector< double , 3 > vecToPlane ;
    for( int i = 0 ; i < 3 ; i++ )
    {
        vecToPlane[ i ] = point[ i ] - plane_origin[ i ] ;
    }
    vecToPlane.Normalize() ;
    double d = (plane_normal[0] * vecToPlane[0]) + (plane_normal[1] * vecToPlane[1]) + (plane_normal[2] * vecToPlane[2]) ;
    return d ;
}

double fiberprocessing::Find_First_Point( DTIPointListType &pointlist ,
  int increment ,
  DTIPointListType::iterator &pit_first
  )
{
    bool first_point = true ;
    double previous_distance = 0 ;
    for( DTIPointListType::iterator pit = pointlist.begin(); pit != pointlist.end(); pit++ )
    {
        //The norm of the normal vector to the plane has been normalized in arc_length_parametrization()
        itk::Point<double, 3> pos = SpatialPosition( (*pit).GetPosition() );
        double d = DistanceToPlane( pos ) ;
        if( first_point )
        {
            first_point = false ;
        }
        else
        {
            if( d * previous_distance < 0 )//if we have points on 2 sides of the plane, the distance will be of opposite sign
            {
                if( increment < 0 )//this current point is on the good side of the plan
                {
                    pit_first = pit - 1 ;
                    return previous_distance ;
                }
                else//the previous point was on the good side of the plan
                {
                    pit_first = pit ;
                    return d ;
                }
                break ;
            }
        }
        previous_distance = d ;
    }
    return std::numeric_limits<double>::quiet_NaN(); ;
}


void fiberprocessing::AddValueParametrization( DTIPointListType::iterator &pit , itk::Point<double,3> p1 , double distance)
{
    size_t fiber_counter = parametrized_position.size() - 1 ;
    parametrized_distance_struct param_dist ;
    param_dist.dist = distance ;
    param_dist.x = p1[0] ;
    param_dist.y = p1[1] ;
    param_dist.z = p1[2] ;
    parametrized_position[fiber_counter].push_back(param_dist);
}

void fiberprocessing::ComputeArcLength( DTIPointListType::iterator &beginit ,
    DTIPointListType::iterator &endit ,
    itk::Point<double , 3 > p2 ,
    int increment ,
    int displacement ,
    double min_distance
    )
{
    double cumulative_distance = min_distance ;
    for( DTIPointListType::iterator pit = beginit+increment ; pit != endit ; pit += increment )
    {
        //gives the distance between current and previous sample point
        double current_length ;
        itk::Point<double, 3> p1 = SpatialPosition( (*pit ).GetPosition() ) ;
        current_length = sqrt((p1[0]-p2[0])*(p1[0]-p2[0])+(p1[1]-p2[1])*(p1[1]-p2[1])+(p1[2]-p2[2])*(p1[2]-p2[2]));
        if( current_length > m_Bandwidth )
        {
            std::cout<<" Distance between 2 consecutive points > 2 x bandwidth" <<std::endl ;
            std::cout<<" Distance: "<< current_length <<std::endl ;
            std::cout<<" 2 x Bandwidth: "<< m_Bandwidth <<std::endl ;
        }
        cumulative_distance += displacement * current_length ;
        //multiplying by -1 to make arc length on 1 side of plane as negative
        AddValueParametrization( pit , p1 , cumulative_distance ) ;
        p2 = p1 ;
    }
}

int fiberprocessing::ParametrizesHalfFiber( DTIPointListType &pointlist ,
    DTIPointListType::iterator &endit ,
    int increment ,
    int displacement
    )
{
    DTIPointListType::iterator pit_first ;
    double distance_min ;
    distance_min = Find_First_Point( pointlist , increment , pit_first ) ;
#ifdef WIN32
    if( _isnan( distance_min ) )
    {
        return 1 ;
    }
#else
    if( std::isnan( distance_min ) )
    {
        return 1 ;
    }
#endif
    itk::Point<double, 3> p1 = SpatialPosition( (*pit_first).GetPosition() ) ;
    AddValueParametrization( pit_first , p1 , distance_min ) ;//distance_min is a signed distance. No need to multiply it by "displacement"
    ComputeArcLength( pit_first , endit , p1 , increment , displacement , distance_min ) ;
    return 0 ;
}


void fiberprocessing::ParametrizesEntireFiber( DTIPointListType &pointlist , int flag_orientation )
{
    //We start in one direction
    DTIPointListType::iterator pit_begin = pointlist.begin() - 1 ;
    ParametrizesHalfFiber( pointlist , pit_begin , -1 , -1*flag_orientation ) ;
    //Then we do parametrize the other one
    DTIPointListType::iterator pit_end = pointlist.end() ;
    ParametrizesHalfFiber( pointlist , pit_end , 1 , flag_orientation ) ;
}

int fiberprocessing::CheckFiberOrientation( DTIPointListType &pointlist , int &count_opposite )
{
    int flag_orientation ;
    DTIPointListType::iterator pit_tmp ;
    pit_tmp = pointlist.begin();
    itk::Point<double, 3> position_first = SpatialPosition( (*pit_tmp).GetPosition() ) ;
    pit_tmp = pointlist.end() -1 ;
    itk::Point<double, 3> position_last = SpatialPosition( (*pit_tmp).GetPosition() ) ;
    itk::Vector<double, 3> orient_vec = position_last - position_first ;
    //verifies that first and last point are on different sides of the plane

    double distance_first = DistanceToPlane( position_first ) ;
    double distance_last = DistanceToPlane( position_last ) ;
    if( distance_first * distance_last > 0)
    {
        return 0 ;
    }
    //
    double dot_prod = (plane_normal[0]*orient_vec[0] + plane_normal[1]*orient_vec[1] + plane_normal[2]*orient_vec[2] );
    if( dot_prod < 0 )
    {
        //found fiber orientation as opposite
        flag_orientation = -1 ;
        count_opposite += 1 ;
    }
    else
    {
        flag_orientation = 1 ;
    }
    return flag_orientation ;
}

void fiberprocessing::arc_length_parametrization( GroupType::Pointer group )
{
    ChildrenListType* children = group->GetChildren(0);
    ChildrenListType::iterator it;
    //**********************************************************************************************************
    // For each fiber
    int count_opposite = 0;
    float plane_norm = ( sqrt( ( plane_normal[ 0 ] * plane_normal[ 0 ] )
        + ( plane_normal[ 1 ] * plane_normal[ 1 ] )
        + ( plane_normal[ 2 ] * plane_normal[ 2 ] )
        )
    ) ;
    //Normalizing normal
    plane_normal[0] /= plane_norm;
    plane_normal[1] /= plane_norm;
    plane_normal[2] /= plane_norm;
    int ignored_fibers = 0;
    for(it = (children->begin()); it != children->end() ; it++)
    {
        if( parametrized_position.empty()
            || (!parametrized_position.empty() && !parametrized_position[parametrized_position.size() - 1 ].empty() )
            )
        {
            parametrized_position.push_back(std::vector<parametrized_distance_struct>());
        }
        DTIPointListType pointlist = dynamic_cast<DTITubeType*>((*it).GetPointer())->GetPoints();
        int flag_orientation = CheckFiberOrientation( pointlist , count_opposite ) ;
        if( flag_orientation || 1 )
        {
            ParametrizesEntireFiber( pointlist , flag_orientation ) ;
        }
        else
        {
            ignored_fibers++ ;
        }
    }
    std::cout<<" l_counter: " << all.size() << std::endl;
    cout << "Total # of opposite oriented fibers:" << count_opposite << endl ;
    cout << "Total # of ignored fibers (first and last point on the same side of the plane:" << ignored_fibers << endl ;
}

itk::Vector<double, 3> fiberprocessing::get_plane_origin()
{
    return(plane_origin);
}
itk::Vector<double, 3> fiberprocessing::get_plane_normal()
{
    return(plane_normal);
}




void fiberprocessing::find_plane(GroupType::Pointer group, std::string auto_plane_origin)
{
    ChildrenListType* pchildren = group->GetChildren(0);
    ChildrenListType::iterator it, it_closest;
    DTIPointListType pointlist;
    DTIPointListType::iterator pit, pit_closest;
    double sum_x=0,sum_y=0,sum_z=0;
    int num_points=0;

    if(auto_plane_origin=="cog")
    {
        //Finding Plane origin as the average x,y,z coordinate of the whole fiber bundle
        for(it = (pchildren->begin()); it != pchildren->end() ; it++)
        {
            pointlist = dynamic_cast<DTITubeType*>((*it).GetPointer())->GetPoints();
            for(pit = pointlist.begin(); pit != pointlist.end(); pit++)
            {
                itk::Point<double, 3> position = (*pit).GetPosition();
                num_points++;
                sum_x=sum_x+position[0]; sum_y=sum_y+position[1]; sum_z=sum_z+position[2];
            }
        }
        plane_origin[0]=sum_x/num_points;
        plane_origin[1]=sum_y/num_points;
        plane_origin[2]=sum_z/num_points;
    }
    else if(auto_plane_origin=="median")
    {
        itk::Vector<double, 3> median_point;
        //Finding Plane origin as the average x,y,z of middle points for each fibers
        int median=0;
        double distance_min=10000.0;
        for(it=pchildren->begin(); it!=pchildren->end(); it++)
        {
            pointlist=dynamic_cast<DTITubeType*>((*it).GetPointer())->GetPoints();
            median=ceil((double)pointlist.size()/2.0);
            pit=pointlist.begin();
            pit+=median;
            itk::Point<double,3> position=(*pit).GetPosition();
            num_points++;
            sum_x+=position[0]; sum_y+=position[1]; sum_z+=position[2];
        }
        median_point[0]=sum_x/num_points;
        median_point[1]=sum_y/num_points;
        median_point[2]=sum_z/num_points;
        for(it=pchildren->begin(); it!=pchildren->end(); it++)
        {
            pointlist=dynamic_cast<DTITubeType*>((*it).GetPointer())->GetPoints();
            median=ceil((double)pointlist.size()/2.0);
            pit=pointlist.begin();
            pit+=median;
            itk::Point<double,3> position=(*pit).GetPosition();
            double distance=sqrt(pow(position[0]-median_point[0],2)+pow(position[1]-median_point[1],2)+pow(position[2]-median_point[2],2));
            if(distance<distance_min)
            {
                distance_min=distance;
                plane_origin[0]=position[0];
                plane_origin[1]=position[1];
                plane_origin[2]=position[2];
            }
        }
    }
    cout<<"\nCalculated Plane Origin (avg x,y,z): "<<plane_origin[0]<<","<<plane_origin[1]<<","<<plane_origin[2]<<endl;

    //Leaving a percent of the bundle end points, find the closest point on bundle to the plane origin (to avoid curved bundles getting ends as the closest point)

    int closest_d = 1000.0;
    itk::Point<double, 3> closest_point_coor;
    closest_point_coor.Fill(0.0);
    for(it = (pchildren->begin()); it != pchildren->end() ; it++)
    {
        pointlist = dynamic_cast<DTITubeType*>((*it).GetPointer())->GetPoints();

        int percent_count = 1;
        for(pit = pointlist.begin(); pit != pointlist.end(); pit++)
        {
            //ignoring first 30% and last 30% of points along the fiber(Fiber-ends)
            if (percent_count>floor(pointlist.size() * .3) && percent_count<floor(pointlist.size() * .7))
            {
                itk::Point<double, 3> position = (*pit).GetPosition();
                double dist =  sqrt((position[0]-plane_origin[0])*(position[0]-plane_origin[0])+(position[1]-plane_origin[1])*(position[1]-plane_origin[1])+(position[2]-plane_origin[2])*(position[2]-plane_origin[2]));
                if (dist <= closest_d)
                {
                    closest_d = dist;
                    pit_closest = pit;
                    closest_point_coor[0] = (*pit).GetPosition()[0];
                    closest_point_coor[1] = (*pit).GetPosition()[1];
                    closest_point_coor[2] = (*pit).GetPosition()[2];
                    it_closest  = it;
                }
            }
            percent_count++;
        }
    }

    //Using 3 points to left and right of this closest point, find the plane normal
    itk::Point<double, 3> point_before, point_after;
    point_before.Fill(0);
    point_after.Fill(0);
    for(it = (pchildren->begin()); it != pchildren->end() ; it++)
    {
        if (it==it_closest)
        {
            pointlist = dynamic_cast<DTITubeType*>((*it).GetPointer())->GetPoints();
            for(pit = pointlist.begin(); pit != pointlist.end(); pit++)
            {
                if (pit==pit_closest)
                {
                    point_before = (*(--(--(--pit)))).GetPosition();
                    ++pit;++pit;++pit;
                    point_after = (*(++(++(++pit)))).GetPosition();
                }
            }
        }
    }
    plane_normal=point_after-point_before;
    double plane_norm = (sqrt((plane_normal[0]*plane_normal[0])+(plane_normal[1]*plane_normal[1])+(plane_normal[2]*plane_normal[2])));
    if (plane_norm != 1)
    {
        plane_normal[0] /= plane_norm;
        plane_normal[1] /= plane_norm;
        plane_normal[2] /= plane_norm;
    }
    cout<<"Plane normal:"<<plane_normal[0]<<","<<plane_normal[1]<<","<<plane_normal[2]<<endl;
}

GroupType::Pointer fiberprocessing::readFiberFile(std::string filename)
{

    int scalarCount = 0;
    int nonscalarCount = 0;

    // ITK Spatial Object
    if(filename.rfind(".fib") != std::string::npos)
    {
        typedef itk::SpatialObjectReader<3, unsigned char> SpatialObjectReaderType;

        // Reading spatial object
        SpatialObjectReaderType::Pointer soreader = SpatialObjectReaderType::New();

        soreader->SetFileName(filename);
        soreader->Update();

        return soreader->GetGroup();
    }
    // VTK Poly Data
    else if (filename.rfind(".vt") != std::string::npos)
    {
        // Build up the principal data structure for fiber tracts
        GroupType::Pointer fibergroup = GroupType::New();

        vtkSmartPointer<vtkPolyData> fibdata(NULL);

        // Legacy
        if (filename.rfind(".vtk") != std::string::npos)
        {
            vtkSmartPointer<vtkPolyDataReader> reader(vtkPolyDataReader::New());
            reader->SetFileName(filename.c_str());
            reader->Update();
            fibdata = reader->GetOutput();

        }
        else if (filename.rfind(".vtp") != std::string::npos)
        {
            vtkSmartPointer<vtkXMLPolyDataReader> reader(vtkXMLPolyDataReader::New());
            reader->SetFileName(filename.c_str());
            reader->Update();
            fibdata = reader->GetOutput();
        }
        else
        {
            throw itk::ExceptionObject("Unknown file format for fibers");
        }

        typedef  itk::SymmetricSecondRankTensor<double,3> ITKTensorType;
        typedef  ITKTensorType::EigenValuesArrayType LambdaArrayType;

        // Iterate over VTK data
        const int nfib = fibdata->GetNumberOfCells();
        int pindex = -1;
        for(int i = 0; i < nfib; ++i)
        {
            itk::DTITubeSpatialObject<3>::Pointer dtiTube = itk::DTITubeSpatialObject<3>::New();
            vtkSmartPointer<vtkCell> fib = fibdata->GetCell(i);

            vtkSmartPointer<vtkPoints> points = fib->GetPoints();

            typedef itk::DTITubeSpatialObjectPoint<3> DTIPointType;
            std::vector<DTIPointType> pointsToAdd;

            vtkSmartPointer<vtkDataArray> fibtensordata = fibdata->GetPointData()->GetTensors();
            vtkSmartPointer<vtkDataArray> fibscalardata = fibdata->GetPointData()->GetArray(m_scalarName);

            for(int j = 0; j < points->GetNumberOfPoints(); ++j)
            {
                ++pindex;       
                vtkFloatingPointType* coordinates = points->GetPoint(j);

                DTIPointType pt;
                // Convert from RAS to LPS for vtk
                pt.SetPosition(coordinates[0], coordinates[1], coordinates[2]);
                pt.SetRadius(0.5);
                pt.SetColor(0.0, 1.0, 0.0);

                if (fibscalardata != NULL)
                {
                  vtkFloatingPointType scalar = fibscalardata->GetTuple1(pindex);
                  pt.AddField(m_scalarName,scalar);
                  scalarCount++;
              }
              else
              {
                  pt.AddField(m_scalarName,0);
                  nonscalarCount++;
              }


              if (fibtensordata != NULL) 
              {

                vtkFloatingPointType* vtktensor = fibtensordata->GetTuple9(pindex);

                float floattensor[6];
                ITKTensorType itktensor;

                floattensor[0] = itktensor[0] = vtktensor[0];
                floattensor[1] = itktensor[1] = vtktensor[1];
                floattensor[2] = itktensor[2] = vtktensor[2];
                floattensor[3] = itktensor[3] = vtktensor[4];
                floattensor[4] = itktensor[4] = vtktensor[5];
                floattensor[5] = itktensor[5] = vtktensor[8];

                pt.SetTensorMatrix(floattensor);

                LambdaArrayType lambdas;

          // Need to do eigenanalysis of the tensor
                itktensor.ComputeEigenValues(lambdas);

                float md = (lambdas[0] + lambdas[1] + lambdas[2])/3;
                float fa = sqrt(1.5) * sqrt((lambdas[0] - md)*(lambdas[0] - md) +
                 (lambdas[1] - md)*(lambdas[1] - md) +
                 (lambdas[2] - md)*(lambdas[2] - md))
                / sqrt(lambdas[0]*lambdas[0] + lambdas[1]*lambdas[1] + lambdas[2]*lambdas[2]);

                float logavg = (log(lambdas[0])+log(lambdas[1])+log(lambdas[2]))/3;

                float ga =  sqrt( SQ2(log(lambdas[0])-logavg) \
                    + SQ2(log(lambdas[1])-logavg) \
                    + SQ2(log(lambdas[2])-logavg) );

                float fro = sqrt(lambdas[0]*lambdas[0] + lambdas[1]*lambdas[1] + lambdas[2]*lambdas[2]);
                float ad = lambdas[2];
                float rd = (lambdas[0] + lambdas[1])/2;

                pt.AddField("FA",fa);
                pt.AddField("MD",md);
                pt.AddField("FRO",fro);
                pt.AddField("l2",lambdas[1]);
                pt.AddField("l3",lambdas[0]);
                pt.AddField("l1",ad);
                pt.AddField("RD",rd);
                pt.AddField("GA",ga);
            }
            pointsToAdd.push_back(pt);
        }

        dtiTube->SetPoints(pointsToAdd);
        fibergroup->AddSpatialObject(dtiTube);
    }
    std::cout << "# of points with scalar values: " << scalarCount << "; # of points without scalar values: " << nonscalarCount << "\n" << std::endl;


    return fibergroup;
    } // end process .vtk .vtp
    else
    {
        throw itk::ExceptionObject("Unknown fiber file");
    }
}




double fiberprocessing::find_min_dist()
{
    double min=100000;
    for (size_t i=0; i<all.size(); i++)
    {
        if (all[i][0]<min)
        {
            min=all[i][0];
        }
    }
    std::cout<<"min is "<<min<<endl;
    return(min);
}

double fiberprocessing::find_max_dist()
{
    double max=-100000;
    for (size_t i=0; i<all.size(); i++)
    {
        if (all[i][0]>max)
        {
            max=all[i][0];
        }
    }
    std::cout<<"max is "<<max<<endl;
    return(max);
}

bool fiberprocessing::sortFunction(parametrized_distance_struct i , parametrized_distance_struct j )
{
    return ( i.dist < j.dist ) ;
}

void fiberprocessing::sort_parameter()
{
    for( size_t fiber_counter = 0 ; fiber_counter < parametrized_position.size() ; fiber_counter++ )
    {
        std::sort(parametrized_position[fiber_counter].begin(), parametrized_position[fiber_counter].end(), sortFunction ) ;
    }
}
