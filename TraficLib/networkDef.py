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
        stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
        tf.scalar_summary('stddev_' + name, stddev)
        tf.scalar_summary('max_' + name, tf.reduce_max(var))
        tf.scalar_summary('min_' + name, tf.reduce_min(var))
        tf.histogram_summary('histogram_' + name, var)

def inference(train_data, num_hidden, num_labels, is_training, num_layers, reuse=False):

    train_data = tf.layers.batch_normalization(train_data, training=is_training)
    if num_layers < 1:
        print('Error: number of layers should be at least 1')
        num_layers = 1
    
    layer = tf.layers.dense(inputs=train_data, units=8192, activation=tf.nn.relu)
    layer2 = tf.layers.dense(inputs=layer, name='layer1', units=4096   , activation=tf.nn.relu)
    layer3 = tf.layers.dense(inputs=layer2, name='layer2', units=2048, activation=tf.nn.relu)
    layer4 = tf.layers.dense(inputs=layer3, name='layer3', units=1024, activation=tf.nn.relu)
    layer5 = tf.layers.dense(inputs=layer4, name='layer4', units=1024, activation=tf.nn.relu)
    layer6 = tf.layers.dense(inputs=layer5, name='layer5', units=512, activation=tf.nn.relu)

    dropout = tf.layers.dropout(inputs=layer6, name='dropout', rate=0.95, training=is_training)
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

    fiber = tf.decode_raw(features['fiber_raw'], tf.float64)
    fiber = tf.cast(fiber, tf.float32)
    if label_type_int64:
        label = tf.decode_raw(features['label'], tf.int64)
        label.set_shape([1])
    else:
        label = features['label']

    return fiber, label

def inputs(dir,  batch_size, num_epochs, conv=False, record_name='train.tfrecords'):

    if not num_epochs:
        num_epochs = None

    label_int = True
    filename = os.path.join(dir, record_name)

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

        print("Fiber Shape :", fiber.get_shape())
        print("Label Shape :", label.get_shape())
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
    print ("")
    print_tensor_shape(labels, "labels")
    print_tensor_shape(logits, "logits")
    size = 100/batch_size

    eval = tf.nn.in_top_k(logits, labels, k=1)
    eval = tf.reshape(eval, [-1])
    print_tensor_shape(eval, "eval")
    non_zero = tf.count_nonzero(eval)
    acc = tf.scalar_mul(size, non_zero)
    return acc

def print_tensor_shape(tensor, string):
# input: tensor and string to describe it
    if __debug__:
        print('DEBUG ' + string, tensor.get_shape())
