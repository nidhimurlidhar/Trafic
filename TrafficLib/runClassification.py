import time
import os.path
import tensorflow as tf
import numpy as np
import networkDef as nn

import sys
from fiberfileIO import *

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_integer('num_hidden', 1024, 'Number of hidden layers.')
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
flags.DEFINE_boolean('multiclass', False,
                         """Whether Multiclassification or Biclassification.""")
flags.DEFINE_string('fiber_name', "Fiber",
                         """In biclassification permit to know the name of the fiber to extract (By default: fiber_name = 'Fiber' which gives Fiber_extracted.vtk)""")


name_labels = [ '0', 'Arc_L_FT', 'Arc_L_FrontoParietal', 'Arc_L_TemporoParietal',  'Arc_R_FT', 'Arc_R_FrontoParietal', 'Arc_R_TemporoParietal',  'CGC_L',  'CGC_R',
                'CGH_L',  'CGH_R',  'CorpusCallosum_Genu',  'CorpusCallosum_Motor', 'CorpusCallosum_Parietal',  'CorpusCallosum_PreMotor',  'CorpusCallosum_Rostrum',
                'CorpusCallosum_Splenium',  'CorpusCallosum_Tapetum', 'CorticoFugal-Left_Motor',  'CorticoFugal-Left_Parietal', 'CorticoFugal-Left_PreFrontal',
                'CorticoFugal-Left_PreMotor', 'CorticoFugal-Right_Motor', 'CorticoFugal-Right_Parietal',  'CorticoFugal-Right_PreFrontal',  'CorticoFugal-Right_PreMotor',
                'CorticoRecticular-Left', 'CorticoRecticular-Right',  'CorticoSpinal-Left', 'CorticoSpinal-Right',  'CorticoThalamic_L_PreFrontal', 'CorticoThalamic_L_SUPERIOR',
                'CorticoThalamic_Left_Motor', 'CorticoThalamic_Left_Parietal',  'CorticoThalamic_Left_PreMotor',  'CorticoThalamic_R_PreFrontal', 'CorticoThalamic_R_SUPERIOR',
                'CorticoThalamic_Right_Motor',  'CorticoThalamic_Right_Parietal', 'CorticoThalamic_Right_PreMotor', 'Fornix_L', 'Fornix_R', 'IFOF_L', 'IFOF_R', 'ILF_L',  'ILF_R',
                'OpticRadiation_Left',  'OpticRadiation_Right', 'Optic_Tract_L',  'Optic_Tract_R',  'SLF_II_L', 'SLF_II_R', 'UNC_L',  'UNC_R']

threshold_labels = [1,  1,  0.9995, 0.99999,  1,  0.945,  0.995,  0.99999,  0.9999, 0.58995,  0.58995,  0.99995,  0.9999, 0.99995,  1,  0.9999, 1,  1,  0.35, 0.79995,
                    1,  0.9999, 0.59995,  0.89995,  0.6,  0.97495,  0.475,  0.55, 0.575,  0.875,  1,  0.8,  0.45, 0.925,  0.35, 1,  0.4,  0.35, 0.945,  0.4,  0.97495,
                    0.9999, 0.99995,  0.99995,  0.99995,  1,  0.9999, 0.99995,  0.25, 0.99995,  1,  1,  1,  1 ]

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
    for num_class in range(num_classes):
        for num_fib in range(len(predictions[num_class])):
            key, value = fibername_split(predictions[num_class][num_fib])

            if key not in dict_pred.keys():
                dict_pred[key] = vector_id_blank
            dict_pred[key][num_class].InsertNextValue(value)
    return dict_pred

def classification(dict, output_dir, num_classes, multiclass, fiber_name):
    # input: predictions    - prediction of the data to classify, size [num_fibers]x[num_labels]
    # input: name_labels    - containing the name of all the labels (classes)
    # input: test_names     - containing the name and index of each fibers
    # output: No output but at the end of this function, we write the positives fibers in one vtk file for each class
    #         Except the class 0


    # Create the output directory if necessary
    if not os.path.exists(os.path.dirname(output_dir)):
        os.makedirs(output_dir)
    append_list = np.ndarray(shape=num_classes, dtype=np.object)
    for i in xrange(num_classes-1):
        append_list[i] = vtk.vtkAppendPolyData()

    bundle_fiber = vtk.vtkPolyData()
    for fiber in dict.keys():
        bundle_fiber = read_vtk_data(fiber)
        for num_class in xrange(num_classes-1):
            if vtk.VTK_MAJOR_VERSION > 5:
                append_list[num_class].AddInputData(extract_fiber(bundle_fiber, dict[fiber][num_class+1]))
            else:
                append_list[num_class].AddInput(extract_fiber(bundle_fiber, dict[fiber][num_class+1]))
    for num_class in xrange(num_classes-1):
        append_list[num_class].Update()
        if multiclass:
          write_vtk_data(append_list[num_class].GetOutput(), output_dir+'/'+name_labels[num_class+1]+'_extracted.vtk')
        else:
          write_vtk_data(append_list[num_class].GetOutput(), output_dir+'/'+fiber_name+'_extracted.vtk')
        print ""

    # run_classification(num_hidden, data_dir, output_dir, checkpoint_dir, summary_dir, conv, multiclass)

def run_classification(data_dir, output_dir, checkpoint_dir, summary_dir, num_hidden=1024,  fiber_name="Fiber", conv=False, multiclass=False):
    # Run evaluation on the input data set
    if multiclass:
      num_classes = 54
    else:
      num_classes = 2
    start = time.time()
    with tf.Graph().as_default() as g:

        # Build a Graph that computes the logits predictions from the
        # inference model.  We'll use a prior graph built by the training

        # Non Conv Version
        if not conv:
            fibers, labels = nn.inputs(data_dir, 'test', batch_size=1, num_epochs=1, conv=False)
            logits = nn.inference(fibers, num_hidden, num_classes, is_training=False)


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
        sess.run(local_init)

        while True:
            prediction = []
            for i in range(num_classes):
                prediction.append([])

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
                    #                    predictions = sess.run([top_k_op])
                    val, pred, name = sess.run([predict_value, predict_class, labels])

                    pred_lab = pred[0][0]
                    pred_val = val[0][0]
                    prediction[pred_lab].append(name[0])
                    # if multiclass and pred_val >= threshold_labels[pred_lab]:
                    #   prediction[pred_lab].append(name[0])
                    # elif not multiclass:
                    #   prediction[pred_lab].append(name[0])

                    step += 1
            except tf.errors.OutOfRangeError:
                summary = tf.Summary()
                summary.ParseFromString(sess.run(summary_op))
                # summary.value.add(tag='Precision @ 1', simple_value=precision)
                summary_writer.add_summary(summary, global_step)

            finally:
                coord.request_stop()

            # shutdown gracefully
            coord.join(threads)
            # if run_once:
            break
        sess.close()
        # print "prediction\n", prediction
        pred_dictionnary = reformat_prediction(prediction, num_classes)
        classification(pred_dictionnary, output_dir, num_classes, multiclass, fiber_name)
    end = time.time()



def main(_):
    start = time.time()
    run_classification(FLAGS.data_dir, FLAGS.output_dir, FLAGS.checkpoint_dir, FLAGS.summary_dir, FLAGS.num_hidden,  FLAGS.fiber_name, FLAGS.conv, FLAGS.multiclass)
    end = time.time()
    print YELLOW, "Classification Process took %dh%02dm%02ds" % (convert_time(end - start)), NC


if __name__ == '__main__':
    tf.app.run()
