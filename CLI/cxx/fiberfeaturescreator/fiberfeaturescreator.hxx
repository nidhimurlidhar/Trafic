#include "fiberfeaturescreator.h"

#include "vtkObjectFactory.h"

#define NB_LINES 250
#define NB_WORDS 250

// #define BLUE "\033[0;34m"
// #define RED "\033[0;31m"
// #define GREEN_BOLD "\033[0;32m"
// #define YELLOW "\033[0;33m"
// #define NC "\033[0m"





vtkStandardNewMacro(FiberFeaturesCreator);

FiberFeaturesCreator::FiberFeaturesCreator(){
	this->inputFibers = vtkSmartPointer<vtkPolyData>::New();
	this->outputFibers = vtkSmartPointer<vtkPolyData>::New();
	this->modelFibers = vtkSmartPointer<vtkPolyData>::New();
    this->nbLandmarks = 0;
    this->landmarkOn = false;
    this->torsionsOn = false;
    this->curvaturesOn = false;
    this->fcsvPointsOn = false;
    this->vtPointsOn = false;
    this->dMapOn = false;
    this->landmarksFilename = "";
}

FiberFeaturesCreator::~FiberFeaturesCreator(){}

void FiberFeaturesCreator::SetInput(std::string input, std::string model, std::string landmarkfile, std::string output, std::string distanceMapFilename)
{
	this->inputFibers = readVTKFile(input);
	this->dMapFilename = distanceMapFilename.c_str();
	if (!model.empty())
	{
		this->modelFibers = readVTKFile(model);
		this->landmarksFilename = output.substr(0,output.rfind("."))+"_landmarks";
	}
	else if (landmarkfile.empty())
	{
		this->fcsvPointsOn = false;
		this->vtPointsOn = false;
	}
	else if (landmarkfile.rfind(".vtk")!=std::string::npos||landmarkfile.rfind(".vtp")!=std::string::npos)
	{
		this->vtPointsOn = true;
		this->landmarksFilename = landmarkfile;
	}
	else if (landmarkfile.rfind(".fcsv")!=std::string::npos)
	{
		this->fcsvPointsOn = true;
		this->landmarksFilename = landmarkfile;
	}
}
void FiberFeaturesCreator::SetInputData(vtkSmartPointer<vtkPolyData> input, std::string model, std::string landmarkfile, std::string output, std::string distanceMapFilename)
{
	this->inputFibers = input;
	this->dMapFilename = distanceMapFilename.c_str();
	
	if (!model.empty())
	{
		this->modelFibers = readVTKFile(model);
		this->landmarksFilename = output.substr(0,output.rfind("."))+"_landmarks";
	}
	else if (landmarkfile.empty())
	{
		this->fcsvPointsOn = false;
		this->vtPointsOn = false;
	}
	else if (landmarkfile.rfind(".vtk")!=std::string::npos||landmarkfile.rfind(".vtp")!=std::string::npos)
	{
		this->vtPointsOn = true;
		this->landmarksFilename = landmarkfile;
	}
	else if (landmarkfile.rfind(".fcsv")!=std::string::npos)
	{
		this->fcsvPointsOn = true;
		this->landmarksFilename = landmarkfile;
	}

}
void FiberFeaturesCreator::SetNbLandmarks(int nbLandmarks)
{
	this->nbLandmarks = nbLandmarks;
}

// void FiberFeaturesCreator::SetDistanceMap(itk::Image< float, 3>::Pointer dMap)
// {
// 	this->distanceMap = dMap;
// }

void FiberFeaturesCreator::init_output()
{
	this->outputFibers=this->inputFibers;
	//std::cout<<"LM0 Avant:"<<this->landmarks[0]->GetPoint(0)[0]<<std::endl;
    this->landmarks.clear();
    this->avgLandmarks = vtkSmartPointer<vtkPoints>::New();
}

