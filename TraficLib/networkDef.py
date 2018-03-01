import tensorflow as tf
import numpy as np
import os
from runStore import run_store

TRAIN_FILE = 'train.tfrecords'
VALIDATION_FILE = 'valid.tfrecords'
TEST_FILE = 'test.tfrecords'

def accuracy(predictions, labels):
    
    acc = (100 * tf.count_nonzero(tf.equal(tf.argmax(predictions, axis=1),labels)) / (int)(np.shape(predictions)[0]))
    tf.summary.scalar('accuracy', acc, family='test')
    
    return acc

def variable_summaries(var, name):
    # Attach a lot of summaries to a Tensor (for TensorBoard visualization).

    with tf.name_scope('summaries_'+ name):
        mean = tf.reduce_mean(var)
        tf.scalar_summary('mean_' + name, mean)
        #with tf.name_scope('stddev'):
        stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
        tf.scalar_summary('stddev_' + name, stddev)
        tf.scalar_summary('max_' + name, tf.reduce_max(var))
        tf.scalar_summary('min_' + name, tf.reduce_min(var))
        tf.histogram_summary('histogram_' + name, var)

def inference(train_data, num_hidden, num_labels, is_training, num_layers):
    # input:    train_data      - train tensor [batch_size, num_data]
    # input:    num_hidden      - number of hidden layers
    # input:    num_data        - num_feature*num_points
    # input:    num_labels      - number of labels
    # input:    valid_data      - valid tensor
    # output:   logits          - tensor of computed train_logits
    # output:   valid           - tensor of computed valid_logits
    # output:   saver           - saver of the model

    train_data = tf.layers.batch_normalization(train_data, training=is_training)
    if num_layers < 1:
        print 'Error: number of layers should be at least 1'
        num_layers = 1
    
    layer = tf.layers.dense(inputs=train_data, name='layer0', units=8192, activation=tf.nn.relu)
    layer2 = tf.layers.dense(inputs=layer, name='layer1', units=4096   , activation=tf.nn.relu)
    layer3 = tf.layers.dense(inputs=layer2, name='layer2', units=2048, activation=tf.nn.relu)
    layer4 = tf.layers.dense(inputs=layer3, name='layer3', units=1024, activation=tf.nn.relu)
    layer5 = tf.layers.dense(inputs=layer4, name='layer4', units=512, activation=tf.nn.relu)
    
    # if num_layers > 1:
    #     for i in xrange(1,num_layers):
    #         layer = tf.layers.dense(inputs=layer, name='layer' + str(i), units=num_hidden, activation=tf.nn.relu)

    dropout = tf.layers.dropout(inputs=layer4, name='dropout', rate=0.5, training=is_training)
    final = tf.layers.dense(inputs=dropout, name='final', units=num_labels, activation=None)

    return final


def loss(logits, labels):
    # input:    logits      - logits tensor, [batch_size, num_labels]
    # input:    labels      - labels tensor, [batch_size, num_labels]
    # output:   loss        - loss tensor of type float.

    loss = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=labels, logits=logits)
    loss = tf.reduce_mean(loss)

    tf.summary.scalar('loss', loss, family='test')

    return loss


def training(l, lr):
    # input: l          -loss tensor from loss()
    # input: lr         - learning_rate scalar for gradient descent
    # output: train_op  - the operation for training

    # train_op = tf.train.GradientDescentOptimizer(learning_rate=lr).minimize(l)
    train_op = tf.train.AdamOptimizer(learning_rate=lr).minimize(l)

    return train_op

def read_and_decode(filename_queue, label_type_int64):
    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)
    features = tf.parse_single_example(
      serialized_example,
      # Defaults are not specified since both keys are required.
      features={
          'fiber_raw': tf.FixedLenFeature([], tf.string),
          'label': tf.FixedLenFeature([], tf.string),
      })
    # Convert from a scalar string tensor (whose single string has

    fiber = tf.decode_raw(features['fiber_raw'], tf.float64)
    fiber = tf.cast(fiber, tf.float32)
    if label_type_int64:
        label = tf.decode_raw(features['label'], tf.int64)
        label.set_shape([1])
    else:
        label = features['label']

    return fiber, label

