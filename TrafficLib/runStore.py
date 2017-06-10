import numpy as np
import argparse
import os
import tensorflow as tf

from storeDef import *

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string('train_dir', '',    ' training input directory')
flags.DEFINE_string('test_dir', '',    ' training input directory')
flags.DEFINE_string('valid_dir', '',    ' training input directory')
flags.DEFINE_string('original_dir', '/root/work/Multiclass/Test/',    ' Oiginal input Test directory before pre processing')
flags.DEFINE_integer('num_landmarks',  5,      'Number of landmarks')
flags.DEFINE_integer('num_points',  50,      'Number of points on each fiber')
flags.DEFINE_boolean('landmarks', False, 'Compute landmarks features')
flags.DEFINE_boolean('curvature', False, 'Compute curvature features')
flags.DEFINE_boolean('torsion', False, 'Compute torsions features')


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
                dataset += data_fiber
                labels += data_label
            except IOError as e:
                print('Could not read:', fiber_file, ':', e, '- it\'s ok, skipping.')
    num_fib = len(dataset)
    num_feat = len(dataset[0])
    num_pt = len(dataset[0][0])

    # Shuffle data
    permutation = np.random.permutation(num_fib)
    dataset = np.array(dataset)[permutation]
    labels = np.array(labels)[permutation]

    # Create an instance of the class train_data where we are going to store our training data
    train_data = data_set(num_fib, num_feat, num_pt)
    train_data.data = dataset[0:num_fib]
    train_data.labels = labels[0:num_fib]
    print "Data Set :", train_data.data.shape

    return train_data


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
                dataset += data_fiber
                data_names += data_name
            except IOError as e:
                print('Could not read:', fiber_file, ':', e, '- it\'s ok, skipping.')
        else:
            print 'Could not read:', fiber_file, 'Not a vtk file ...Skipping.'

    num_fib = len(dataset)
    num_feat = len(dataset[0])
    num_pt = len(dataset[0][0])
    print "Nb Fibers:", num_fib
    print "Nb Features:", num_feat
    print "Nb Points:", num_pt

    # Create an instance of the class train_data where we are going to store our training data
    test_data = data_set(num_fib, num_feat, num_pt) # type_lab=np.str, type_dat=np.float64)
    test_data.data = np.array(dataset)
    test_data.labels = np.array(data_names)
    print "Testing Set :", test_data.data.shape


def run_store(train_dir='', valid_dir='', test_dir='', num_landmarks=5, num_points=50, lmOn=False, curvOn=False, torsOn=False):
    if train_dir:
        train_set = read_training(train_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)

        #   Convert to Examples and write the result to TFRecords.
        convert_to(train_set, 'train', train_dir)

    if valid_dir:
        valid_set = read_training(valid_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)

        #   Convert to Examples and write the result to TFRecords.
        convert_to(valid_set, 'valid', valid_dir)

    if test_dir:
        test_set = read_testing(test_dir, original_dir, num_landmarks, lmOn, curvOn, torsOn)

        # Convert to Examples and write the result to TFRecords.
        convert_to(test_set, 'test', test_dir)
        # Convert_to(test_set.validation, 'validation')


def main(_):
    run_store(FLAGS.train_dir, FLAGS.test_dir, FLAGS.valid_dir, FLAGS.original_dir, FLAGS.original_dir, FLAGS.num_landmarks, FLAGS.num_points, FLAGS.landmarks, FLAGS.curvature, FLAGS.torsion)
  # Get the data.



if __name__ == '__main__':
    tf.app.run()