void FiberFeaturesCreator::Update()
{
	this->init_output();
	vtkSmartPointer<vtkDataArray> test_array_torsion;
	vtkSmartPointer<vtkDataArray> test_array_curv;

	if (dMapOn)
	{
		std::cout<<std::endl<<"---CSV File found, Computing landmarks from Distance Map File "<<this->dMapFilename<<NC<<std::endl;
	}
	else if(fcsvPointsOn)
	{
		std::cout<<std::endl<<"---FCSV File found, Computing landmarks from the FCSV File "<<this->landmarksFilename<<NC<<std::endl;
		this->compute_landmarks_from_fcsv();
		//this->compute_landmarks_average();
	}
	else if(vtPointsOn)
	{
		std::cout<<std::endl<<"---VTK File found, Computing landmarks from the VTK File "<<this->landmarksFilename<<NC<<std::endl;
		this->compute_landmarks_from_vtk_vtp();
		//this->compute_landmarks_average();
	}

	else
	{

		std::cout<<std::endl<<"---No VTK or FCSV or CSV File for the landmarks, Computing landmarks from the model"<<NC<<std::endl;
		this->compute_landmarks_from_model();
		this->compute_landmarks_average();
	}

	if (dMapOn)
	{
		this->compute_landmark_feature_from_dMap();
	}
	if(this->landmarkOn)
	{
		std::cout<<std::endl;
		puts("Computing Distance To Landmarks Features of the Fibers");
		puts("******************************************************");
		this->compute_landmark_feature();
		if(!fcsvPointsOn && !vtPointsOn)
			this->write_landmarks_file();
	
	}
	if(this->torsionsOn || this->curvaturesOn)
	{
		test_array_torsion = this->inputFibers->GetPointData()->GetScalars("torsion");
		test_array_curv = this->inputFibers->GetPointData()->GetScalars("curvature");
		if(!test_array_torsion || !test_array_curv)
			this->compute_tangents_binormals_normals();
	}
	if(this->torsionsOn)
	{
		if(!test_array_torsion)
		{
			std::cout<<std::endl;
			puts("Computing Torsions Features of the Fibers");
			puts("*****************************************");
			this->compute_torsions_feature();
		}
		else
		{
			puts("Torsions features already present - Skipping");
			puts("*****************************************");
		}


	}
	if(this->curvaturesOn)
	{
		if(!test_array_curv)
		{
			std::cout<<std::endl;
			puts("Computing Curvatures Features of the Fibers");
			puts("*****************************************");
			this->compute_curvatures_feature();
		}
		else
		{
			puts("Curvatures features already present - Skipping");
			puts("*****************************************");
		}


	}

}

vtkSmartPointer<vtkPolyData> FiberFeaturesCreator::GetOutput()
{
	return this->outputFibers;
}