def inputs(dir,  batch_size, num_epochs, conv=False):
    """Reads input data num_epochs times.
    Args:
    train: Selects between the training (True) and validation (False) data.
    batch_size: Number of examples per returned batch.
    num_epochs: Number of times to read the input data, or 0/None to
       train forever.
    Returns:
    A tuple (images, labels), where:
    * images is a float tensor with shape [batch_size, mnist.IMAGE_PIXELS]
      in the range [-0.5, 0.5].
    * labels is an int32 tensor with shape [batch_size] with the true label,
      a number in the range [0, mnist.NUM_CLASSES).
    Note that an tf.train.QueueRunner is added to the graph, which
    must be run using e.g. tf.train.start_queue_runners().
    """

    if not num_epochs:
        num_epochs = None

    label_int = True
    filename = os.path.join(dir, TRAIN_FILE)

    record_iterator = tf.python_io.tf_record_iterator(path=filename)

    for string_record in record_iterator:
        break
    example = tf.train.Example()
    example.ParseFromString(string_record)

    nb_pts = int(example.features.feature['num_points'].int64_list.value[0])

    nb_ft = int(example.features.feature['num_features'].int64_list.value[0])


    with tf.name_scope('input'):
        filename_queue = tf.train.string_input_producer(
            [filename], num_epochs=num_epochs)

        # Even when reading in multiple threads, share the filename
        # queue.
        fiber, label = read_and_decode(filename_queue, label_int)

        fiber.set_shape([nb_pts*nb_ft])

        if conv:
            fiber = tf.reshape(fiber, [nb_ft, nb_pts])

        print "Fiber Shape :", fiber.get_shape()
        print "Label Shape :", label.get_shape()
        # Shuffle the examples and collect them into batch_size batches.
        # (Internally uses a RandomShuffleQueue.)
        # We run this in two threads to avoid being a bottleneck.
        fibers, sparse_labels = tf.train.shuffle_batch(
            [fiber, label], batch_size=batch_size, num_threads=4,
            capacity=10000 + 3 * batch_size,
            # Ensures a minimum amount of shuffling of examples.
            min_after_dequeue=10000)
    return fibers, sparse_labels


def reformat_conv(dataset, num_features, num_points, labels, num_labels):
    num_channels = 1
    dataset = dataset.reshape(
        (-1, num_features, num_points)).astype(np.float32)
    labels = (np.arange(num_labels) == labels[:, None]).astype(np.float32)
    return dataset, labels


def evaluation (logits, labels, batch_size):
    # input: logits: Logits tensor, float - [batch_size, 256, 256, NUM_CLASSES].
    # input: labels: Labels tensor, int32 - [batch_size, 256, 256]
    # output: scaler int32 tensor with number of examples that were
    #         predicted correctly
    logits = tf.cast(logits, dtype=tf.float32)
    labels = tf.reshape(labels, [-1])
    print ""
    print_tensor_shape(labels, "labels")
    print_tensor_shape(logits, "logits")
    size = 100/batch_size # = 100*(1/batch_size)

    # _, eval = tf.nn.top_k(logits, k=1)
    eval = tf.nn.in_top_k(logits, labels, k=1)
    # eval = tf.cast(eval, dtype=tf.int8)
    eval = tf.reshape(eval, [-1])
    print_tensor_shape(eval, "eval")
    # num_true = tf.where(eval)
    non_zero = tf.count_nonzero(eval)
    # print_tensor_shape(non_zero, "non_zero")
    acc = tf.scalar_mul(size, non_zero)
    # print_tensor_shape(acc, "acc")
    return acc

def print_tensor_shape(tensor, string):
# input: tensor and string to describe it
    if __debug__:
        print('DEBUG ' + string, tensor.get_shape())


