
import numpy as np
import argparse
import os
import smote
import json
from storeDef import *

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', action='store', dest='input_dir', help='Training directory (usually the output directory from makeDataset.py)', default='')
parser.add_argument('--number_landmarks', type=int, action='store', dest='number_landmarks', help='Number of landmarks', default=32)
parser.add_argument('--number_points', type=int, action='store', dest='number_points', default=50, help='Number of points on each fiber')
parser.add_argument('--no_landmarks', action='store_true', dest='no_landmarks', help='Don\'t compute landmarks features')
parser.add_argument('--no_curvature', action='store_true', dest='no_curvature', help='Don\'t compute curvature features')
parser.add_argument('--no_torsion', action='store_true', dest='no_torsion', help='Don\'t compute torsions features')
parser.add_argument('--use_smote', action='store_false', dest='use_smote', help='Use synthetic oversampling')

def read_training(input_dir, num_landmarks, num_points, landmarks, curvature, torsion):
    dataset = []
    labels = []
    folders = [
        os.path.join(input_dir, d) for d in sorted(os.listdir(input_dir))
        if os.path.isdir(os.path.join(input_dir, d))]
    fiber_names = []
    for label, folder in enumerate(folders):
        fiber_names.append(os.path.basename(folder))
        fiber_files = [
            os.path.join(folder, d) for d in sorted(os.listdir(folder))]
        for fiber in fiber_files:
            fiber_file = os.path.join(folder, fiber)
            try:
                data_fiber, data_label = fiber_extract_feature(fiber_file, landmarks, curvature, torsion,
                                                      num_landmarks, num_points, label, train=True)
                if len(data_fiber) > 0:
                  dataset.extend(data_fiber.reshape((len(data_fiber),-1)))
                  labels.extend(data_label)
            except IOError as e:
                print('Could not read:', fiber_file, ':', e, '- it\'s ok, skipping.')

    permutation = np.random.permutation(len(dataset))
    return np.array(dataset)[permutation], np.array(labels)[permutation], fiber_names

def read_testing(fiber_file, num_landmarks, num_points, landmarks, curvature, torsion):
    try:
        data_fiber, data_name = fiber_extract_feature(fiber_file, landmarks, curvature, torsion,
            num_landmarks, num_points, os.path.splitext(fiber_file)[0], train=False)
        dataset = data_fiber.reshape((len(data_fiber),-1))
    
    except IOError as e:
        print('Could not read:', fiber_file, ':', e, '- it\'s ok, skipping.')
        
    return np.array(dataset), np.array(data_name)
    
def run_store(input_dir='', num_landmarks=32, num_points=50, lmOn=True, curvOn=True, torsOn=True, use_smote=False):
    nb_features = num_landmarks + int(curvOn) + int(torsOn)
    if input_dir:
        dataset, labels, names = read_training(input_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)

        ##output descritpion file
        with open(os.path.join(input_dir, 'dataset_description.json'), 'w') as json_description_file:
            dictionary = { 'directory' : input_dir, 'num_landmarks' : num_landmarks, 'num_points' : num_points, 'lmOn' : lmOn, 'curvOn' : curvOn, 'torsOn' : torsOn, 'smote' : use_smote }
            json_description_file.write(json.dumps({'store_parameters' : dictionary, 'labels' : names}, indent=4, separators=(',', ': ')))


        if use_smote:
            dataset, labels = smote.generate_with_SMOTE(dataset.reshape(len(dataset),-1),labels)
            permutation = np.random.permutation(len(dataset))
            dataset = dataset[permutation]
            labels = labels[permutation]

            print('Smote success !')
        dataset = dataset.reshape(len(dataset), nb_features, num_points)

        len_validation = int(len(dataset) * 0.01)
        len_testing = int(len(dataset) * 0.01)
        len_training = len(dataset) - (len_validation + len_testing)

        validation_set = data_set(len_training, nb_features, num_points)
        validation_set.data = dataset[0:len_validation]
        validation_set.labels = labels[0:len_validation]

        testing_set = data_set(len_training, nb_features, num_points)
        testing_set.data = dataset[len_validation + 1 : len_validation + len_testing]
        testing_set.labels = labels[len_validation + 1 : len_validation + len_testing]

        training_set = data_set(len_training, nb_features, num_points)
        training_set.data = dataset[len_validation + len_testing + 1 : - 1]
        training_set.labels = labels[len_validation + len_testing + 1 : - 1]

        print ('Final datasets shape: ', 'validation: ', np.shape(validation_set.data), 'testing: ', np.shape(testing_set.data), 'training: ', np.shape(training_set.data))
        #   Convert to Examples and write the result to TFRecords.

        convert_to(validation_set, 'validation', input_dir)
        convert_to(testing_set, 'testing', input_dir)
        convert_to(training_set, 'train', input_dir)

def main():
    args = parser.parse_args()    
    run_store(input_dir=args.input_dir, num_landmarks=args.number_landmarks, num_points=args.number_points, lmOn=not args.no_landmarks, curvOn=not args.no_curvature, torsOn=not args.no_torsion, use_smote=not args.use_smote)
  # Get the data.



if __name__ == '__main__':
    main()