void FiberFeaturesCreator::compute_landmarks_from_model()//std::vector<std::vector<vtkPoints*> > compute_landmarks()
{
	//TEST SUR INPUTSFIBERS ETC...
	std::vector<vtkFloatArray*> arclengthMatrix;
	//std::vector<std::vector<double*> > landmarks;

	vtkSmartPointer<vtkDataArray> arclengthArray = this->modelFibers->GetPointData()->GetScalars("SamplingDistance2Origin");
	int NbPtCurrentFiber;
	int NbFibers = this->modelFibers->GetNumberOfCells();
	int k = 0;
	for(int i=0; i<NbFibers; i++)
	{
		vtkFloatArray* arclengthArrayCurrent = vtkFloatArray::New();
		NbPtCurrentFiber = this->modelFibers->GetCell(i)->GetPoints()->GetNumberOfPoints();
		for(int j=0; j<NbPtCurrentFiber; j++)
		{
			if(!arclengthArray) 
			{
				throw itk::ExceptionObject("Error during the extraction of the scalars 'SamplingDistance2Origin' in the model. Please check that the model has the model fiber is valid (Must have 'SamplingDistance2Origin' as a scalar parameter)");
			}

			arclengthArrayCurrent->InsertNextTuple1(arclengthArray->GetTuple1(k));
			arclengthArray->GetTuple1(k);
			k++;
		}
		arclengthMatrix.push_back(arclengthArrayCurrent);
	}
	for(int i=0; i<NbFibers; i++)
	{
		std::vector<int> landmarksIndexArray = find_landmarks_index(arclengthMatrix[i]->GetNumberOfTuples() , this->nbLandmarks);
		//std::cout<<"Size = "<<landmarksIndexArray.size()<<"   ";
		vtkSmartPointer<vtkPoints> landmarksPtToAdd = vtkSmartPointer<vtkPoints>::New();
		//landmarksPtToAdd->SetNumberOfPoints(this->nbLandmarks);
		vtkPoints* pts = this->modelFibers->GetCell(i)->GetPoints();
		double* pt;
		for (int j = 0; j < this->nbLandmarks; ++j)
		{
			double* pt = new double[3];
			vtkIdList* pid;
			pt[0] = (pts->GetPoint(landmarksIndexArray[j]))[0];
			pt[1] = (pts->GetPoint(landmarksIndexArray[j]))[1];
			pt[2] = (pts->GetPoint(landmarksIndexArray[j]))[2];
			//std::cout<<"Pt  x = "<<pt[0]<<" y = "<<pt[1]<<" z = "<<pt[2]<<std::endl;
			landmarksPtToAdd->InsertNextPoint(pt[0],pt[1],pt[2]);
		}

		this->landmarks.push_back(landmarksPtToAdd);
	}

}
void FiberFeaturesCreator::compute_landmarks_from_vtk_vtp()
{
	vtkSmartPointer<vtkPolyData> vtkLandmarks = readVTKFile(this->landmarksFilename);
	int NbPoints = vtkLandmarks->GetNumberOfPoints();
	this->SetNbLandmarks(NbPoints);
	vtkSmartPointer<vtkPoints> point = vtkSmartPointer<vtkPoints>::New();
	for(int i=0; i<NbPoints; ++i)
	{
		this->avgLandmarks->InsertNextPoint(vtkLandmarks->GetPoint(i)[0],vtkLandmarks->GetPoint(i)[1],vtkLandmarks->GetPoint(i)[2]);
	}
	//this->landmarks.push_back(point);

}
void FiberFeaturesCreator::compute_landmarks_from_fcsv()
{
	std::fstream fcsvfile(this->landmarksFilename.c_str());
	std::string line;
	std::string mot;
	std::string words[NB_LINES][NB_WORDS]; // !!!! WARNING DEFINE AND TO PROTECT IF SUPERIOR TO 20
	int i,j;
	vtkSmartPointer<vtkPoints> landmarksPtToAdd = vtkSmartPointer<vtkPoints>::New();
	
	if(fcsvfile)
	{
		getline(fcsvfile, line);
		fcsvfile>>mot;
		while(mot=="#")
		{
			if(getline(fcsvfile, line))
				fcsvfile>>mot;
			else
				mot="#";
		}

		i=0;
		do
		{
			
			std::size_t pos_end;// = mot.find(",,");
			std::size_t pos1;
			j=0;
			do
			{
				std::size_t pos0 = 0;
				pos1 = mot.find(',');
				pos_end = mot.find(",,");
				words[i][j] = mot.substr(pos0, pos1-pos0);
				mot = mot.substr(pos1+1);
				j++;
			}
			while(pos1+1<pos_end);
			i++;
		}
		while(fcsvfile>>mot);
		int NbPoints = i;
		int NbFibers = this->inputFibers->GetNumberOfCells();
		this->SetNbLandmarks(NbPoints);
		for (int i = 0; i < NbPoints; ++i)
		{
			double x = atof(words[i][1].c_str());
			double y = atof(words[i][2].c_str());
			double z = atof(words[i][3].c_str());
			this->avgLandmarks->InsertNextPoint(x,y,z);
		}
		// for (int i = 0; i < NbFibers; ++i)
		// {
		// 	this->landmarks.push_back(landmarksPtToAdd);
		// }
	}
	else
	{
		std::cout<<"Error Impossible to open file!";
	}
}

