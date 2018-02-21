
import numpy as np
import argparse
import os
import tensorflow as tf
import smote
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
    for label, folder in enumerate(folders):
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
    return np.array(dataset)[permutation], np.array(labels)[permutation]

def read_testing(test_dir, src_dir, num_landmarks, num_points, landmarks, curvature, torsion):
    dataset = []
    data_names = []
    fibers = [
        os.path.join(test_dir, d) for d in sorted(os.listdir(test_dir))
        if os.path.isfile(os.path.join(test_dir, d))]

    for fiber_file in fibers:
        if fiber_file.rfind(".vtk")!= -1 or fiber_file.rfind(".vtp")!= -1 :
            name_fiber = os.path.basename(fiber_file)
            name_src = os.path.join(src_dir, name_fiber)
            try:
                data_fiber, data_name = fiber_extract_feature(fiber_file, landmarks, curvature, torsion,
                                                      num_landmarks, num_points, name_src, train=False)
                dataset.extend(data_fiber.reshape((len(data_fiber),-1)))
                data_names.extend(data_name)
            except IOError as e:
                print('Could not read:', fiber_file, ':', e, '- it\'s ok, skipping.')
        else:
            print 'Could not read:', fiber_file, 'Not a vtk file ...Skipping.'
    
    return np.array(dataset), np.array(data_names)
    
def run_store(train_dir='', valid_dir='', test_dir='', original_dir='', num_landmarks=5, num_points=50, lmOn=True, curvOn=True, torsOn=True, use_smote=False):
    if train_dir:
        dataset, labels = read_training(train_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)
        if use_smote:
            dataset, labels = smote.generate_with_SMOTE(dataset.reshape(len(dataset),-1),labels)
            permutation = np.random.permutation(len(dataset))
            dataset = dataset[permutation]
            labels = labels[permutation]
            print('Smote success !')
        dataset = dataset.reshape(len(dataset), num_landmarks + 2, num_points)
    	train_set = data_set(len(dataset), num_landmarks + 2, num_points)
    	train_set.data = dataset
    	train_set.labels = labels
        print ('Final dataset shape: ', np.shape(train_set.data))
        #   Convert to Examples and write the result to TFRecords.
        convert_to(train_set, 'train', train_dir)

    elif valid_dir:
        valid_set = read_training(valid_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)

        #   Convert to Examples and write the result to TFRecords.
        convert_to(valid_set, 'valid', valid_dir)

    elif test_dir:
        data, names = read_testing(test_dir, original_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)
        data = data.reshape(len(data), num_landmarks + 2, num_points)
        print (np.shape(data))
        test_set = data_set(len(data), num_landmarks + 2, num_points)
        test_set.data = data
        test_set.labels = names 
        # Convert to Examples and write the result to TFRecords.
        convert_to(test_set, 'test', test_dir)
        # Convert_to(test_set.validation, 'validation')


def main(_):
    run_store(FLAGS.train_dir, FLAGS.valid_dir, FLAGS.test_dir,  FLAGS.original_dir, FLAGS.num_landmarks, FLAGS.num_points, FLAGS.landmarks, FLAGS.curvature, FLAGS.torsion, FLAGS.use_smote)
  # Get the data.



if __name__ == '__main__':
    tf.app.run()
