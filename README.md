# TRAFIC - TRACTS FIBERS CLASSIFICATION USING DEEP LEARNING

## What is it ?
Trafic is a program that performs classification of tract fibers using deep learning algorithms. This extension uses ITK and VTK Libraries to extract features from the fibers, and Tensorflow, for all the deep learning part, meaning the training and the testing.

## Requirements

### Packages
* ITK (v4.7 and above)
* VTK (v6.1.0 and above)
* SlicerExecutionModel

### Software
* polydatatransform (part of niral_utilities)

### Notes
* Have +4GiB free of ram to run the program

## LICENSE
see LICENSE

## CLI Instructions
Trafic is a python application.
It should be run from within a Docker container in which Tensorflow has been installed, ideally with python3 and GPU access.
A Dockerfile is provided in Docker/Dockerfile to build the rest of the image


### Multiclassification from CLI
Classification is mainly done through the TraficMulti.py script. However, there are a few different options:
By default, the script will do sampling, compute the fiber features and add them to a new temporary vtk file that will be used later for the classification.
This works fine, but this preprocessing step takes some time, and has to be repeated every time you want to classify the same file.
To speed things up, you have the option to run the preprocessing of your fiber file only once, then specify this preprocessed fiber as input, which will cause the preprocessing to be skipped.
For both of these options, you can use a csv file to run the classification on multiple cases in one call:

#### Non preprocessed fiber file
##### Input parameters:
```
--input (Input fiber file to be classified)
--displacement (Displacement field from input space to the training dataset's space)
--landmarks (Path to the landmarks file)
--checkpoint_dir (Directory containg the trained model - Tensorflow checkpoint files -)
```
##### Output parameters:
```
--output_dir (Output directory)
--summary (Log directory, optional)
```

##### CSV input
Alternatively, you can specify parameters as a csv file, in which case the script should be called with the --input_csv flag.
In the csv input file, each row should consist of the input parameters needed to classify one tract. The parameters should be ordered this way:
```
input, output_dir, checkpoint_dir, summary, displacement_field, landmarks
```

#### Preprocessed fiber file
##### Run the preprocessing
In order to preprocess a fiber file, you should use the script fiber_preprocessing.py
This script takes the following parameters:

###### Input parameters:
```
--input (Input fiber file to be preprocessed)
--displacement (Displacement field from input space to the training dataset's space)
--landmarks (Path to the landmarks file)
```
Optional:
```
--number_points (Number of points to use for the sampling. Default: 50)
--number_landmarks (Number of landmarks to use. Default: 32)
--no_landmarks (Don't add the landmarks to the features)
--no_curvature (Don't add curvature to the features)
--no_torsion (Don't add torsion to the features)
```
###### Output parameters:
```
--output (Output preprocessed fiber file)
--summary (Log directory, optional)
```
###### CSV input
Alternatively, you can specify parameters as a csv file, in which case the script should be called with the --input_csv flag.
In the csv input file, each row should consist of the input parameters needed to classify one tract. The parameters should be ordered this way:
```
input, output, displacement, landmarks
```

##### Classification of a preprocessed fiber file
###### Input parameters:
```
--preprocessed_fiber (Input preprocessed fiber file to be classified)
--checkpoint_dir (Directory containg the trained model - Tensorflow checkpoint files -)
```
###### Output parameters:
```
--output_dir (Output directory)
--summary (Log directory, optional)
```

###### CSV input
Alternatively, you can specify parameters as a csv file, in which case the script should be called with the --input_csv flag.
In the csv input file, each row should consist of the input parameters needed to classify one tract. The parameters should be ordered this way:
```
preprocessed_fiber, output_dir, checkpoint_dir, summary
```
#### Exploiting the classification output
The classification script outputs a .json file containing class information for every tract. To use this information and get an .vtk file as output, you can use the extractClassifiedFibers.py script:
```
--class_data (JSON file comntaining the classification results)
--input (VTK file containing the origin fiber tract used for the classification)
--output_dir (Output directory)
```


### Training from CLI
#### Preprocessing
Before training the model, you need to create the dataset that Trafic will use

Your data should be organized like this:
```
...
atlas1/fiber_name1/fiber_name1.vtk
atlas1/fiber_name2/fiber_name2.vtk
atlas1/fiber_name3/fiber_name3.vtk
...
atlas2/fiber_name1/fiber_name1.vtk
atlas2/fiber_name2/fiber_name2.vtk
atlas2/fiber_name3/fiber_name3.vtk
...
```
You can train against multiple datasets, but you need to have a displacement field from one of these datasets to all the others. This dataset should be the one for which you have a landmarks file.

For each dataset: 
* Transform the landmarks file with the displacement field to this particular dataset's space using polydatatransform (from NiralUser/niral_utilities):
```
polydatatransform --invertx --inverty --fiber_file [path_to_landmarks_file.fcsv] -D [path_to_displacement_field.nrrd] -o [path_to_output_landmarks_file.fcsv]
```
* Check that the transformed landmarks are correct using a visualisation tool such as Slicer
* run makeDataset.py with the following parameters:
```
--input_dir : this dataset's directory
--output_dir : output directory, should be the same for all your datasets
--landmarks : landmarks file for this particular dataset
```
Optional:
```
--number_points (Number of points to use for the sampling. Default: 50)
--number_landmarks (Number of landmarks to use. Default: 32)
--no_landmarks (Don't add the landmarks to the features)
--no_curvature (Don't add curvature to the features)
--no_torsion (Don't add torsion to the features)
```
#### Creating the tensorflow dataset
* use the runStore.py script using the following parameters: 
```
--input_dir : the folder you used as output from makeDataset.py
```
Optional:
```
--number_points (Number of points to use for the sampling. Default: 50)
--number_landmarks (Number of landmarks to use. Default: 32)
--no_landmarks (Don't add the landmarks to the features)
--no_curvature (Don't add curvature to the features)
--no_torsion (Don't add torsion to the features)
```
Expected output: a train.tfrecords file should have been created in your data directory. If it's not present, check that tensorflow has been properly installed

#### Training using the newly created tfrecords
* use the runtraining.py script using the following parameters:
```
--input_dir as the directory containing your .tfrecords file
--checkpoint_dir as the checkpoint output directory, where your trained model will be stored
--summary as a log directory
```
Optional:
```
--learning_rate  (Initial learning rate)
--number_epochs (Number of epochs)
--batch_size (Batch size)
--number_hidden (Size of hidden layers. Not currently in use)
--number_layers (Number of layers. Not currently in use)
```
* Expected output: your output directory should contain a checkpoint file and different tensorflow files.
You can delete all the temporary folders that were used in the preprocessing stages
