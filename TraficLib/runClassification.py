import time
import os.path
import tensorflow as tf
import numpy as np
import networkDef as nn

import sys
import json
import simplejson
from fiberfileIO import *

import shutil

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string('data_dir', '',
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

    list = fibername.split(":")
    if len(list) == 2:
        name = list[0]
        index = int(list[1])
        return name, index
    else:
        raise Exception("Non valid format for the file %s. "
                        "Impossible to extract name and index of the fiber" % fibername)


def reformat_prediction(predictions, num_classes):
    vector_id_blank = []
    for i in range(num_classes):
        vector_id_blank.append(vtk.vtkIdTypeArray())
    dict_pred = {}
    for pred_class, indexes in predictions.iteritems():
        if int(pred_class) > num_classes +1 or int(pred_class) < 0:
            continue
        if pred_class not in dict_pred.keys():
            dict_pred[pred_class] = vtk.vtkIdTypeArray()
        for index in indexes:
            dict_pred[pred_class].InsertNextValue(index)




    return dict_pred

def classification(dict, output_dir, num_classes, fiber_name, name_labels):
    # input: predictions    - prediction of the data to classify, dictionary where key=predicted class and value = array of indexes
    # input: name_labels    - containing the name of all the labels (classes)
    # input: test_names     - containing the name and index of each fibers
    # output: No output but at the end of this function, we write the positives fibers in one vtk file for each class
    #         Except the class 0

    append_list = np.ndarray(shape=num_classes, dtype=np.object)
    for i in xrange(num_classes):
        append_list[i] = vtk.vtkAppendPolyData()

    bundle_fiber = vtk.vtkPolyData()

    bundle_fiber = read_vtk_data(fiber_name)
    
    print dict.keys()
    for pred_class in dict.keys():
        if vtk.VTK_MAJOR_VERSION > 5:
            append_list[pred_class].AddInputData(extract_fiber(bundle_fiber, dict[pred_class]))
        else:
            append_list[pred_class].AddInput(extract_fiber(bundle_fiber, dict[pred_class]))

    for num_class in xrange(num_classes):
        if append_list[num_class].GetInput() is None or num_class == 0: #if the vtk file would be empty, then don't try to write it
            print "Skipped class ",num_class," because empty"
            continue
        append_list[num_class].Update()
        write_vtk_data(append_list[num_class].GetOutput(), output_dir+'/'+name_labels[num_class]+'_extracted.vtk')
        print ""

    # run_classification(num_hidden, data_dir, output_dir, checkpoint_dir, summary_dir, conv, multiclass)

def run_classification(data_dir, output_dir, checkpoint_dir, summary_dir, fiber_name="Fiber", conv=False):
    # Run evaluation on the input data set

    print (output_dir)
    if not os.path.exists(output_dir):
        print output_dir
        os.makedirs(output_dir)
    try:
        shutil.copyfile(os.path.join(checkpoint_dir, 'dataset_description.json'), os.path.join(output_dir, 'dataset_description.json'))
    except IOError:
        print 'Failed to copy'

    start = time.time()
    with tf.Graph().as_default() as g:

        #read training information
        with open(os.path.join(checkpoint_dir, 'dataset_description.json')) as json_desc_file:
            json_string = json_desc_file.read()
            description_dict = simplejson.loads(json_string)
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
            # fibers, labels = nn.inputs(data_dir, 'test', batch_size=1, num_epochs=1, conv=False)
            fibers, labels = run_store(test_dir=dir, num_landmarks=num_landmarks, num_points=num_points, lmOn=lmOn, curvOn=curvOn, torsOn=torsOn, use_smote=False)
            fibers = fibers.reshape(len(fibers), num_points * num_features)
            fibers = tf.convert_to_tensor(fibers, dtype=tf.float32)
            labels = tf.convert_to_tensor(labels, dtype=tf.string)           


            logits = nn.inference(fibers, num_hidden=num_hidden, num_labels=num_classes, is_training=False, num_layers=num_layers)


        # Conv Version
        else:
            fibers, labels = nn.inputs(data_dir, 'test', batch_size=1,
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
        print 'Starting tf session'
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
                step = 0
                while not coord.should_stop():
                    # run a single iteration of evaluation
                    val, pred, name = sess.run([predict_value, predict_class, labels])
                    for i in range(0,len(val[0])):
                        pred_lab = pred[0][i][0]
                        if not pred_lab in prediction:
                            prediction[pred_lab] = []

                        # if val >= threshold_labels[pred_lab]:
                        fiber_name, index = fibername_split(name[0][i]) #fetch the index
                        prediction[pred_lab].append(index)
                    step += 1
                    break
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
        pred_dictionnary = reformat_prediction(prediction, num_classes)
        classification(pred_dictionnary, output_dir, num_classes, data_dir + '/' + fiber_name, name_labels)
    end = time.time()

def main(_):
    start = time.time()
    run_classification(FLAGS.data_dir, FLAGS.output_dir, FLAGS.checkpoint_dir, FLAGS.summary_dir, FLAGS.fiber_name, FLAGS.conv)
    end = time.time()
    print YELLOW, "Classification Process took %dh%02dm%02ds" % (convert_time(end - start)), NC


if __name__ == '__main__':
    tf.app.run()