void FiberFeaturesCreator::compute_landmark_feature_from_dMap()
{
	int NbFibers=this->inputFibers->GetNumberOfCells();
    typedef itk::Image< double, 3> ImageType;
    itk::ImageFileReader<ImageType>::Pointer reader = itk::ImageFileReader<ImageType>::New();
    typedef itk::Point< double, ImageType::ImageDimension> PointType;
    typedef itk::LinearInterpolateImageFunction < ImageType, double> InterpolatorType;
    ImageType::Pointer dM;
	std::fstream csv_file;
	std::string img_filename;
	int start =0;
	double tuple;
	double * ras;
	std::string landmarkLabel, start_char;

	vtkSmartPointer<vtkDataArray> test_array;

	InterpolatorType::Pointer interpolator = InterpolatorType::New();

	// itk::Image< float, 3>::IndexType index;
	itk::ContinuousIndex<double, 3> index;
	vtkPoints* pts = this->inputFibers->GetPoints();
	csv_file.open(this->dMapFilename.c_str());
	std::getline(csv_file, img_filename, ',');
	while(!img_filename.empty() && img_filename!="\n")
	{
		vtkSmartPointer<vtkFloatArray> dist2landmark = vtkFloatArray::New() ;
		std::cout<<img_filename<<std::endl;
		reader->SetFileName(img_filename.c_str());
    	reader->Update();
    	dM = reader->GetOutput();
		do
		{
			start ++;
			std::stringstream ss;
			ss << start;
			start_char = ss.str();
			landmarkLabel = "Distance2Landmark"+start_char;
			test_array = this->inputFibers->GetPointData()->GetScalars(landmarkLabel.c_str());
		}
		while(test_array);

		dist2landmark->SetName(landmarkLabel.c_str());
		int NbPts = this->inputFibers->GetNumberOfPoints();
		for (int i=0; i<NbPts; ++i)
		{
			ras = new double[3];
			ras[0] = pts->GetPoint(i)[0];
			ras[1] = pts->GetPoint(i)[1];
			ras[2] = pts->GetPoint(i)[2];

			PointType ijk;
			ijk[0] = -ras[0];
			ijk[1] = -ras[1];
			ijk[2] = ras[2];

			dM->TransformPhysicalPointToContinuousIndex(ijk, index);
			interpolator->SetInputImage(dM);
			tuple = interpolator->EvaluateAtContinuousIndex(index);

	     //    index[0] = abs(p0[0] + dM->GetOrigin()[0]);
	    	// index[1] = abs(p0[1] + dM->GetOrigin()[1]);
	    	// index[2] = abs(p0[2] - dM->GetOrigin()[2]);

	    	// tuple = dM->GetPixel(index);
	    	dist2landmark->InsertNextTuple1(tuple);

		}
		this->outputFibers->GetPointData()->SetActiveScalars(landmarkLabel.c_str());
		this->outputFibers->GetPointData()->SetScalars(dist2landmark);
		std::getline(csv_file, img_filename, ',');
	}


	// if(NbFibers < 0)
	// {
	// 	throw itk::ExceptionObject("Empty input fiber");
	// }

	// int NbPtOnFiber, start=0;
	// std::string landmarkLabel, start_char;

	// vtkSmartPointer<vtkDataArray> test_array;
	// do
	// {
	// 	start ++;
	// 	start_char = static_cast<std::ostringstream*>( &( std::ostringstream() << start) )->str();
	// 	landmarkLabel = "Distance2dMap_Landmark"+start_char;
	// 	test_array = this->inputFibers->GetPointData()->GetScalars(landmarkLabel.c_str());
	// }
	// while(test_array);


	// // std::string k_char = static_cast<std::ostringstream*>( &( std::ostringstream() << start) )->str();
	// // landmarkLabel.push_back("Distance2Landmark"+ start_char);
	

	// double * p1;
	// double * p0;
	// double * p2;

	// vtkSmartPointer<vtkFloatArray> dist2landmark = vtkFloatArray::New() ;
	
	// //std::cout<<"---Computing Scalar "<<landmarkLabel[k]<<std::endl;
	// dist2landmark->SetName(landmarkLabel.c_str());

	// int NbPts = this->inputFibers->GetNumberOfPoints();
	// vtkPoints* pts = this->inputFibers->GetPoints();

 //    itk::Image< float, 3>::IndexType index;
	
	// float tuple;

	// for (int i=0; i<NbPts; ++i)
	// {
	// 	p0 = new double[3];
	// 	p0[0] = pts->GetPoint(i)[0];
	// 	p0[1] = pts->GetPoint(i)[1];
	// 	p0[2] = pts->GetPoint(i)[2];

 //        index[0] = abs(p0[0] + this->distanceMap->GetOrigin()[0]);
 //    	index[1] = abs(p0[1] + this->distanceMap->GetOrigin()[1]);
 //    	index[2] = abs(p0[2] - this->distanceMap->GetOrigin()[2]);

 //    	tuple = this->distanceMap->GetPixel(index);

	// }

	// // for(int i=0; i<NbFibers; i++)
	// // {
	// // 	double* p1 = new double[3];

	// // 		p1[0] = (this->avgLandmarks->GetPoint(k))[0];
	// // 		p1[1] = (this->avgLandmarks->GetPoint(k))[1];
	// // 		p1[2] = (this->avgLandmarks->GetPoint(k))[2];

	// // 	vtkPoints* pts = this->inputFibers->GetCell(i)->GetPoints();
	// // 	NbPtOnFiber = pts->GetNumberOfPoints();
	// // 	for(int j=0; j<NbPtOnFiber; j++)
	// // 	{
	// // 		double* p0 = new double[3];
	// // 		p0[0] = pts->GetPoint(j)[0];
	// // 		p0[1] = pts->GetPoint(j)[1];
	// // 		p0[2] = pts->GetPoint(j)[2];
	// // 		double tuple = sqrt((p0[0]-p1[0])*(p0[0]-p1[0])+(p0[1]-p1[1])*(p0[1]-p1[1])+(p0[2]-p1[2])*(p0[2]-p1[2]));
	// // 		dist2landmark->InsertNextTuple1(tuple);
	// // 	}

	// // }
	// this->outputFibers->GetPointData()->SetActiveScalars(landmarkLabel.c_str());
	// this->outputFibers->GetPointData()->SetScalars(dist2landmark);

}

