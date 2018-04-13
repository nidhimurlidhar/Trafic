import time
import os.path
import tensorflow as tf
import numpy as np
import networkDef as nn

import sys
import json
# import json
from fiberfileIO import *

import shutil

from runStore import read_testing

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string('data_file', '',
                    'Directory with the training data.')
flags.DEFINE_string('output_dir', '/root/work/Multiclass/Results/',
                    'Output directory')
flags.DEFINE_string('checkpoint_dir', '',
                    """Directory where to write model checkpoints.""")
flags.DEFINE_string('summary_dir', '/root/work/SaveTest/',
                    """Directory where to write model checkpoints.""")
flags.DEFINE_boolean('conv', False,
                         """Whether use conv version or no Conv.""")
flags.DEFINE_string('fiber_name', "Fiber",
                         """To know the name of the fiber to extract (By default: fiber_name = 'Fiber' which gives Fiber_extracted.vtk)""")


def fibername_split(fibername):
    # input: fibername      - designate a single fiber in the format [name of the fiber bundle]:[index of the fiber]
    # output: name          - name of the fiber bundle
    # output: index         - index the single fiber to extract
    fibername = fibername.decode('UTF-8')
    list = fibername.split(":")
    if len(list) == 2:
        name = list[0]
        index = int(list[1])
        return name, index
    else:
        raise Exception("Non valid format for the file %s. "
                        "Impossible to extract name and index of the fiber" % fibername)

def run_classification(data_file, output_dir, checkpoint_dir, summary_dir, fiber_name="Fiber", conv=False):
    # Run evaluation on the input data set

    print (output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        shutil.copyfile(os.path.join(checkpoint_dir, 'dataset_description.json'), os.path.join(output_dir, 'dataset_description.json'))
    except IOError:
        print ('Failed to copy')

    start = time.time()
    with tf.Graph().as_default() as g:

        #read training information
        with open(os.path.join(checkpoint_dir, 'dataset_description.json')) as json_desc_file:
            json_string = json_desc_file.read()
            description_dict = json.loads(json_string)
            name_labels = description_dict['labels']
            store_params = description_dict['store_parameters']
            train_params = description_dict['training_parameters']

        
            num_classes = len(name_labels)
        
            num_landmarks = store_params['num_landmarks']
            num_points = store_params['num_points']
            lmOn = store_params['lmOn']
            curvOn = store_params['curvOn']
            torsOn = store_params['torsOn']
            num_features = num_landmarks * int(lmOn) + int(curvOn) + int(torsOn)

            num_layers = train_params['nb_layers']
            num_hidden = train_params['num_hidden']
        # Build a Graph that computes the logits predictions from the
        # inference model.  We'll use a prior graph built by the training

        # Non Conv Version

        if not conv:
            fibers, labels = read_testing(fiber_file=data_file, num_landmarks=num_landmarks, num_points=num_points, landmarks=lmOn, curvature=curvOn, torsion=torsOn)
            fibers = fibers.reshape(len(fibers), num_points * num_features)
            fibers = tf.convert_to_tensor(fibers, dtype=tf.float32)
            labels = tf.convert_to_tensor(labels, dtype=tf.string)           

            # with tf.variable_scope("model") as scope:
            logits = nn.inference(fibers, num_hidden=num_hidden, num_labels=num_classes, is_training=False, num_layers=num_layers)


        # Conv Version
        else:
            fibers, labels = nn.inputs(data_file, 'test', batch_size=1,
                                      num_epochs=1, conv=True)

            logits = nn.inference_conv(fibers, 2, 34, 50, num_hidden, num_classes, is_training=False)

        logits = tf.nn.softmax(logits)
        predict_value, predict_class = tf.nn.top_k(logits, k=1)

        # setup the initialization of variables
        local_init = tf.local_variables_initializer()

        # Build the summary operation based on the TF collection of Summaries.
        summary_op = tf.summary.merge_all()
        summary_writer = tf.summary.FileWriter(summary_dir, g)

        # create the saver and session
        saver = tf.train.Saver()
        sess = tf.Session()

        # init the local variables
        print ('Starting tf session')
        sess.run(local_init)


        while True:
            prediction = {}

            # read in the most recent checkpointed graph and weights
            ckpt = tf.train.get_checkpoint_state(checkpoint_dir)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)
                global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
            else:
                print('No checkpoint file found in %s' % checkpoint_dir)
                return

            # start up the threads
            coord = tf.train.Coordinator()
            threads = tf.train.start_queue_runners(sess=sess, coord=coord)

            try:
                val, pred, name = sess.run([predict_value, predict_class, labels])
                for i in range(0,len(val)):
                    pred_lab = str(pred[i][0])
                    if not pred_lab in prediction:
                        prediction[pred_lab] = []
                    if val[i] >= 0.7:
                        fiber_name, index = fibername_split(name[i]) #fetch the index
                        prediction[pred_lab].append(index)
            except tf.errors.OutOfRangeError:
                summary = tf.Summary()
                summary.ParseFromString(sess.run(summary_op))
                summary_writer.add_summary(summary, global_step)

            finally:
                coord.request_stop()

            # shutdown gracefully
            coord.join(threads)
            break
        sess.close()

        with open(os.path.join(checkpoint_dir, 'dataset_description.json')) as json_desc_file:
            json_string = json_desc_file.read()
            description_dict = json.loads(json_string)

            prediction_strings={}
            for key in prediction.keys():
                prediction_strings[key] = json.dumps(prediction[key])
            description_dict['predictions'] = prediction_strings
            
            with open(os.path.join(output_dir, 'classification_output.json'), 'w') as output_file:
                print ('Writing output file')
                output_json_string = json.dumps(description_dict, sort_keys=True, indent=4, separators=(',', ': '))
                output_file.write(output_json_string)
    end = time.time()

def main(_):
    start = time.time()
    run_classification(FLAGS.data_file, FLAGS.output_dir, FLAGS.checkpoint_dir, FLAGS.summary_dir, FLAGS.fiber_name, FLAGS.conv)
    end = time.time()
    print (YELLOW, "Classification Process took %dh%02dm%02ds" % (convert_time(end - start)), NC)


if __name__ == '__main__':
    tf.app.run()
