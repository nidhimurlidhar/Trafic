import time
import os.path
import tensorflow as tf
import numpy as np
import networkDef as nn
import argparse
import sys
from fiberfileIO import *
from datetime import datetime
import shutil
import json
import zipfile

YELLOW = "\033[0;33m"
NC = "\033[0m"
flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_float('learning_rate', 0.000001, 'Initial learning rate.')
flags.DEFINE_integer('number_epochs', 3, 'Number of epochs to run trainer.')
flags.DEFINE_integer('batch_size', 5, 'Batch size.')
flags.DEFINE_string('input_dir', '',
                    'Directory with the training data.')
flags.DEFINE_string('checkpoint_dir', '',
                    """Directory where to write model checkpoints.""")
flags.DEFINE_string('summary', '',
                    """Directory where to write summary.""")
flags.DEFINE_string('model_description', '', 'Path to custom JSON model description, refer to documentation for format information')

def run_training(input_dir, checkpoint_dir, summary, number_epochs=3, learning_rate=0.000001, batch_size=5, model_description = ''):
    
    num_classes = 0

    checkpoint_dir = os.path.join(checkpoint_dir,datetime.now().strftime("%Y%m%d-%H%M%S"))
    if not os.path.isdir(checkpoint_dir):
        os.makedirs(checkpoint_dir)

    shutil.copy(os.path.join(input_dir, 'dataset_description.json'), os.path.join(checkpoint_dir, 'dataset_description.json'))

    description_dict = {}
    ## output json description file
    with open(os.path.join(checkpoint_dir, 'dataset_description.json'), 'r') as json_desc_file:
        json_string = json_desc_file.read()
        description_dict = json.loads(json_string)
        num_classes = len(description_dict['labels'])
        store_params = description_dict['store_parameters']
        num_landmarks = store_params['num_landmarks']
        num_points = store_params['num_points']
        lmOn = store_params['lmOn']
        curvOn = store_params['curvOn']
        torsOn = store_params['torsOn']
        num_features = num_landmarks * int(lmOn) + int(curvOn) + int(torsOn)

    model = None
    if model_description is '':
        print('Model shape not specified, using default.')
        model = {'layers':[
                {'name':'layer1', 'units':8192},
                {'name':'layer2', 'units':4096},
                {'name':'layer3', 'units':1024},
                {'name':'layer4', 'units':1024},
                {'name':'layer5', 'units':512}],
                'dropout_rate':0.95}
    else:
        with open(model_description, 'r') as json_model_file:
            model_string = json_model_file.read()
            model = json.loads(model_string)

    with open(os.path.join(checkpoint_dir, 'dataset_description.json'), 'w') as json_desc_file:
        training_parameters = {'batch_size' : batch_size, 'num_epochs' : number_epochs, 'input_dataset' : input_dir, 'checkpoint_directory' : checkpoint_dir, 'log_directory' : summary}
        training_parameters['model'] = model
        description_dict['training_parameters'] = training_parameters
        json_desc_file.write(json.dumps(description_dict, sort_keys=True, indent=4, separators=(',', ': ')))

    # with open(os.path.join(checkpoint_dir, 'dataset_description.json'), 'w') as json_desc_file:
        ## Output json configuration to tensorboard
        string_tensor = tf.constant(json.dumps(description_dict, sort_keys=True, indent=4, separators=(',', ': ')).replace('\n', '  \n').replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;'))
        tf.summary.text('parameters', string_tensor)


    # construct the graph
    with tf.Graph().as_default():
        # with tf.variable_scope('', reuse=tf.AUTO_REUSE):
        ## training data
        # Define inputs
        fibers, labels = nn.inputs(input_dir, batch_size=batch_size, num_epochs=number_epochs, conv=False)
        labels = tf.reshape(labels, [-1])


        # Define the network
        results = nn.inference(train_data=fibers, num_labels=num_classes, is_training=True, model=model)

        # Define metrics
        loss = nn.loss(results, labels)
        accuracy = nn.accuracy(results, labels)

        # Setup the training operations
        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(update_ops):
            train_op = nn.training(loss, learning_rate)

        # setup the summary ops to use TensorBoard
        summary_op = tf.summary.merge_all()

        # init to setup the initial values of the weights
        init_op = tf.group(tf.global_variables_initializer(),
                           tf.local_variables_initializer())

        # setup a saver for saving checkpoints
        saver = tf.train.Saver(save_relative_paths=True)

        # create the session
        sess = tf.Session()

        # specify where to write the log files for import to TensorBoard
        summary_writer = tf.summary.FileWriter(os.path.join(summary,datetime.now().strftime("%Y%m%d-%H%M%S")),
                                                graph=sess.graph)

        # initialize the graph
        sess.run(init_op)

        # setup the coordinato and threadsr.  Used for multiple threads to read data.
        # Not strictly required since we don't have a lot of data but typically
        # using multiple threads to read data improves performance
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess, coord=coord)


        cum_acc = 0
        cum_loss = 0

        print_delta = 500
        save_delta = 100000

        # loop will continue until we run out of input training cases
        try:
            step = 0
            while not coord.should_stop():

                # start time and run one training iteration
                start_time = time.time()
                _, loss_value, accuracy_value = sess.run([train_op, loss, accuracy])
                duration = time.time() - start_time
                cum_acc += accuracy_value
                cum_loss += loss_value
                if step % print_delta == 0:# and step is not 0:

                    print('Step %d: loss = %.12f, acc = %.10f (%.3f sec)' % (step, loss_value, accuracy_value, duration))
                    print('Since last step (cumulated): loss = %.12f, acc = %.10f' % (cum_loss / print_delta, cum_acc / print_delta))
                    cum_acc = 0
                    cum_loss = 0
                    print("")

                    sys.stdout.flush()

                    # output some data to the log files for tensorboard
                    summary_str = sess.run(summary_op)
                    summary_writer.add_summary(summary_str, step)
                    summary_writer.flush()

                # less frequently output checkpoint files.  Used for evaluating the model
                if step % save_delta == 0:
                    checkpoint_path = os.path.join(checkpoint_dir,
                                                   'model.ckpt')
                    saver.save(sess, checkpoint_path, global_step=step)
                    # _, testing_loss_value, testing_accuracy_value = sess.run([testing_op, testing_loss, testing_accuracy])
                    # print(testing_loss_value, testing_accuracy_value)
                  
                step += 1
                break
                # quit after we run out of input files to read
        except tf.errors.OutOfRangeError:
            print('Done training for %d epochs, %d steps.' % (number_epochs,
                                                              step))
            checkpoint_path = os.path.join(checkpoint_dir,
                                           'model.ckpt')
            saver.save(sess, checkpoint_path, global_step=step)

        finally:
            coord.request_stop()

        # shut down the threads gracefully
        coord.join(threads)
        sess.close()

        # Creating the archive
        with zipfile.ZipFile(os.path.join(checkpoint_dir, 'model.zip'), 'w') as model_zipfile:
            model_zipfile.write(checkpoint_dir, 'model')
            for root, dirs, files in os.walk(checkpoint_dir):
                for file in files:
                    if file != 'model.zip':
                        print('Zipping: ', file)
                        model_zipfile.write(os.path.join(root, file), os.path.join('model', file))
            model_zipfile.write(os.path.join(input_dir, 'landmarks.fcsv'), 'landmarks.fcsv')
            model_zipfile.write(os.path.join(checkpoint_dir, 'dataset_description.json'), 'dataset_description.json')


def main(_):
    start = time.time()
    run_training(FLAGS.input_dir, FLAGS.checkpoint_dir, FLAGS.summary, FLAGS.number_epochs, FLAGS.learning_rate, FLAGS.batch_size, FLAGS.model_description)
    end = time.time()
    print("Training Process took %dh%02dm%02ds" % (convert_time(end - start)))


if __name__ == '__main__':
    tf.app.run()