// Method landmark;
void FiberFeaturesCreator::compute_landmark_feature()
{
	int NbFibers=this->inputFibers->GetNumberOfCells();
	if(NbFibers < 0)
	{
		throw itk::ExceptionObject("Empty input fiber");
	}

	int NbPtOnFiber, start=0;
	std::vector<std::string> landmarkLabel;

	// !!!! If at each runing we want append Landmarks and not rewrite it decomment those lines
	vtkSmartPointer<vtkDataArray> test_array;
	do
	{
		start ++;
		std::stringstream ss;
		ss << start;
		std::string start_char = ss.str();
		std::string lm_name = "Distance2Landmark"+start_char;
		test_array = this->inputFibers->GetPointData()->GetScalars(lm_name.c_str());
	}
	while(test_array);

	for(int k=start; k<this->nbLandmarks+start+1; k++)
	{
		std::stringstream ss;
		ss << k;
		std::string k_char = ss.str();
		landmarkLabel.push_back("Distance2Landmark"+k_char);
		
	}

	double * p1 = new double[3];
	double * p0 = new double[3];
	double tuple;
	vtkPoints* pts;
	for(int k=0; k<this->nbLandmarks; k++)
	{
		vtkSmartPointer<vtkFloatArray> dist2landmark = vtkFloatArray::New() ;
		
		//std::cout<<"---Computing Scalar "<<landmarkLabel[k]<<std::endl;
		dist2landmark->SetName(landmarkLabel[k].c_str());
		for(int i=0; i<NbFibers; i++)
		{
				p1[0] = (this->avgLandmarks->GetPoint(k))[0];
				p1[1] = (this->avgLandmarks->GetPoint(k))[1];
				p1[2] = (this->avgLandmarks->GetPoint(k))[2];

			pts = this->inputFibers->GetCell(i)->GetPoints();
			NbPtOnFiber = pts->GetNumberOfPoints();
			for(int j=0; j<NbPtOnFiber; j++)
			{
				p0[0] = pts->GetPoint(j)[0];
				p0[1] = pts->GetPoint(j)[1];
				p0[2] = pts->GetPoint(j)[2];
				tuple = sqrt((p0[0]-p1[0])*(p0[0]-p1[0])+(p0[1]-p1[1])*(p0[1]-p1[1])+(p0[2]-p1[2])*(p0[2]-p1[2]));
				dist2landmark->InsertNextTuple1(tuple);
			}

		}
		this->outputFibers->GetPointData()->SetActiveScalars(landmarkLabel[k].c_str());
		this->outputFibers->GetPointData()->SetScalars(dist2landmark);
	}
	
}

