import numpy as np
import argparse
import os
import tensorflow as tf
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
    num_feat = 0
    if landmarks:
        num_feat+=num_landmarks
    if curvature:
        num_feat+=1
    if torsion:
        num_feat+=1

    # Shuffle data
    permutation = np.random.permutation(num_fib)
    # dataset = np.asrray(dataset)[permutation]
    # labels = np.asrray(labels)[permutation]

    # Create an instance of the class train_data where we are going to store our training data
    train_data = data_set(num_fib, num_feat, num_points)
    data_t = train_data.data
    # print ""
    # print np.asarray(labels)[permutation[50]]
    # print ""
    # print np.asarray(dataset)[permutation[50]]
    # print ""
    # print np.asarray(labels)[permutation[50]]
    # print ""
    # print np.asarray(dataset)[permutation[50]]

    for i in xrange(num_fib):
        data_t[i] = dataset[permutation[i]]
        dataset[permutation[i]] = []
    del dataset
    train_data.labels=np.asarray(labels)[permutation]
    del labels
    # train_data.data = np.asarray(dataset)[permutation]
    # del dataset
    # train_data.labels = np.asarray(labels)[permutation]
    # print train_data.labels[50]
    # print ""
    # print train_data.data[50]
    # for i in xrange(50):
    #     print train_data.labels[i]
    #     sys.stdout.flush()
    
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
    data_t = test_data.data
    for i in xrange(num_fib):
        data_t[i] = dataset[0]
        del dataset[0]
    test_data.labels=np.asarray(data_names)
    del data_names
    print "Testing Set :", test_data.data.shape
    return test_data
    
def run_store(train_dir='', valid_dir='', test_dir='', original_dir='', num_landmarks=5, num_points=50, lmOn=True, curvOn=True, torsOn=True):
    if train_dir:
        train_set = read_training(train_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)

        #   Convert to Examples and write the result to TFRecords.
        convert_to(train_set, 'train', train_dir)

    elif valid_dir:
        valid_set = read_training(valid_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)

        #   Convert to Examples and write the result to TFRecords.
        convert_to(valid_set, 'valid', valid_dir)

    elif test_dir:
        test_set = read_testing(test_dir, original_dir, num_landmarks, num_points, lmOn, curvOn, torsOn)

        # Convert to Examples and write the result to TFRecords.
        convert_to(test_set, 'test', test_dir)
        # Convert_to(test_set.validation, 'validation')


def main(_):
    run_store(FLAGS.train_dir, FLAGS.valid_dir, FLAGS.test_dir,  FLAGS.original_dir, FLAGS.num_landmarks, FLAGS.num_points, FLAGS.landmarks, FLAGS.curvature, FLAGS.torsion)
  # Get the data.



if __name__ == '__main__':
    tf.app.run()
