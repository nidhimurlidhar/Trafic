#ifndef FIBERPROCESSING_H
#define FIBERPROCESSING_H

#include <string>
#include <cmath>
#include <memory>
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <math.h>
#include <numeric>
#include <algorithm>

#include <vtkCellArray.h>
#include <vtkPolyLine.h>
#include <vtkVersion.h>
#include <itkSpatialObjectReader.h>
#include <itkSpatialObjectWriter.h>

#include "dtitypes.h"

#ifndef vtkFloatingPointType
#define vtkFloatingPointType double
#endif

struct parametrized_distance_struct
{
  double dist ;
  double x ;
  double y ;
  double z ;
};

class fiberprocessing{

 public:
  fiberprocessing();
  ~fiberprocessing();
  //Main functions
  void fiberprocessing_main(std::string& input_file  ,
                                            bool planeautoOn ,
                                            std::string auto_plane_origin,
                                            int num_landmarks
                                            );

  std::vector<parametrized_distance_struct> get_landmarks();
 private:
  void ComputeArcLength( DTIPointListType::iterator &beginit ,
                                        DTIPointListType::iterator &endit ,
                                        itk::Point<double , 3 > p2 ,
                                        int increment ,
                                        int displacement ,
                                        double min_distance
                                        );
  void arc_length_parametrization(GroupType::Pointer group);
  void landmarks_processing(GroupType::Pointer group, int num_landmarks);
  //IO functions
  GroupType::Pointer readFiberFile(std::string filename);
  //Helper functions
  void find_plane(GroupType::Pointer group, std::string auto_plane_origin);
  double find_min_dist();
  double find_max_dist();
  void sort_parameter();
  itk::Vector<double, 3> get_plane_origin();
  itk::Vector<double, 3> get_plane_normal();
  double SQ2(double x) {return x*x;};
  static bool sortFunction(parametrized_distance_struct i , parametrized_distance_struct j );
  double DistanceToPlane(itk::Point<double , 3> point) ;
  int CheckFiberOrientation( DTIPointListType &pointlist , int &count_opposite ) ;
  void ParametrizesEntireFiber(DTIPointListType &pointlist , int flag_orientation ) ;
  int ParametrizesHalfFiber(DTIPointListType &pointlist , DTIPointListType::iterator &endit, int increment, int displacement ) ;
  void AddValueParametrization( DTIPointListType::iterator &pit , itk::Point<double,3> p1 , double distance ) ;
  double Find_First_Point(DTIPointListType &pointlist , int displacement , DTIPointListType::iterator &pit_first ) ;
  itk::Point< double , 3> SpatialPosition(itk::Point<double, 3> position ) ;
  //Variables
  itk::Vector<double, 3> plane_origin, plane_normal;
  itk::Point<double, 3> closest_point;
  //all --> contain all the dti info in the order of FA, MD FRO, l2, l3, AD(l1), RD, GA
  std::vector< std::vector<double> >  all;
  std::vector< std::vector<parametrized_distance_struct> > parametrized_position;
  std::vector<parametrized_distance_struct> m_landmarks;
  double closest_d;
  itk::Vector<double,3> m_Spacing ;
  itk::Vector<double,3> m_Offset ;
  double m_Bandwidth ;
  bool m_WorldSpace ;
  const char* m_scalarName;

};


#endif