// Method Torsions;	
void FiberFeaturesCreator::compute_landmarks_average()
{
	double avg_x=0, avg_y=0, avg_z=0;
	for(int i=0; i<this->nbLandmarks; i++)
	{
		for(int j=0; j<this->landmarks.size(); j++)
		{
			avg_x += this->landmarks[j]->GetPoint(i)[0];
			avg_y += this->landmarks[j]->GetPoint(i)[1];
			avg_z += this->landmarks[j]->GetPoint(i)[2];
			// if(i==4) 
			// {
			// 	std::cout<<"avgZ ="<<this->landmarks[1]->GetPoint(i)[2]<<"   ";
			// }
		}
		avg_x /= this->landmarks.size();
		avg_y /= this->landmarks.size();
		avg_z /= this->landmarks.size();

		this->avgLandmarks->InsertNextPoint(avg_x,avg_y,avg_z);
		avg_x=0; avg_y=0; avg_z=0;
	}
}


void FiberFeaturesCreator::compute_tangents_binormals_normals()
{
	vnl_vector_fixed<double,3> x0;
	vnl_vector_fixed<double,3> x1;
	vnl_vector_fixed<double,3> x2;
	double ds0;
	double ds1;
	vnl_vector_fixed<double,3> T0;
	vnl_vector_fixed<double,3> T1;
	vnl_vector_fixed<double,3> B;
	vnl_vector_fixed<double,3> N;
	int NbCells = this->inputFibers->GetNumberOfCells();

	for (int i =0; i<NbCells; i++)
	{
		int NbPoints = this->inputFibers->GetCell(i)->GetNumberOfPoints();
		for(int j = 0; j <NbPoints; j++) 
		{
			if(j<NbPoints-1)
			{
				x0.copy_in(this->inputFibers->GetCell(i)->GetPoints()->GetPoint(j));
				x1.copy_in(this->inputFibers->GetCell(i)->GetPoints()->GetPoint(j+1));
				ds0 = (x1-x0).two_norm();
				T0 = (x1-x0)/ds0;

				if(this->torsionsOn)
				{
					x2.copy_in(this->inputFibers->GetCell(i)->GetPoints()->GetPoint(j+2));
					ds1 = (x2-x1).two_norm();
					T1 = (x2-x1)/ds1;
					B = vnl_cross_3d(T0, T1);
					N = vnl_cross_3d(B, T0);
				}

			}
			this->tangents.push_back(T0);
			this->ds.push_back(ds0);
			if(this->torsionsOn)
			{
				this->binormals.push_back(B);
				this->normals.push_back(N);
			}
		}
	}

	// double * x0;
	// double * x1;
	// double ds;
	// double * T;
	// int NbCells = this->inputFibers->GetNumberOfCells();

	// for (int i =0; i<NbCells; i++)
	// {
	// 	int NbPoints = this->inputFibers->GetCell(i)->GetNumberOfPoints();
	// 	for(int j = 0; j <NbPoints; j++) 
	// 	{
	// 		if(j < NbPoints-1)
	// 		{
	// 			x0 = this->inputFibers->GetCell(i)->GetPoints()->GetPoint(j);
	// 			x1 = this->inputFibers->GetCell(i)->GetPoints()->GetPoint(j+1);
	// 			ds = sqrt((x0[0]-x1[0])*(x0[0]-x1[0]) + (x0[1]-x1[1])*(x0[1]-x1[1]) + (x0[2]-x1[2])*(x0[2]-x1[2]));
	// 			T = (*x1-*x0)/ds;
	// 		}
	// 		this->tangents.push_back(T);
	// 	}
	// }


}


