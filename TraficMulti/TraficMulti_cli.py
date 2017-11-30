import numpy as np
import argparse
import os
import tensorflow as tf
from os import path, sys
from shutil import rmtree
import subprocess


TRAFIC_LIB_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), "TraficLib")
sys.path.append(TRAFIC_LIB_DIR)
print path.join(TRAFIC_LIB_DIR)
from makeDataset import run_make_dataset
from envInstallTF import runMaybeEnvInstallTF


flags = tf.app.flags
FLAGS = flags.FLAGS

flags.DEFINE_boolean('biclassification', False, 'Compute torsions features')
flags.DEFINE_boolean('multiclassification', False, 'Compute torsions features')
flags.DEFINE_string('class_input_fiber', '', 'Input fiber to classify')
flags.DEFINE_string('class_output', '', 'Output directory')
flags.DEFINE_string('class_summary', '', 'Output summary directory')
flags.DEFINE_string('class_displacement', '', 'Displacement field to PED_1yr-2yr atlas')
flags.DEFINE_string('checkpoints', '', 'Tensorflow checkpoint directory')

flags.DEFINE_boolean('training', False, 'Compute torsions features')
flags.DEFINE_float('learning_rate', 0.010, 'Model learning rate (for training)')
flags.DEFINE_integer('epoch_number', 1, 'Number of epochs (for training)')
flags.DEFINE_string('train_dataset', '', 'Training dataset directory') ##containing tfrecords ? look for that
flags.DEFINE_string('train_output', '', 'Training output directory (where tensorflow checkpoints will be stored)')

def OnClassRun(self):
    print "IN"
    inputfile = "/ASD/Martin_Data/ADNI/processing/DTI/AutoTract/3.PostProcess/CorpusCallosum_Genu_bundle_clean_crop_parametrized/CorpusCallosum_Genu_bundle_clean_crop_parametrized_cleanEnds.vtp"
    outputDir = "/ASD/Martin_Data/ADNI/processing/DTI/trafic/output2"
    modelDir="/work/boucaud/test_trafic/checkpoints"
    summaryDir="/ASD/Martin_Data/ADNI/processing/DTI/trafic_summary"
    displacementFieldFile="/ASD/Martin_Data/ADNI/processing/DTI/AutoTract/1.Registration/displacementField.nrrd"
    logic = TraficMultiLogic()
    logic.runClassification(inputfile, outputDir, modelDir, summaryDir, displacementFieldFile)
    print("END OF TESTING")
    return
    if self.CheckInputClass() and self.CheckOutputDirClass() and self.CheckModelDirClass() and self.CheckSumDirClass() and self.CheckdFClassPath():
      print "IN IN IN"
      logic = TraficMultiLogic()
      logic.runClassification(self.inputClass.text, self.modelDirClass.text, self.sumDirClass.text, self.outputDirClass.text, self.dFPathClass.text)
    print "TOO BAD"
    return

def OnTrainTrain(self):
    logic = TraficMultiLogic()
    logic.runStoreAndTrain( self.dataDirTrain.text, self.modelDirTrain.text, self.lr_spinbox.value, self.num_epochs_spinbox.value, self.sumDirTrain.text )
    # if self.CheckDataDirTrain() and self.CheckModelDirTrain() and self.CheckSumDirTrain():
    return



