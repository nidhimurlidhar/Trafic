#ifndef __DistanceMapFilter_h
#define __DistanceMapFilter_h
 
#include "itkImageToImageFilter.h"
#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"
#include "itkObjectFactory.h"
#include "itkImageRegionIterator.h"
#include "itkImageRegionConstIterator.h"
#include "itkNeighborhoodIterator.h"
#include <itkOtsuThresholdImageFilter.h>
#include "../../utils/fiberfileIO.h"

#define NONWM_VALUE 0
#define WM_VALUE 1

#define NONWM_COST 20.0
#define WM_COST 1.0
#define START_COST 0.0

#define MAX_PATH 65535.0
 
namespace itk
{
template< class TImage>
class DistanceMapFilter:public ImageToImageFilter< TImage, TImage >
{
public:
  /** Standard class typedefs. */
  typedef DistanceMapFilter Self;
  typedef ImageToImageFilter< TImage, TImage > Superclass;
  typedef SmartPointer< Self > Pointer;
 
  /** Method for creation through the object factory. */
  itkNewMacro(Self);
 
  /** Run-time type information (and related methods). */
  itkTypeMacro(DistanceMapFilter, ImageToImageFilter);

  void Init(typename TImage::IndexType start);
  void SetInputData(typename TImage::Pointer input);
  void Update();
  void SetLandmarks(vtkSmartPointer<vtkPolyData> lmParam);
  typename TImage::Pointer GetOutput();


 
protected:
  DistanceMapFilter(){}
  ~DistanceMapFilter(){}
 
  /** Does the real work. */
  virtual void GenerateData();
  typename TImage::Pointer Binarisation(typename TImage::Pointer imgGray);
  void browse_update_path(bool left_right, bool top_bottom, bool front_back);

 
private:
  // DistanceMapFilter(const Self &); //purposely not implemented
  // void operator=(const Self &);  //purposely not implemented
  typename TImage::Pointer cost;
  typename TImage::Pointer path;
  typename TImage::Pointer input;
  typename TImage::Pointer W_Cost;

  // double (*)W_Cost[3][3]; //{  { {sqrt(3), sqrt(2), sqrt(3)},  {sqrt(2), 1, sqrt(2)}, {sqrt(3), sqrt(2), sqrt(3)} },
  //                             { {sqrt(2),   1,     sqrt(2)},  {   1,    0,    1   }, {sqrt(2),   1,     sqrt(2)} },
  //                             { {sqrt(3), sqrt(2), sqrt(3)},  {sqrt(2), 1, sqrt(2)}, {sqrt(3), sqrt(2), sqrt(3)}, } ;
 
};
} //namespace ITK
 
 
#ifndef ITK_MANUAL_INSTANTIATION
#include "distancemapfilter.hxx"
#endif
 
 
#endif // __DistanceMapFilter_h