// Method Torsions
/* 
> If the points of the polyline are x[k]
> ds[k] = length(x[k+1]-x[k])
> T[k] = (x[k+1]-x[k]) / ds[k]
> B[k] = cross(T[k],T[k+1]) // Vector product
> N[k] = cross(B[k],T[k])
> // T,B,N defines the discrete Frenet Frame of the curve
> tau[k]   = -dot((B[k+1] - B[k]),N[k]) / ds[k] //torsion
*/
void FiberFeaturesCreator::compute_torsions_feature()
{
	std::string featureLabel = "torsion";
	vtkSmartPointer<vtkFloatArray> torsion = vtkFloatArray::New();
	//std::cout<<"---Computing Scalar "<<featureLabel<<std::endl;

	torsion->SetName(featureLabel.c_str());
	int k=0;
	float tau;
	int NbCells = this->inputFibers->GetNumberOfCells();
	for (int i =0; i<NbCells; i++)
	{
		int NbPoints = this->inputFibers->GetCell(i)->GetNumberOfPoints();
		for(int j = 0; j <NbPoints; j++) 
		{
			if(j<NbPoints-1)
			{
				tau = -dot_product(this->binormals[k+1]-this->binormals[k], this->normals[k])/(this->ds[k]);
			}
			torsion->InsertNextTuple1(tau);
			// std::cout<<tau<<std::endl;
			k++;
		}
	}
	this->outputFibers->GetPointData()->SetActiveScalars(featureLabel.c_str());
	this->outputFibers->GetPointData()->SetScalars(torsion);
}
// Method Curvature;
/* 
> If the points of the polyline are x[k]
> ds[k] = length(x[k+1]-x[k])
> T[k] = (x[k+1]-x[k]) / ds[k]
> // T,B,N defines the discrete Frenet Frame of the curve
> kappa[k] = length(T[k+1] - T[k]) / ds[k] // curavture
*/	
void FiberFeaturesCreator::compute_curvatures_feature()
{
	std::string featureLabel = "curvature";
	vtkSmartPointer<vtkFloatArray> curvature = vtkFloatArray::New();
	//std::cout<<"---Computing Scalar "<<featureLabel<<std::endl;
	curvature->SetName(featureLabel.c_str());
	int k=0;
	float kappa;
	int NbCells = this->inputFibers->GetNumberOfCells();
	for (int i =0; i<NbCells; i++)
	{
		int NbPoints = this->inputFibers->GetCell(i)->GetNumberOfPoints();
		for(int j = 0; j <NbPoints; j++) 
		{
			if(j<NbPoints-1)
			{
				kappa = (this->tangents[k+1]-this->tangents[k]).two_norm()/(this->ds[k]);
			}
			curvature->InsertNextTuple1(kappa);
			k++;
		}
	}
	this->outputFibers->GetPointData()->SetActiveScalars(featureLabel.c_str());
	this->outputFibers->GetPointData()->SetScalars(curvature);
	
}

void FiberFeaturesCreator::SetLandmarksOn()
{
	this->landmarkOn = true;
}

void FiberFeaturesCreator::SetCurvatureOn()
{
	this->curvaturesOn = true;
}

void FiberFeaturesCreator::SetTorsionOn()
{
	this->torsionsOn = true;
}
void FiberFeaturesCreator::SetdMapOn()
{
	this->dMapOn = true;
}

void FiberFeaturesCreator::write_landmarks_file()
{
	std::string fcsv = this->landmarksFilename + ".fcsv";
	std::ofstream fcsvfile;
	fcsvfile.open(fcsv.c_str());
	std::cout<<"---Writing FCSV Landmarks File to "<<GREEN<<fcsv.c_str()<<NC<<std::endl;
	fcsvfile << "# Markups fiducial file version = 4.5\n";
	fcsvfile << "# CoordinateSystem = 0\n";
	fcsvfile << "# columns = id,x,y,z,ow,ox,oy,oz,vis,sel,lock,label,desc,associatedNodeID\n";
	for(int i=0; i<this->nbLandmarks; i++)
	{
		fcsvfile <<"Landmark_"<<i<<","<<this->avgLandmarks->GetPoint(i)[0]<<","<<this->avgLandmarks->GetPoint(i)[1]<<","<<this->avgLandmarks->GetPoint(i)[2];
		fcsvfile <<",0,0,0,1,1,1,0,F-"<<i+1<<",,\n";
	}
	fcsvfile.close();

	std::string vtkfile = this->landmarksFilename + ".vtk";
	vtkSmartPointer<vtkPolyData> landmarksPolydata = vtkSmartPointer<vtkPolyData>::New();
	vtkPoints* points = vtkPoints::New();
	for(int i=0; i<this->nbLandmarks; i++)
	{
		points->InsertPoint(i,this->avgLandmarks->GetPoint(i)[0],this->avgLandmarks->GetPoint(i)[1],this->avgLandmarks->GetPoint(i)[2]);
	}
	landmarksPolydata->SetPoints(points);
	writeVTKFile(vtkfile.c_str(), landmarksPolydata);
}



std::vector<int> find_landmarks_index(int nbSamples , int nbLandmarks)
{
	std::vector<int> index;

	for(int k=0; k < nbLandmarks; k++)
	{
		index.push_back(k*((nbSamples-1)/(nbLandmarks-1)));
	}
	return index;
}