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
* Have an algorithm to compute atlas-registration (e.g: DTI-Reg) to obtain the displacement field

## LICENSE
see LICENSE

## CLI Instructions
Trafic is a CLI application

### Training from CLI
#### Preprocessing
Before training the model, you need to create the dataset that Trafic will use

Your data should be organized like this architecture:
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
--input_folder : this dataset's directory
--output_folder : output directory, should be the same for all your datasets
--landmark_file : landmarks file for this particular dataset
--num_landmarks : number of landmarks
```
#### Creating the tensorflow dataset
* use the runStore.py script using the following parameters: 
```
--train_dir : the folder you used as output from makeDataset.py
--num_landmarks : number of landmarks
```
Expected output: a tran.tfrecords file should have been created in your data directory. If it's not present, check that tensorflow has been properly installed

#### Training using the newly created tfrecords
* use the runtraining.py script using the following parameters:
```
--data_dir as the directory containing you .tfrecords file
--checkpoint_dir as the final output directory, where you trained model will be stored
--summary_dir as a log directory
```
* use the --multiclass flag if you want to train for multiclassification
* Expected output: your output directory should contain a checkpoint file and different tensorflow files.
You can delete all the temporary folders that were used in the preprocessing stages



### Biclassification from CLI
### Multiclassification from CLI
Run the TraficMulti_cli.py script with the following parameters:
#### Inputs parameters:
```
--input (Input fiber file to be classified)
--displacement (Displacement field from input space to the training dataset's space)
--checkpoints (Directory containg the trained model - Tensorflow checkpoint files -)
```
Alternatively, you can specify parameters as a csv file, in which case the script should be called with the --input_csv flag.
In the csv input file, each row should consist of the input parameters needed to classify one tract. The parameters should be ordered this way:
```
fiber_file,output_directory,model_directory,summary_directory,displacement_field
```
#### Output parameters:
```
--output (Output directory)
--summary (Log directory)
```
