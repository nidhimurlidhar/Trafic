import sys
from fiberfileIO import read_vtk_data
import numpy as np
import resource
import os
import tensorflow as tf
import gc


class data_set:
    def __init__(self, height, rows, cols):
        self.data = np.ndarray(shape=(height, rows, cols))
        self.labels = np.ndarray(shape=height)

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def convert_to(fibers, labels, name, directory):
    """Converts a dataset to tfrecords."""
    # fibers = data_set.data
    # labels = data_set.labels

    num_fib = len(fibers) #.shape[0]

    if len(labels) != num_fib:
        raise ValueError('size %d does not match label size %d.' %
                         (num_fib, len(labels)))
    rows = len(fibers[0])
    cols = len(fibers[0][0])

    filename = os.path.join(directory, name + '.tfrecords')
    print('Writing', filename)
    sys.stdout.flush()
    writer = tf.python_io.TFRecordWriter(filename)
    for index in xrange(num_fib):
        # print "Label:", labels[index].dtype
        fiber_raw = np.array(fibers[index]).tostring()
        example = tf.train.Example(features=tf.train.Features(feature={
            'num_features': _int64_feature(rows),
            'num_points': _int64_feature(cols),
            'label': _bytes_feature(np.array(labels[index]).tostring()),
            'fiber_raw': _bytes_feature(fiber_raw)}))
        writer.write(example.SerializeToString())
    writer.close()


def fiber_extract_feature(fiber_file, lmOn, curveOn, torsOn, num_landmarks, num_points, label, train=False):
    array_name = []
    dataset = []
    labels = []
    # print "============================================="
    # print fiber_file
    # print "Memory usage 1: %s (kb)" % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    fiber = read_vtk_data(fiber_file)
    # print "Memory usage 2: %s (kb)" % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    nb_fibers = fiber.GetNumberOfCells()
    nb_features = 0
    if lmOn:
        nb_features += num_landmarks
        for i in xrange(0, num_landmarks):
            array_name.append("Distance2Landmark" + str(i+1))
    if curveOn:
        nb_features += 1
        array_name.append("curvature")
    if torsOn:
        nb_features += 1
        array_name.append("torsion")
    
    fiber_data = np.ndarray(shape=(nb_features, num_points), dtype=np.float64)
    for k in xrange(0, nb_fibers):

        for i in xrange(0, nb_features):
            feature_array = fiber.GetPointData().GetScalars(array_name[i])
            for j in xrange(k*num_points, (k+1)*num_points):
                fiber_data[i, j % num_points] = feature_array.GetTuple1(j)
            del feature_array

        # Find a better normalization
        # max_value = np.amax(fiber_data, 1)
        # min_value = np.amin(fiber_data, 1)
        # for l in range(0, nb_features):
        #     fiber_data[l, :] = (fiber_data[l, :] - (max_value[l] + min_value[l]) / 2) / \
        #                        (max_value[l] - min_value[l])
        if fiber_data.shape != (nb_features, num_points):
            raise Exception('Unexpected image shape: %s' % str(fiber_data.shape))
        dataset.append(fiber_data)

        if train:   # If it's a training
            labels.append(label)
        else:   # If it's a testing
            labels.append(label+":"+str(k))
        # del fiber_data
        # print fiber_data
    # del fiber
    # del fiber_data
    # gc.collect()
    # print "Memory usage 3: %s (kb)" % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # print "============================================="
    # print ""
    return dataset, labels
