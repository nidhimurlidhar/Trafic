#include <string>
#include <cmath>
#include <memory>
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <math.h>

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
#include <vtkFloatArray.h>

#include "dtitypes.h"
#include "argio.h"
#include "fiberprocessing.h"
#include "createLandmarksCLP.h"

#include <fstream> 

std::vector<std::string> parse_csv(std::string filename){
    std::ifstream filestream(filename.c_str());
    std::vector<std::string> results;
    std::string cell;
    while(std::getline(filestream, cell, ',')){
        cell.erase(std::remove(cell.begin(), cell.end(), '\n'), cell.end()); //remove newlines
        results.push_back(cell);
    }
    return results;
}

bool output_landmarks(std::string filename, std::vector< parametrized_distance_struct > landmarks){
    std::ofstream stream(filename.c_str());

    if(!stream.good())
        return false;

    stream << "# Markups fiducial file version = 4.5\n# CoordinateSystem = 0\n# Columns = id,x,y,z,ow,ox,oy,oz,vis,sel,lock,label,desc,associatedNodeID\n";
    for(int i = 0; i < landmarks.size(); i++){
        stream << "Landmark_" << i << "," << landmarks[i].x << "," << landmarks[i].y << "," << landmarks[i].z << ",0,0,0,1,1,1,0,LM-" << i+1 << std::endl;
    }

    stream.close();
    return true;
}

int main(int argc, char* argv[])
{
    PARSE_ARGS;

    std::vector <std::string> file_list = parse_csv(input_fiber_list);
    if(file_list.size() == 0)
    {
        std::cout << "Error: No input file names could be extracted from the CSV" << std::endl;
        return -1;
    }

    std::vector< std::vector <parametrized_distance_struct> > split_landmarks;
    std::vector<parametrized_distance_struct> merged_landmarks;

    for(int i = 0; i < file_list.size(); i++)
    {
        std::string input_fiber_file = file_list[i];

        if(input_fiber_file!="")
        {
            fstream filecheck;
            filecheck.open(input_fiber_file.c_str(),fstream::in);
            if (!filecheck.good())
            {
                std::cout<<"Unable to open the input fiber file...exit without results!\n"<<std::endl;
                return -1;
            }
            filecheck.close();
        }

        if(num_landmarks <= 0){
            std::cout << "Error: number of landmarks must be at least 1" << std::endl;
            return -1;
        }
        bool plane_auto_on=true;

        //generate landmarks
        fiberprocessing FP;
        std::cout << "Processing " << input_fiber_file << "..." << std::endl;
        FP.fiberprocessing_main(input_fiber_file, plane_auto_on, "cog", num_landmarks);
        std::vector<parametrized_distance_struct> FP_landmarks = FP.get_landmarks();
        if(FP_landmarks.size() == num_landmarks)
            split_landmarks.push_back(FP_landmarks);
    }

    //merge all landmarks
    for (int i = 0; i < split_landmarks.size(); i++){
        for(int j = 0; j < num_landmarks; j++){
            merged_landmarks.push_back(split_landmarks[i][j]);
        }
    }

    //write merged landmarks
    if(!output_landmarks(output_landmarks_full, merged_landmarks))
    {
        std::cout << "Error: failed to write full landmarks to file" << std::endl;
        return -1;
    }
    return 0 ;
}


