import os
from os import path, sys
from shutil import rmtree
import subprocess
import numpy as np
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

TRAFIC_LIB_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), "TraficLib")
sys.path.append(TRAFIC_LIB_DIR)
print path.join(TRAFIC_LIB_DIR)
from makeDataset import run_make_dataset
from envInstallTF import runMaybeEnvInstallTF
# print runPreprocess
import logging


#
# TraficMulti
#

class TraficMulti(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "TraficMulti" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Classification"]
    self.parent.dependencies = []
    self.parent.contributors = ["Prince Ngattai Lam (UNC-NIRAL)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    """
    self.parent.acknowledgementText = """
""" # replace with organization, grant and thanks.

#
# TraficMultiWidget
#

class TraficMultiWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setupEditionTab(self):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                UI FILES LOADING                                   #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    loader = qt.QUiLoader()
    self.EditionTabName = 'TraficMultiEditionTab'
    scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
    scriptedModulesPath = os.path.dirname(scriptedModulesPath)
    path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.EditionTabName)
    qfile = qt.QFile(path)
    qfile.open(qt.QFile.ReadOnly)
    widget = loader.load(qfile, self.editionTabWidget)

    self.editionLayout = qt.QVBoxLayout(self.editionTabWidget)
    self.editionWidget = widget


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                 FIBER DISPLAY AREA                                #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    displayFibersCollapsibleButton = ctk.ctkCollapsibleButton()
    displayFibersCollapsibleButton.text = "Fiber Bundle"
    self.editionLayout.addWidget(displayFibersCollapsibleButton)

    # Layout within the dummy collapsible button
    displayFibersFormLayout = qt.QFormLayout(displayFibersCollapsibleButton)

    #
    # Fibers Tree View
    #
    # self.inputFiber = slicer.qMRMLTractographyDisplayTreeView()
    self.inputFiber = slicer.qMRMLNodeComboBox()
    self.inputFiber.nodeTypes = ["vtkMRMLFiberBundleNode"]
    self.inputFiber.addEnabled = False
    self.inputFiber.removeEnabled = True
    self.inputFiber.noneEnabled = True
    self.inputFiber.showHidden = True
    self.inputFiber.showChildNodeTypes = False
    self.inputFiber.setMRMLScene(slicer.mrmlScene)
    displayFibersFormLayout.addRow("Input Fiber", self.inputFiber)

    # self.progress = qt.QProgressDialog()
    # self.progress.setValue(0)
    # self.progress.show()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                 FIBER SELECTION AREA                              #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    selectionFibersCollapsibleButton = ctk.ctkCollapsibleButton()
    selectionFibersCollapsibleButton.text = "Fiber Selection"
    self.editionLayout.addWidget(selectionFibersCollapsibleButton)

    # Layout within the dummy collapsible button
    selectionFibersFormLayout = qt.QFormLayout(selectionFibersCollapsibleButton)

    self.selectionFiber = self.getWidget('qSlicerTractographyEditorROIWidget', index_tab=0)
    self.ROISelectorDisplay = self.getWidget('ROIForFiberSelectionMRMLNodeSelector', index_tab=0)
    self.ROISelectorDisplay.setMRMLScene(slicer.mrmlScene)
    self.fiberList = self.getWidget('fiberList', index_tab=0)
    name_labels = ['Select a type of fiber','0','Arc_L_FT','Arc_L_FrontoParietal','Arc_L_TemporoParietal','Arc_R_FT','Arc_R_FrontoParietal','Arc_R_TemporoParietal','CGC_L','CGC_R','CGH_L','CGH_R','CorpusCallosum_Genu',
               'CorpusCallosum_Motor','CorpusCallosum_Parietal','CorpusCallosum_PreMotor','CorpusCallosum_Rostrum','CorpusCallosum_Splenium','CorpusCallosum_Tapetum','CorticoFugal-Left_Motor',
               'CorticoFugal-Left_Parietal','CorticoFugal-Left_PreFrontal','CorticoFugal-Left_PreMotor','CorticoFugal-Right_Motor','CorticoFugal-Right_Parietal','CorticoFugal-Right_PreFrontal',
               'CorticoFugal-Right_PreMotor','CorticoRecticular-Left','CorticoRecticular-Right','CorticoSpinal-Left','CorticoSpinal-Right','CorticoThalamic_L_PreFrontal','CorticoThalamic_L_SUPERIOR',
               'CorticoThalamic_Left_Motor','CorticoThalamic_Left_Parietal','CorticoThalamic_Left_PreMotor','CorticoThalamic_R_PreFrontal','CorticoThalamic_R_SUPERIOR',
               'CorticoThalamic_Right_Motor','CorticoThalamic_Right_Parietal','CorticoThalamic_Right_PreMotor','Fornix_L','Fornix_R','IFOF_L','IFOF_R','ILF_L','ILF_R',
               'OpticRadiation_Left','OpticRadiation_Right','Optic_Tract_L','Optic_Tract_R','SLF_II_L','SLF_II_R','UNC_L','UNC_R']
    self.fiberList.addItems(name_labels)
    self.fiberList.setMaxVisibleItems(5)
    # selectionFibersFormLayout.addRow(self.selectionFiber)
    selectionFibersFormLayout.addRow(self.selectionFiber)

    self.disROI = self.getWidget('DisableROI', index_tab=0)
    self.posROI = self.getWidget('PositiveROI', index_tab=0)
    self.negROI = self.getWidget('NegativeROI', index_tab=0)
    self.interROI = self.getWidget('InteractiveROI', index_tab=0)
    self.showROI = self.getWidget('ROIVisibility', index_tab=0)

    # self.accEditOn = self.getWidget('EnableAccurateEdit')
    self.extractFiber = self.getWidget('CreateNewFiberBundle', index_tab=0)

    self.ROISelector = slicer.qSlicerTractographyEditorROIWidget()
    self.ROISelector.setFiberBundleNode(self.inputFiber.currentNode())
    self.ROISelector.setMRMLScene(slicer.mrmlScene)
    self.ROISelector.setAnnotationMRMLNodeForFiberSelection(self.ROISelectorDisplay.currentNode())
    self.ROISelector.setAnnotationROIMRMLNodeToFiberBundleEnvelope(self.ROISelectorDisplay.currentNode())


    # self.editionLayout.addWidget(self.ROISelector)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                 FIBER REVIEW AREA                                 #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    reviewsCollapsibleButton = ctk.ctkCollapsibleButton()
    reviewsCollapsibleButton.text = "Reviews"
    self.editionLayout.addWidget(reviewsCollapsibleButton)

    self.reviewsFormLayout = qt.QFormLayout(reviewsCollapsibleButton)
    self.reviewsList = slicer.qMRMLTractographyDisplayTreeView()
    self.reviewsList.setMRMLScene(slicer.mrmlScene)
    self.reviewsFormLayout.addRow(self.reviewsList)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                 CLEAR AND SAVE AREA                               #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    self.dFPath = qt.QLineEdit("")
    self.outputDirEdit = qt.QLineEdit("")
    # self.dFPath.setEnabled(False)

    self.dFSelector = qt.QPushButton("Browse")
    self.outputDirEditSelector = qt.QPushButton("Browse")
    self.clearButton = qt.QPushButton("CLEAR")
    self.clearButton.toolTip = "Clear everything."
    self.clearButton.enabled = True
    self.saveButton = qt.QPushButton("SAVE")
    self.saveButton.toolTip = "Save and update Trafic database."
    self.saveButton.enabled = True

        # self.editionLayout.addWidget(self.ROISelector)
    gridLayoutdF = qt.QGridLayout()
    gridLayoutClearSave = qt.QGridLayout()

    gridLayoutdF.addWidget(qt.QLabel("Displacement field"), 0, 0)
    gridLayoutdF.addWidget(self.dFPath, 0, 1)
    gridLayoutdF.addWidget(self.dFSelector, 0, 2)
    gridLayoutdF.addWidget(qt.QLabel("Output Directory"), 1, 0)
    gridLayoutdF.addWidget(self.outputDirEdit, 1, 1)
    gridLayoutdF.addWidget(self.outputDirEditSelector, 1, 2)

    gridLayoutClearSave.addWidget(self.clearButton, 0, 0)
    gridLayoutClearSave.addWidget(self.saveButton, 0, 2)
    self.editionLayout.addLayout(gridLayoutdF)
    self.editionLayout.addLayout(gridLayoutClearSave)



    self.nodeDict = {}

    # Initialization of the dictionnary that will contains the Node ID and their type
    for i in xrange(1, len(name_labels)):
      self.nodeDict[name_labels[i]] = []


    self.editionLayout.addStretch(1)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                 CONNECTIONS                                       #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    self.inputFiber.connect("currentNodeChanged(vtkMRMLNode*)", self.onChangeCurrentNode)
    self.disROI.connect("toggled(bool)", self.onDisROI)
    self.posROI.connect("toggled(bool)", self.onPosROI)
    self.negROI.connect("toggled(bool)", self.onNegROI)
    self.interROI.connect("toggled(bool)", self.onInterROI)
    self.showROI.connect("toggled(bool)", self.onShowROI)
    # self.accEditOn.connect("toggled(bool)", self.onAccEditOn)

    self.ROISelectorDisplay.connect("currentNodeChanged(vtkMRMLNode*)", self.onChangeCurrentNode)
    self.ROISelectorDisplay.connect("nodeAddedByUser(vtkMRMLNode*)", self.onAddNode)
    self.saveButton.connect("clicked(bool)", self.onSaveButton)
    self.clearButton.connect("clicked(bool)", self.onClearButton)

    self.extractFiber.connect("clicked(bool)", self.OnExtractFiber)
    self.dFSelector.connect("clicked(bool)", self.OndFSelector)
    self.dFPath.connect("editingFinished()", self.checkdFPath)
    self.outputDirEditSelector.connect("clicked(bool)", self.OnOutputDirEditSelector)
    self.outputDirEdit.connect("editingFinished()", self.CheckOutputDirEdit)

    return

  def setupTrainingTab(self):
    self.trainingLayout = qt.QVBoxLayout(self.trainingTabWidget)
    gridLayoutTrain = qt.QGridLayout()
    self.lr_spinbox = qt.QDoubleSpinBox()
    self.lr_spinbox.setSingleStep(0.001)
    self.lr_spinbox.setValue(0.01)
    self.lr_spinbox.setDecimals(3)

    self.num_epochs_spinbox = qt.QSpinBox()
    self.num_epochs_spinbox.setSingleStep(1)
    self.num_epochs_spinbox.setValue(1)

    gridLayoutTrain.addWidget(qt.QLabel("Learning Rate"), 0, 0)
    gridLayoutTrain.addWidget(self.lr_spinbox, 0, 1)
    gridLayoutTrain.addWidget(qt.QLabel("Number of Epochs"), 1, 0)
    gridLayoutTrain.addWidget(self.num_epochs_spinbox, 1, 1)

    gridLayoutSumdir = qt.QGridLayout()
    self.sumDirTrainSelector = qt.QPushButton("Browse")
    self.sumDirTrain = qt.QLineEdit("")

    self.modelDirTrainSelector = qt.QPushButton("Browse")
    self.modelDirTrain = qt.QLineEdit("")

    self.dataDirTrainSelector = qt.QPushButton("Browse")
    self.dataDirTrain = qt.QLineEdit("")



    gridLayoutSumdir.addWidget(qt.QLabel("Data Directory"), 1, 0)
    gridLayoutSumdir.addWidget(self.dataDirTrain, 1, 1)
    gridLayoutSumdir.addWidget(self.dataDirTrainSelector, 1, 2)

    gridLayoutSumdir.addWidget(qt.QLabel("Model Directory"), 2, 0)
    gridLayoutSumdir.addWidget(self.modelDirTrain, 2, 1)
    gridLayoutSumdir.addWidget(self.modelDirTrainSelector, 2, 2)

    gridLayoutSumdir.addWidget(qt.QLabel("Summary Directory"), 3, 0)
    gridLayoutSumdir.addWidget(self.sumDirTrain, 3, 1)
    gridLayoutSumdir.addWidget(self.sumDirTrainSelector, 3, 2)

    gridResTrain = qt.QGridLayout()
    self.trainReset = qt.QPushButton("RESET")
    self.trainTrain = qt.QPushButton("TRAIN")
    gridResTrain.addWidget(self.trainReset, 0, 0)
    gridResTrain.addWidget(self.trainTrain, 0, 1)

    self.trainingLayout.addLayout(gridLayoutTrain)
    self.trainingLayout.addLayout(gridLayoutSumdir)

    self.trainingLayout.addLayout(gridResTrain)
    self.trainingLayout.addStretch(1)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                 CONNECTIONS                                       #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    self.trainReset.connect("clicked(bool)", self.OnTrainReset)
    self.trainTrain.connect("clicked(bool)", self.OnTrainTrain)
    self.dataDirTrainSelector.connect("clicked(bool)", self.OnDataDirTrain)
    self.modelDirTrainSelector.connect("clicked(bool)", self.OnModelDirTrain)
    self.sumDirTrainSelector.connect("clicked(bool)", self.OnSumDirTrain)
    self.dataDirTrain.connect("editingFinished()", self.CheckDataDirTrain)
    self.modelDirTrain.connect("editingFinished()", self.CheckModelDirTrain)
    self.sumDirTrain.connect("editingFinished()", self.CheckSumDirTrain)


    # self.trainingWidget = widget

    return

  def setupClassificationTab(self):
    self.classificationLayout = qt.QVBoxLayout(self.classificationTabWidget)
    gridLayoutClass = qt.QGridLayout()
    ### Input File
    self.inputClass = qt.QLineEdit("")
    self.inputClassSelector = qt.QPushButton("Browse")

    ### Output Directory
    self.outputDirClass = qt.QLineEdit("")
    self.outputDirClassSelector = qt.QPushButton("Browse")


    ### Model Directory
    self.modelDirClass = qt.QLineEdit("")
    self.modelDirClassSelector = qt.QPushButton("Browse")


    ### Summary Directory
    self.sumDirClass = qt.QLineEdit("")
    self.sumDirClassSelector = qt.QPushButton("Browse")

    ### Displacement Field
    self.dFPathClass = qt.QLineEdit("")
    self.dFPathClassSelector = qt.QPushButton("Browse")


    gridLayoutClass.addWidget(qt.QLabel("Input File"), 0, 0)
    gridLayoutClass.addWidget(self.inputClass, 0, 1)
    gridLayoutClass.addWidget(self.inputClassSelector, 0, 2)
    gridLayoutClass.addWidget(qt.QLabel("Output Directory"), 1, 0)
    gridLayoutClass.addWidget(self.outputDirClass, 1, 1)
    gridLayoutClass.addWidget(self.outputDirClassSelector, 1, 2)
    gridLayoutClass.addWidget(qt.QLabel("Model Directory"), 2, 0)
    gridLayoutClass.addWidget(self.modelDirClass, 2, 1)
    gridLayoutClass.addWidget(self.modelDirClassSelector, 2, 2)
    gridLayoutClass.addWidget(qt.QLabel("Summary Directory"), 3, 0)
    gridLayoutClass.addWidget(self.sumDirClass, 3, 1)
    gridLayoutClass.addWidget(self.sumDirClassSelector, 3, 2)
    gridLayoutClass.addWidget(qt.QLabel("Displacement Field"), 4, 0)
    gridLayoutClass.addWidget(self.dFPathClass, 4, 1)
    gridLayoutClass.addWidget(self.dFPathClassSelector, 4, 2)

    gridResClass = qt.QGridLayout()
    self.classReset = qt.QPushButton("RESET")
    self.classRun = qt.QPushButton("RUN")
    gridResClass.addWidget(self.classReset, 0, 0)
    gridResClass.addWidget(self.classRun, 0, 1)

    self.classificationLayout.addLayout(gridLayoutClass)
    self.classificationLayout.addLayout(gridResClass)
    self.classificationLayout.addStretch(1)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                 CONNECTIONS                                       #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    self.classReset.connect("clicked(bool)", self.OnClassReset)
    self.classRun.connect("clicked(bool)", self.OnClassRun)

    self.inputClassSelector.connect("clicked(bool)", self.OnInputClass)
    self.outputDirClassSelector.connect("clicked(bool)", self.OnOutputDirClass)
    self.modelDirClassSelector.connect("clicked(bool)", self.OnModelDirClass)
    self.sumDirClassSelector.connect("clicked(bool)", self.OnSumDirClass)
    self.dFPathClassSelector.connect("clicked(bool)", self.OndFClassSelector)

    self.inputClass.connect("editingFinished()", self.CheckInputClass)
    self.outputDirClass.connect("editingFinished()", self.CheckOutputDirClass)
    self.modelDirClass.connect("editingFinished()", self.CheckModelDirClass)
    self.sumDirClass.connect("editingFinished()", self.CheckSumDirClass)
    self.dFPathClass.connect("editingFinished()", self.CheckdFClassPath)

    # self.classificationWidget = widget
    return

  def setup(self):


    ScriptedLoadableModuleWidget.setup(self)

    os.environ['ITK_AUTOLOAD_PATH']= ''
    self.moduleName = 'TraficMulti'
    self.editionTabWidget = qt.QWidget()
    self.trainingTabWidget = qt.QWidget()
    self.classificationTabWidget = qt.QWidget()
    self.tabs = qt.QTabWidget()
    self.tabs.addTab(self.editionTabWidget,"Edition")
    self.tabs.addTab(self.trainingTabWidget,"Training")
    self.tabs.addTab(self.classificationTabWidget,"Classification")
    self.layout = self.parent.layout()
    self.layout.addWidget(self.tabs)
    self.setupEditionTab()
    self.setupClassificationTab()
    self.setupTrainingTab()

  def getWidget(self, objectName, index_tab=0):
    if index_tab == 0:
      return self.findWidget(self.editionWidget, objectName)
    if index_tab == 1:
      return self.findWidget(self.trainingWidget, objectName)
    if index_tab == 2:
      return self.findWidget(self.classificationWidget, objectName)

  def findWidget(self, widget, objectName):
    if widget.objectName == objectName:
      return widget
    else:
      for w in widget.children():
        resulting_widget = self.findWidget(w, objectName)
        if resulting_widget:
          return resulting_widget
    return None

  def onDisROI(self):
    if self.disROI.isChecked():
      self.ROISelector.disableROISelection(True)


  def onPosROI(self):
    if self.posROI.isChecked():
      self.ROISelector.positiveROISelection(True)


  def onNegROI(self):
    if self.negROI.isChecked():
      self.ROISelector.negativeROISelection(True)

  def onInterROI(self):
    if self.interROI.isChecked():
      self.ROISelector.setInteractiveROI(True)


  def onShowROI(self):
      self.ROISelectorDisplay.currentNode().SetDisplayVisibility(self.showROI.isChecked())

  def OnOutputDirEditSelector(self):
    self.OnBrowseDirectory(self.outputDirEdit)

  def CheckOutputDirEdit(self):
    return self.CheckBrowseDirectory(self.outputDirEdit, "Edition Output Directory")

  def OndFSelector(self):
    fileDialog = qt.QFileDialog()
    fileDialog.setFileMode(qt.QFileDialog.ExistingFile)
    fileDialog.setNameFilter("displacement field (*.nrrd)")
    if fileDialog.exec_():
      text = fileDialog.selectedFiles()
      self.dFPath.setText(text[0])

  def OndFClassSelector(self):
    fileDialog = qt.QFileDialog()
    fileDialog.setFileMode(qt.QFileDialog.ExistingFile)
    fileDialog.setNameFilter("displacement field (*.nrrd)")
    if fileDialog.exec_():
      text = fileDialog.selectedFiles()
      self.dFPathClass.setText(text[0])

  def CheckdFClassPath(self):
    if self.dFPathClass.text == "":
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("Please choose a displacement field filename")
      msg.exec_()
    elif not os.path.isfile(self.dFPathClass.text):
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("File doesn't exist. Please correct the displacement field filename")
      msg.exec_()
      return False
    elif self.dFPathClass.text.rfind(".nrrd") == -1:
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("Invalid File Format. Must be a .nrrd file. Please correct the displacement field filename")
      msg.exec_()
      return False

    return True

  def checkdFPath(self):
    if self.dFPath.text == "":
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("Please choose a displacement field filename")
      msg.exec_()
    elif not os.path.isfile(self.dFPath.text):
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("File doesn't exist. Please correct the displacement field filename")
      msg.exec_()
      return False
    elif self.dFPath.text.rfind(".nrrd") == -1:
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("Invalid File Format. Must be a .nrrd file. Please correct the displacement field filename")
      msg.exec_()
      return False
    return True

  def OnInputClass(self):
    fileDialog = qt.QFileDialog()
    fileDialog.setFileMode(qt.QFileDialog.ExistingFile)
    fileDialog.setNameFilter("input file (*.vtk *.vtp)")
    if fileDialog.exec_():
      text = fileDialog.selectedFiles()
      self.inputClass.setText(text[0])

  def CheckInputClass(self):
    if not os.path.isfile(self.inputClass.text):
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("File doesn't exist. Please correct the input file")
      msg.exec_()
      return False
    elif self.inputClass.text.rfind(".vtk") == -1 and self.inputClass.text.rfind(".vtp") == -1:
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("Invalid File Format. Must be a .vtk or .vtp file. Please correct the input file")
      msg.exec_()
      return False
    return True


  def OnDataDirTrain(self):
    self.OnBrowseDirectory(self.dataDirTrain)

  def OnModelDirTrain(self):
    self.OnBrowseDirectory(self.modelDirTrain)

  def OnSumDirTrain(self):
    self.OnBrowseDirectory(self.sumDirTrain)

  def CheckDataDirTrain(self):
    return self.CheckBrowseDirectory(self.dataDirTrain, "Data Directory")

  def CheckModelDirTrain(self):
    return self.CheckBrowseDirectory(self.modelDirTrain, "Model Directory")

  def CheckSumDirTrain(self):
    return self.CheckBrowseDirectory(self.sumDirTrain, "Summary Directory")

  def OnOutputDirClass(self):
    self.OnBrowseDirectory(self.outputDirClass)

  def OnModelDirClass(self):
    self.OnBrowseDirectory(self.modelDirClass)

  def OnSumDirClass(self):
    self.OnBrowseDirectory(self.sumDirClass)

  def CheckOutputDirClass(self):
    return self.CheckBrowseDirectory(self.outputDirClass, "Classification Output Directory")

  def CheckModelDirClass(self):
    return self.CheckBrowseDirectory(self.modelDirClass, "Model Directory")

  def CheckSumDirClass(self):
    return self.CheckBrowseDirectory(self.sumDirClass, "Summary Directory")

  def OnBrowseDirectory(self, dir):
    fileDialog = qt.QFileDialog()
    fileDialog.setFileMode(qt.QFileDialog.DirectoryOnly)
    if fileDialog.exec_():
      text = fileDialog.selectedFiles()
      dir.setText(text[0])

  def CheckBrowseDirectory(self, dir, name):
    if dir.text=="":
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("Please choose "+ str(name) + "")
      msg.exec_()
      return False
    elif not os.path.isdir(dir.text):
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("Unknown or non valid directory. Please correct the "+ str(name))
      msg.exec_()
      return False
    return True

  # def onAccEditOn(self):
  # #   if self.accEditOn.isChecked():
  # #     # print 
  # #     # if(self.ROISelector.fiberBundleNode()):
  # #     self.ROISelector.setInteractiveFiberEdit(True)
  # #     else:
  #   print "FAIL"

  def onChangeCurrentNode(self):
    self.posROI.setChecked(True)
    self.ROISelector.setFiberBundleNode(self.inputFiber.currentNode())
    self.ROISelector.setAnnotationROIMRMLNodeToFiberBundleEnvelope(self.ROISelectorDisplay.currentNode())



  def onAddNode(self):
    self.posROI.setChecked(True)
    self.ROISelector.setAnnotationMRMLNodeForFiberSelection(self.ROISelectorDisplay.currentNode())
    self.ROISelector.setAnnotationROIMRMLNodeToFiberBundleEnvelope(self.ROISelectorDisplay.currentNode())

  def onSaveButton(self):

    #TO DO: Save all Data and Clear after + Add a message box to confirm the save + Message to choose the dF
    if self.checkdFPath() and self.CheckOutputDirEdit():
      currentPath = os.path.dirname(os.path.abspath(__file__))
      tmp_dir = os.path.join(self.outputDirEdit.text, 'tmp_dir_save')
      final_dir = os.path.join(self.outputDirEdit.text, 'Multiclass')
      logic = TraficMultiLogic()
      logic.runSaveFiber(self.nodeDict, tmp_dir)
      self.removeNodeExtracted()
      # Initialization of the dictionnary
      for key in self.nodeDict.keys():
        self.nodeDict[key] = []

      logic.runPreProcess(self.dFPath.displayText, tmp_dir, final_dir)
      rmtree(tmp_dir)
        # logic.runStore()

  def OnTrainReset(self):
    self.num_epochs_spinbox.setValue(1)
    self.lr_spinbox.setValue(0.01)
    self.sumDirTrain.text = "/tmp"
    self.modelDirTrain.text = ""
    self.dataDirTrain.text = ""

  def OnClassReset(self):
    self.sumDirClass.text = "/tmp"
    self.modelDirClass.text = ""
    self.outputDirClass.text = ""
    self.inputClass.text = ""

  def OnClassRun(self):
    print "IN"
    if self.CheckInputClass() and self.CheckOutputDirClass() and self.CheckModelDirClass() and self.CheckSumDirClass() and self.CheckdFClassPath():
      print "IN IN IN"
      logic = TraficMultiLogic()
      logic.runClassification(self.inputClass.text, self.modelDirClass.text, self.sumDirClass.text, self.outputDirClass.text, self.dFPathClass.text)
    print "TOO BAD"
    return

  def OnTrainTrain(self):
    if self.CheckDataDirTrain() and self.CheckModelDirTrain() and self.CheckSumDirTrain():
        logic = TraficMultiLogic()
        logic.runStoreAndTrain( self.dataDirTrain.text, self.modelDirTrain.text, self.lr_spinbox.value, self.num_epochs_spinbox.value, self.sumDirTrain.text )
    return
  def onClearButton(self):

    while(self.inputFiber.currentNode() != None):
      print "None"
      self.inputFiber.removeCurrentNode()
    self.removeNodeExtracted()
    slicer.mrmlScene.Clear(0)
    #TO DO: Clear all Data
    return

  def removeNodeExtracted(self):
    nodeIDs = np.array(self.nodeDict.values())
    nodeIDs = [val for sublist in nodeIDs for val in sublist] #Flatten the list
    # print nodeIDs
    for nodeID in nodeIDs:
      slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetNodeByID(nodeID))
      print "Remove ", nodeID


  def OnExtractFiber(self):
    if self.fiberList.itemText(self.fiberList.currentIndex) == "Select a type of fiber":
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("You must choose which type of fiber you want to extract from the current fiber")
      msg.exec_()
    elif self.disROI.isChecked():
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("ROI is disable, please choose Positive or Negative region to extract")
      msg.exec_()
    else:
      nameNode = self.fiberList.itemText(self.fiberList.currentIndex)
      # Process To modify the name
      
      # If not already exist 
      # self.reviewsFormLayout.addRow(reviewNode)
      # self.ROISelector.setAnnotationMRMLNodeForFiberSelection(newNode)

      # print self.ROISelector.fiberBundleNode()
      
      self.ROISelector.FiberBundleFromSelection.addNode()
      nodeID = self.ROISelector.FiberBundleFromSelection.currentNode().GetID()
      self.nodeDict[nameNode].append(nodeID)
      numExtract = len(self.nodeDict[nameNode])
      self.ROISelector.FiberBundleFromSelection.currentNode().SetName(nameNode+"_extracted_"+str(numExtract))
      
      logic = TraficMultiLogic()
      logic.runExtractFiber(self.ROISelector, self.posROI.isChecked(), self.negROI.isChecked())

    return
