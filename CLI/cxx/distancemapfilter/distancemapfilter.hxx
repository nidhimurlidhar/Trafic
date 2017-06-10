
#ifndef __DistanceMapFilter_hxx
#define __DistanceMapFilter_hxx
 
#include "distancemapfilter.h"


namespace itk
{
 
template< class TImage>
void DistanceMapFilter< TImage>
::GenerateData()
{
  // typename TImage::ConstPointer input = this->GetInput();
  // typename TImage::Pointer output = this->GetOutput();
 
  // itk::Index<2> cornerPixel = input->GetLargestPossibleRegion().GetIndex();
  // typename TImage::PixelType newValue = 3;
 
  // this->AllocateOutputs();
 
  // ImageAlgorithm::Copy(input.GetPointer(), output.GetPointer(), output->GetRequestedRegion(),
  //                      output->GetRequestedRegion() );
 
  // output->SetPixel( cornerPixel, newValue );
}

template< class TImage>
void DistanceMapFilter< TImage>
::Init(typename TImage::IndexType start)
{
	this->cost = TImage::New();
	this->path = TImage::New();


	typename TImage::IndexType index;
	index.Fill(1);

	typename TImage::RegionType region = this->input->GetLargestPossibleRegion();

	this->cost->SetRegions(region);
	this->path->SetRegions(region);

	// this->cost->Setorigin(this->input->);
	this->path->SetOrigin(this->input->GetOrigin());
	this->path->SetSpacing(this->input->GetSpacing());
	this->path->SetDirection(this->input->GetDirection());
	this->cost->SetDirection(this->input->GetDirection());


	this->cost->Allocate();
	this->path->Allocate();

	typename TImage::SizeType size = region.GetSize();

	this->path->FillBuffer(size[0]*size[1]*size[2]);
	this->path->SetPixel(start, 0);

	itk::ImageRegionIterator<TImage> it_cost(this->cost, this->cost->GetLargestPossibleRegion());
	itk::ImageRegionIterator<TImage> it_inp(this->input, this->input->GetLargestPossibleRegion());

	it_inp.GoToBegin();
	it_cost.GoToBegin();
	while ( !it_inp.IsAtEnd())
	{
		if (it_inp.Get() == NONWM_VALUE)
		{
			it_cost.Set(NONWM_COST);
			// std::cout<<"Value 1 "<<it.Get()<<std::endl;
		}
		else if (it_inp.Get() == WM_VALUE)
		{
			it_cost.Set(WM_COST);
			// std::cout<<"Value 2"<<it_inp.Get()<<std::endl;
		}
		else
		{
			std::cout<<"Value 3"<<it_inp.Get()<<std::endl;
			throw itk::ExceptionObject("Input image not binary, must only have two values");
		}
		++it_inp; 
		++it_cost;
	}

	this->cost->SetPixel(start, START_COST);
}

template< class TImage>
void DistanceMapFilter< TImage>	
::Update()
{
	this->browse_update_path(1,1,1);
	this->browse_update_path(1,1,0);
	this->browse_update_path(1,0,1);
	this->browse_update_path(1,0,0);
	this->browse_update_path(0,1,1);
	this->browse_update_path(0,1,0);
	this->browse_update_path(0,0,1);
	this->browse_update_path(0,0,0);

}

template< class TImage>
void DistanceMapFilter< TImage>	
::browse_update_path(bool left_right, bool top_bottom, bool front_back)
{
	typename TImage::SizeType img_size = this->input->GetLargestPossibleRegion().GetSize();

	typedef itk::NeighborhoodIterator<TImage> NeighborhoodIteratorType;
	int startX, startY, startZ;
	int endX, 	endY, 	endZ;
	int stepX, 	stepY, 	stepZ;

	// puts("1");
	// On the X axis
	if(left_right)
	{
		startX = 0;
		endX = img_size[0];
		stepX = 1;
	}
	else
	{
		startX = img_size[0]-1;
		endX = -1;
		stepX = -1;
	}

	// On the Y axis
	if(top_bottom)
	{
		startY = 0;
		endY = img_size[1];
		stepY = 1;
	}
	else
	{
		startY = img_size[1]-1;
		endY = -1;
		stepY = -1;
	}

	// On the Z axis
	if(left_right)
	{
		startZ = 0;
		endZ = img_size[2];
		stepZ = 1;
	}
	else
	{
		startZ = img_size[2]-1;
		endZ = -1;
		stepZ = -1;
	}
	typename NeighborhoodIteratorType::RadiusType radius;
	radius.Fill(1);

	NeighborhoodIteratorType it_path(radius, this->path, this->path->GetLargestPossibleRegion());
	// NeighborhoodIteratorType it_cost(radius, this->cost, this->cost->GetLargestPossibleRegion());
	NeighborhoodIteratorType it_w_cost(radius, this->W_Cost, this->W_Cost->GetLargestPossibleRegion());
	typename TImage::IndexType index;
	index.Fill(1);

	it_w_cost.SetLocation(index);

	float min, neighbor_value;

	// Nested loops to browse all the image in different directions
	for (int i = startX; i-endX != 0; i+=stepX)
	{
		for (int j = startY; j-endY != 0; j+=stepY)
		{
			for (int k = startZ; k-endZ != 0; k+=stepZ)
			{

				// std::cout<<"x:"<<i<<" y:"<<j<<" z:"<<k<<std::endl;

				index[0] = i;
				index[1] = j;
				index[2] = k;
				it_path.SetLocation(index);
				// it_cost.SetLocation(index);

				// puts("1");
				min = it_path.GetCenterPixel();

				// puts("2");

				// if(this->cost->GetPixel(index)==WM_COST)
				// {
					// std::cout<<"Value "<<it_path.GetCenterPixel()<<std::endl;
					// std::cout<<"Value "<<this->path->GetPixel(index)<<std::endl;
					for (int u = 0; u < it_path.Size(); ++u)
					{
						// puts("3");
						neighbor_value = it_path.GetPixel(u) + this->cost->GetPixel(index)*it_w_cost.GetPixel(u);
						if( neighbor_value < min)
						{
							min = neighbor_value;
						}
					}

					it_path.SetCenterPixel(min);
					// std::cout<<"Value "<<it_path.GetCenterPixel()<<std::endl;
					// std::cout<<"Value "<<this->path->GetPixel(index)<<std::endl;

				// }


				/* code */
			}
		}
	}

}

template< class TImage>
void DistanceMapFilter< TImage>	
::SetLandmarks(vtkSmartPointer<vtkPolyData> lmParam)
{
	this->landmarks = lmParam;

}

template< class TImage>
void DistanceMapFilter< TImage>
::SetInputData(typename TImage::Pointer input)
{

	// this->input = this->Binarisation(input);
	this->input = input;
	this->W_Cost = TImage::New();

  	typename TImage::IndexType r_start;
	r_start.Fill(0);

	typename TImage::SizeType r_size;
	r_size.Fill(3);

	typename TImage::RegionType region(r_start, r_size);
	this->W_Cost->SetRegions(region);
	this->W_Cost->Allocate();
	this->W_Cost->FillBuffer(0);

	float d;
	typename TImage::IndexType i_pixel;
	for(int i=0; i < 3; ++i)
	{
		for (int j = 0; j < 3; ++j)
		{
			for (int k = 0; k < 3; ++k)
			{
				d = sqrt((i-1)*(i-1) + (j-1)*(j-1) + (k-1)*(k-1));
				i_pixel[0] = i;
				i_pixel[1] = j;
				i_pixel[2] = k;
				this->W_Cost->SetPixel( i_pixel , d);
			}
		}
	}
	// std::cout<<"Value"<<W_Cost<<std::endl; 

}

template< class TImage>
typename TImage::Pointer DistanceMapFilter< TImage>
::GetOutput()
{
	// typename TImage::Pointer output = this->GetInput();
	return this->path;
}

template< class TImage>
typename TImage::Pointer DistanceMapFilter< TImage>
::Binarisation(typename TImage::Pointer imgGray)
{
	typedef itk::OtsuThresholdImageFilter <TImage, TImage> FilterType;

	typename FilterType::Pointer otsuFilter =  FilterType::New();
	typename TImage::Pointer binImg = TImage::New();

	otsuFilter->SetInsideValue(NONWM_VALUE);
	otsuFilter->SetOutsideValue(WM_VALUE);
	otsuFilter->SetInput(imgGray);
	otsuFilter->Update();
	binImg = otsuFilter->GetOutput();

	return binImg;
	// return binImg;
}
}// end namespace
 
 
#endif