class TraficMultiLogic():
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """


  def runExtractFiber(self, selector, pos, neg):
    """
    Run the extraction algorithm
    TO DO: Add some verification
    """
    selector.createNewBundleFromSelection()
    selector.negativeROISelection(pos) # We switch the state of the ROI Selection
    selector.positiveROISelection(neg) 
    selector.updateBundleFromSelection()
    selector.negativeROISelection(neg) 
    selector.positiveROISelection(pos)

  def runSaveFiber(self, nodeDict, dir):
    """
    Run the save algorithm
    TO DO: Add some verification + Save through the server + Which Location ? + How to identify fibers and dF ?
    """

    logging.info('Saving Fibers')
    for key in nodeDict.keys():
      dirname = os.path.join(dir, key)
      if not os.path.isdir(dirname):
        os.makedirs(dirname)


      for j in xrange(len(nodeDict[key])):
        filename = os.path.join( dirname, key+"_"+str(len(os.listdir(dirname)))+".vtk" )
        node = slicer.mrmlScene.GetNodeByID(nodeDict[key][j])
        print filename
        slicer.util.saveNode(node, filename)
    logging.info('Fibers saved')

  def runPreProcess(self, dF_path, input_dir, output_dir):
    #TO CHANGE: LOCATION OF CLI AND VARIABLES
    #
    currentPath = os.path.dirname(os.path.abspath(__file__))
    cli_dir = os.path.join(currentPath, "..","cli-modules")
    polydatatransform = os.path.join(cli_dir, "polydatatransform")
    lm_ped = "/work/dprince/Multiclass/Landmarks/landmarks_32pts_afprop.fcsv"
    tmp_dir = os.path.join(currentPath, "tmp_dir_lm_preprocess")

    logging.info('Preprocessing started')
    new_lm_path = os.path.join(tmp_dir, "lm_prepocess.fcsv")
    if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)

    logging.info('Polydata transform')
    cmd_polydatatransform = [polydatatransform, "--invertx", "--inverty", "--fiber_file", lm_ped, "-D", dF_path, "-o", new_lm_path]
    out, err = subprocess.Popen(cmd_polydatatransform, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    # print("\nout : " + str(out))
    if err != "":
        print("\nerr : " + str(err))
    logging.info('Make Dataset')
    run_make_dataset(input_dir, output_dir, new_lm_path, landmarksOn=True)
    rmtree(tmp_dir)
    logging.info('Preprocessing completed')

    return

  def runStoreAndTrain(self, data_dir, model_dir, lr, num_epochs, sum_dir):
    runMaybeEnvInstallTF()
    data_dir="/work/dprince/PED/ModelPed"
    model_dir="/work/dprince/Multiclass/Models/dMap"
    sum_dir="/home/boucaud/model"
    currentPath = os.path.dirname(os.path.abspath(__file__))
    env_dir = os.path.join(currentPath, "..", "miniconda2")
    pipeline_train_py = os.path.join(TRAFIC_LIB_DIR, "PipelineTrain.py")
    cmd_py = str(pipeline_train_py) + ' --data_dir ' + str(data_dir) + ' --multiclass --summary_dir ' + str(sum_dir)+ ' --checkpoint_dir ' + str(model_dir) + ' --lr ' + str(lr) + ' --num_epochs ' + str(num_epochs)
    cmd_virtenv = 'ENV_DIR="'+str(env_dir)+'";'
    cmd_virtenv = cmd_virtenv + 'export PYTHONPATH=$ENV_DIR/envs/env_trafic/lib/python2.7/site-packages:$ENV_DIR/lib/:$ENV_DIR/lib/python2.7/lib-dynload/:$ENV_DIR/lib/python2.7/:$ENV_DIR/lib/python2.7/site-packages/:$PYTHONPATH;'
    # cmd_virtenv = cmd_virtenv + 'export PYTHONHOME=$ENV_DIR/bin/:$PYTHONHOME;'
    cmd_virtenv = cmd_virtenv + 'export PATH=$ENV_DIR/bin/:$PATH;'
    cmd_virtenv = cmd_virtenv + 'source activate env_trafic;'
    cmd_virtenv = cmd_virtenv + 'LD_LIBRARY_PATH=$ENV_DIR/envs/env_trafic/lib/libc6_2.17/lib/:$ENV_DIR/envs/env_trafic/lib/libc6_2.17/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH $ENV_DIR/envs/env_trafic/lib/libc6_2.17/lib/x86_64-linux-gnu/ld-2.17.so `which python` '
    cmd_pipeline_train = cmd_virtenv + str(cmd_py) + ';'


    if not os.path.exists("tmp_dir_lm_class"):
        os.makedirs("tmp_dir_lm_class")

    print(cmd_pipeline_train)
    cmd = ["bash", "-c", str(cmd_pipeline_train)]
    log_dir = os.path.join(sum_dir,"Logs")
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    out = open(os.path.join(log_dir,"training_out.txt"), "wb")
    err = open(os.path.join(log_dir,"training_err.txt"), "wb")
    subprocess.Popen(cmd, stdout=out, stderr=err)
    # print("\nout : " + str(out) + "\nerr : " + str(err))
    return

  def runClassification(self, data_file,  model_dir, sum_dir, output_dir, dF_Path):
    runMaybeEnvInstallTF() ### todo : block while the installation is running. no point in executing the rest of the function while installing at the same time
    currentPath = os.path.dirname(os.path.abspath(__file__))
    env_dir = os.path.join(currentPath, "..", "miniconda2")
    cli_dir = os.path.join(currentPath, "..","cli-modules")

    # polydatatransform = os.path.join(cli_dir, "polydatatransform")
    polydatatransform = "/work/boucaud/builds/niral_utilities/bin/polydatatransform"
    lm_ped = os.path.join(currentPath,"Resources", "Landmarks", "landmarks_32pts_afprop.fcsv") ###CHANGED HERE
    tmp_dir = os.path.join(currentPath, "tmp_dir_lm_class")
    if not os.path.isdir(tmp_dir):
      os.makedirs(tmp_dir)
    new_lm_path = os.path.join(tmp_dir, "lm_class.fcsv")

    cmd_polydatatransform = [polydatatransform, "--invertx", "--inverty", "--fiber_file", lm_ped, "-D", dF_Path, "-o", new_lm_path]
    print(cmd_polydatatransform)
    out, err = subprocess.Popen(cmd_polydatatransform, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print("\nout : " + str(out))

    pipeline_eval_py = os.path.join(TRAFIC_LIB_DIR, "PipelineEval.py")
    cmd_py = str(pipeline_eval_py) + ' --data_file ' + str(data_file) + ' --multiclass --summary_dir ' + str(sum_dir)+ ' --checkpoint_dir ' + str(model_dir) + ' --output_dir ' + str(output_dir) + ' --landmark_file ' + str(new_lm_path)
    cmd_virtenv = 'ENV_DIR="'+str(env_dir)+'";'
    cmd_virtenv = cmd_virtenv + 'export PYTHONPATH=$ENV_DIR/envs/env_trafic/lib/python2.7/site-packages:$ENV_DIR/lib/:$ENV_DIR/lib/python2.7/lib-dynload/:$ENV_DIR/lib/python2.7/:$ENV_DIR/lib/python2.7/site-packages/:$PYTHONPATH;'
    cmd_virtenv = cmd_virtenv + 'export PATH=$ENV_DIR/bin/:$PATH;'
    cmd_virtenv = cmd_virtenv + 'source activate env_trafic;'
    cmd_virtenv = cmd_virtenv + 'LD_LIBRARY_PATH=$ENV_DIR/envs/env_trafic/lib/libc6_2.17/lib/:$ENV_DIR/envs/env_trafic/lib/libc6_2.17/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH $ENV_DIR/envs/env_trafic/lib/libc6_2.17/lib/x86_64-linux-gnu/ld-2.17.so `which python` '
    cmd_pipeline_class = cmd_virtenv + str(cmd_py) + ';'
    print(str(cmd_pipeline_class))
    cmd = ["bash", "-c", str(cmd_pipeline_class)]
    log_dir = os.path.join(sum_dir,"Logs")
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    out = open(os.path.join(log_dir,"training_out.txt"), "wb")
    err = open(os.path.join(log_dir,"training_err.txt"), "wb")
    _, _ = subprocess.Popen(cmd, stdout=out, stderr=err).communicate()
    # print("\nout : " + str(out) + "\nerr : " + str(err))
    rmtree(tmp_dir)

    # print("\nout : " + str(out) + "\nerr : " + str(err))
    return

    # logging.info('Processing completed')

    # return True


def main():
    print FLAGS.multiclassification
    print FLAGS.class_input_fiber
    print FLAGS.class_output
    print FLAGS.class_summary
    print FLAGS.class_displacement
    print FLAGS.checkpoints
    logic = TraficMultiLogic()
    if(FLAGS.multiclassification):
        logic.runClassification(FLAGS.class_input_fiber, FLAGS.checkpoints, FLAGS.class_summary, FLAGS.class_output, FLAGS.class_displacement)
    else if(FLAGS.train):
        print 'should run training here'
    return

if __name__ == '__main__':
    main()