#
# TraficMultiLogic
#

class TraficMultiLogic(ScriptedLoadableModuleLogic):
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
    cli_dir = os.path.join(currentPath, "..", "..","cli-modules")
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
    print(cmd_pipeline_train)
    cmd = ["bash", "-c", str(cmd_pipeline_train)]
    out = open(os.path.join(TRAFIC_LIB_DIR,"Logs","training_out.txt"), "wb")
    err = open(os.path.join(TRAFIC_LIB_DIR,"Logs","training_err.txt"), "wb")
    subprocess.Popen(cmd, stdout=out, stderr=err)
    # print("\nout : " + str(out) + "\nerr : " + str(err))
    return

  def runClassification(self, data_file,  model_dir, sum_dir, output_dir, dF_Path):
    runMaybeEnvInstallTF()
    currentPath = os.path.dirname(os.path.abspath(__file__))
    env_dir = os.path.join(currentPath, "..", "..", "miniconda2")
    cli_dir = os.path.join(currentPath, "..", "..","cli-modules")
    polydatatransform = os.path.join(cli_dir, "polydatatransform")
    lm_ped = "/work/dprince/Multiclass/Landmarks/landmarks_32pts_afprop.fcsv"
    tmp_dir = os.path.join(currentPath, "tmp_dir_lm_class")
    if not os.path.isdir(tmp_dir):
      os.makedirs(tmp_dir)
    new_lm_path = os.path.join(tmp_dir, "lm_class.fcsv")

    cmd_polydatatransform = [polydatatransform, "--invertx", "--inverty", "--fiber_file", lm_ped, "-D", dF_Path, "-o", new_lm_path]
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
    print(cmd_pipeline_class)
    cmd = ["bash", "-c", str(cmd_pipeline_class)]
    out = open(os.path.join(TRAFIC_LIB_DIR,"Logs","classification_out.txt"), "wb")
    err = open(os.path.join(TRAFIC_LIB_DIR,"Logs","classification_err.txt"), "wb")
    _, _ = subprocess.Popen(cmd, stdout=out, stderr=err).communicate()
    # print("\nout : " + str(out) + "\nerr : " + str(err))
    rmtree(tmp_dir)

    # print("\nout : " + str(out) + "\nerr : " + str(err))
    return

    # logging.info('Processing completed')

    # return True

    


class TraficMultiTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_TraficMulti1()

  def test_TraficMulti1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = TraficMultiLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