def inference_conv(train_data, patch_size, num_features, num_points, num_hidden, num_labels, is_training):
    # Variables.
    # print "data", data.get_shape()
    train_data = tf.cast(train_data, tf.float32)
    depth = 100
    w_1 = tf.Variable(tf.truncated_normal(
        [patch_size, num_features, num_features], stddev=0.1, dtype=tf.float32))
    # b_1 = tf.Variable(tf.zeros([num_points]))
    w_1_2 = tf.Variable(tf.truncated_normal(
        [patch_size, num_features, depth], stddev=0.1, dtype=tf.float32))

    w_2 = tf.Variable(tf.truncated_normal(
        [patch_size, depth, depth], stddev=0.1, dtype=tf.float32))
    b_2 = tf.Variable(tf.constant(1.0, shape=[num_points]))

    w_3 = tf.Variable(tf.truncated_normal(
        [patch_size, patch_size, depth/2, depth], stddev=0.1, dtype=tf.float32))

    w_3_1 = tf.Variable(tf.truncated_normal(
        [patch_size, patch_size, depth, depth], stddev=0.1, dtype=tf.float32))

    # w_4 = tf.Variable(tf.truncated_normal(
    #     [depth * depth, num_hidden], stddev=0.1))
    # w_4 = tf.Variable(tf.truncated_normal(
    #     [num_points * depth, num_hidden], stddev=0.1))
    w_4 = tf.Variable(tf.truncated_normal(
        [num_points * depth, num_hidden], stddev=0.1, dtype=tf.float32))
    b_4 = tf.Variable(tf.constant(1.0, shape=[num_hidden], dtype=tf.float32))
    w_final = tf.Variable(tf.truncated_normal(
        [num_hidden, num_labels], stddev=0.1, dtype=tf.float32))
    b_final = tf.Variable(tf.constant(1.0, shape=[num_labels], dtype=tf.float32))

    # Model.
    def model(data):
        with tf.name_scope('Layer1'):
            data = batch_norm(data, is_training)
            # data = tf.expand_dims(data, 3)
            conv = tf.nn.conv1d(data, w_1, 1, padding='SAME', data_format="NCHW")
            print "conv:", conv.get_shape()
            # hidden = tf.nn.relu(conv + b_1)
            hidden = tf.nn.relu(conv)
            # hidden = batch_norm(hidden, num_points)
            print "hidden:", hidden.get_shape()

        with tf.name_scope('Layer2'):
            # hidden = batch_norm(hidden, is_training)
            conv = tf.nn.conv1d(hidden, w_1_2, 1, padding='SAME', data_format="NCHW")
            print "conv:", conv.get_shape()
            hidden = tf.nn.relu(conv)
            print "hidden:", hidden.get_shape()

        # with tf.name_scope('Layer3'):
        #     # hidden = batch_norm(hidden, is_training)
        #     hidden = tf.expand_dims(hidden, 3)
        #     conv = tf.nn.conv2d(hidden, w_3, [1, 1, 1, 1], padding='SAME', data_format="NCHW")
        #     print "conv:", conv.get_shape()
        #     hidden = tf.nn.relu(conv)
        #     print "hidden:", hidden.get_shape()

        # with tf.name_scope('Layer4'):
            # conv = tf.nn.conv1d(hidden, w_2, 1, padding='SAME', data_format="NCHW")
            # print "conv:", conv.get_shape()
            # hidden = tf.nn.relu(conv)
            # print "hidden:", hidden.get_shape()

        # with tf.name_scope('Layer5'):
            # conv = tf.nn.conv2d(hidden, w_3_1, [1, 1, 1, 1], padding='SAME', data_format="NCHW")
            # print "conv:", conv.get_shape()
            # hidden = tf.nn.relu(conv)
            # print "hidden:", hidden.get_shape()

        # with tf.name_scope('Layer6'):
            # conv = tf.nn.conv1d(hidden, w_3, 1, padding='SAME')
            # print "conv:", conv.get_shape()
            # hidden = tf.nn.relu(conv)
            # print "hidden:", hidden.get_shape()

        # with tf.name_scope('Layer7'):
            # conv = tf.nn.conv1d(hidden, w_2, 1, padding='SAME')
            # print "conv:", conv.get_shape()
            # hidden = tf.nn.relu(conv)
            # print "hidden:", hidden.get_shape()
        with tf.name_scope('LastLayer'):
            # hidden = tf.squeeze(hidden, [3])
            # hidden = batch_norm(hidden, is_training)
            shape = hidden.get_shape().as_list()
            print "shape", shape
            reshape = tf.reshape(hidden, [shape[0], shape[1] * shape[2]])
            hidden = tf.nn.relu(tf.matmul(reshape, w_4) + b_4)
        # hidden = batch_norm(hidden, num_hidden)
        # hidden = batch_norm(hidden, is_training)
        return tf.matmul(hidden, w_final) + b_final

    logits = model(train_data)

    return logits #, valid, saver
#     with tf.name_scope('Hidden1'):
#         w_1 = tf.Variable(
#             tf.truncated_normal([num_data, num_hidden]), name='w_1')
#         b_1 = tf.Variable(tf.zeros([num_hidden]), name='b_1')
#         h_final = tf.nn.relu(tf.matmul(train_data, w_1) + b_1)
#
#     # with tf.name_scope('Hidden2'):
#     #     w_2 = tf.Variable(
#     #         tf.truncated_normal([num_hidden, num_hidden]), name='w_2')
#     #     b_2 = tf.Variable(tf.zeros([num_hidden]), name='b_2')
#     #     h_final = tf.nn.relu(tf.matmul(h_1, w_2) + b_2)
#
#     with tf.name_scope('Final'):
#         w_final = tf.Variable(
#             tf.truncated_normal([num_hidden, num_labels]), name='w_final')
#         b_final = tf.Variable(tf.zeros([num_labels]), name='b_final')
#         logits = tf.matmul(h_final, w_final) + b_final
#     # tf.histogram_summary("Logits", logits)
#
#     saver = tf.train.Saver({"w_1": w_1, "b_1": b_1, "w_final": w_final, "b_final": b_final}, max_to_keep=10000)
#
#     if valid_data is not None:
#         valid = tf.matmul(tf.nn.relu(tf.matmul(valid_data, w_1) + b_1), w_final) + b_final
#     else:
#         valid = None
#     return logits, valid, saver
