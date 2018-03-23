
import numpy as np
import argparse
import os
import tensorflow as tf
import smote
import json
from storeDef import *

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string('train_dir', '',    ' training directory')
flags.DEFINE_string('test_dir', '',    ' testing directory')
flags.DEFINE_string('valid_dir', '',    ' validation directory')
flags.DEFINE_string('original_dir', '',    ' Oiginal input Test directory before pre processing')
flags.DEFINE_integer('num_landmarks',  5,      'Number of landmarks')
flags.DEFINE_integer('num_points',  50,      'Number of points on each fiber')
flags.DEFINE_boolean('landmarks', True, 'Compute landmarks features')
flags.DEFINE_boolean('curvature', True, 'Compute curvature features')
flags.DEFINE_boolean('torsion', True, 'Compute torsions features')
flags.DEFINE_boolean('use_smote', False, 'Use synthetic oversampling')

def read_training(train_dir, num_landmarks, num_points, landmarks, curvature, torsion):
    dataset = []
    labels = []
    folders = [
        os.path.join(train_dir, d) for d in sorted(os.listdir(train_dir))
        if os.path.isdir(os.path.join(train_dir, d))]
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

def read_testing(fiber_file, src_dir, num_landmarks, num_points, landmarks, curvature, torsion):
    try:
        data_fiber, data_name = fiber_extract_feature(fiber_file, landmarks, curvature, torsion,
            num_landmarks, num_points, os.path.splitext(fiber_file)[0], train=False)
        dataset = data_fiber.reshape((len(data_fiber),-1))
    
    except IOError as e:
        print('Could not read:', fiber_file, ':', e, '- it\'s ok, skipping.')
        
    return np.array(dataset), np.array(data_name)
    
def run_store(train_dir='', valid_dir='', test_dir='', original_dir='', num_landmarks=32, num_points=50, lmOn=True, curvOn=True, torsOn=True, use_smote=False):
    nb_features = num_landmarks + int(curvOn) + int(torsOn)
    if train_dir:
        dataset, labels, names = read_training(train_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)

        ##output descritpion file
        with open(os.path.join(train_dir, 'dataset_description.json'), 'w') as json_description_file:
            dictionary = { 'directory' : train_dir, 'num_landmarks' : num_landmarks, 'num_points' : num_points, 'lmOn' : lmOn, 'curvOn' : curvOn, 'torsOn' : torsOn, 'smote' : use_smote }
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

        convert_to(validation_set, 'validation', train_dir)
        convert_to(testing_set, 'testing', train_dir)
        convert_to(training_set, 'train', train_dir)

    elif valid_dir:
        valid_set = read_training(valid_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)

        #   Convert to Examples and write the result to TFRecords.
        convert_to(valid_set, 'valid', valid_dir)

    elif test_dir:
        data, names = read_testing(test_dir, original_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)
        data = data.reshape(len(data), nb_features, num_points)
        print (np.shape(data))
        return data, names


def main(_):
    run_store(FLAGS.train_dir, FLAGS.valid_dir, FLAGS.test_dir,  FLAGS.original_dir, FLAGS.num_landmarks, FLAGS.num_points, FLAGS.landmarks, FLAGS.curvature, FLAGS.torsion, FLAGS.use_smote)
  # Get the data.



if __name__ == '__main__':
    tf.app.run()
