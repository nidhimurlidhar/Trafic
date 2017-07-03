# TRAFIC - TRACTS FIBERS CLASSIFICATION USING DEEP LEARNING

## What is it ?
Trafic is a program that performs classification of tract fibers using deep learning algorithms. This extension uses ITK and VTK Libraries to extract features from the fibers, and Tensorflow, for all the deep learning part, meaning the training and the testing.

## Requirements

### Packages
* ITK (v4.7 and above)
* VTK (v6.1.0 and above)
* SlicerExecutionModel
### Software
* Slicer with the SlicerDMRI Extension (Use of Tractography Display)
### Notes
* Have +4GiB free of ram to run the program
* Have an algorithm to compute atlas-registration (e.g: DTI-Reg) to obtain the displacement field
* Program is running in background and write every outputs in the corresponding log file
### Future Improvement
* 
## LICENSE
see License