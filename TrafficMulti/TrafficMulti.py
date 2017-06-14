import os
from os import path, sys
from shutil import rmtree
import subprocess
import numpy as np
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

TRAFFIC_LIB_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), "TrafficLib")
sys.path.append(TRAFFIC_LIB_DIR)
print path.join(TRAFFIC_LIB_DIR)
from makeDataset import run_make_dataset
# print runPreprocess
import logging

TMP_DIR = "/work/dprince/DirectoryTest/"
TRAIN_DIR = "/work/dprince/DirectoryTrain/"


#
# TrafficMulti
#

class TrafficMulti(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "TrafficMulti" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# TrafficMultiWidget
#

class TrafficMultiWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setupEditionTab(self):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                UI FILES LOADING                                   #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    loader = qt.QUiLoader()
    self.EditionTabName = 'TrafficMultiEditionTab'
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
    
    self.dFPath = qt.QLineEdit("Select displacement field for the fiber")
    # self.dFPath.setEnabled(False)

    self.atalsSelector = qt.QPushButton("Browse")
    self.clearButton = qt.QPushButton("CLEAR")
    self.clearButton.toolTip = "Clear everything."
    self.clearButton.enabled = True
    self.saveButton = qt.QPushButton("SAVE")
    self.saveButton.toolTip = "Save and update Traffic database."
    self.saveButton.enabled = True

        # self.editionLayout.addWidget(self.ROISelector)
    gridLayoutdF = qt.QGridLayout()
    gridLayoutClearSave = qt.QGridLayout()

    gridLayoutdF.addWidget(qt.QLabel("Displacement field"), 0, 0)
    gridLayoutdF.addWidget(self.dFPath, 0, 1)
    gridLayoutdF.addWidget(self.atalsSelector, 0, 2)
    gridLayoutClearSave.addWidget(self.clearButton, 0, 0)
    gridLayoutClearSave.addWidget(self.saveButton, 0, 2)
    self.editionLayout.addLayout(gridLayoutdF)
    self.editionLayout.addLayout(gridLayoutClearSave)

    self.nodeDict = {}

    # Initialization of the dictionnary that will contains the Node ID and their type
    for i in xrange(1, len(name_labels)):
      self.nodeDict[name_labels[i]] = []


    self.layout.addStretch(1)

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
    self.atalsSelector.connect("clicked(bool)", self.OndFSelector)
    self.dFPath.connect("editingFinished()", self.checkdFPath)
    return

  def setupTrainingTab(self):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                UI FILES LOADING                                   #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    loader = qt.QUiLoader()
    self.TrainingTabName = 'TrafficMultiTrainingTab'
    scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
    scriptedModulesPath = os.path.dirname(scriptedModulesPath)
    path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.TrainingTabName)
    qfile = qt.QFile(path)
    qfile.open(qt.QFile.ReadOnly)
    widget = loader.load(qfile, self.trainingTabWidget)
    self.trainingLayout = qt.QVBoxLayout(self.trainingTabWidget)
    self.trainingWidget = widget
    return

  def setupClassificationTab(self):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                UI FILES LOADING                                   #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    loader = qt.QUiLoader()
    self.ClassificationTabName = 'TrafficMultiClassificationTab'
    scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
    scriptedModulesPath = os.path.dirname(scriptedModulesPath)
    path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.ClassificationTabName)
    qfile = qt.QFile(path)
    qfile.open(qt.QFile.ReadOnly)
    widget = loader.load(qfile, self.classificationTabWidget)
    self.classificationLayout = qt.QVBoxLayout(self.classificationTabWidget)
    self.classificationWidget = widget
    return

  def setup(self):


    ScriptedLoadableModuleWidget.setup(self)

    os.environ['ITK_AUTOLOAD_PATH']= ''
    self.moduleName = 'TrafficMulti'
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
    out, err = subprocess.Popen(["/tools/Slicer4/Slicer-4.7.0-2017-05-19-linux-amd64/bin/python-real","/work/dprince/TRAFFIC/Traffic/TrafficLib/envTensorFlow.py"] , stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print err
    print out
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # #                                UI FILES LOADING                                   #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # loader = qt.QUiLoader()
    # self.moduleName = 'TrafficMulti'
    # scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
    # scriptedModulesPath = os.path.dirname(scriptedModulesPath)
    # path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.moduleName)
    # qfile = qt.QFile(path)
    # qfile.open(qt.QFile.ReadOnly)
    # widget = loader.load(qfile, self.parent)
    # self.layout = self.parent.layout()
    # self.widget = widget


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # #                                 FIBER DISPLAY AREA                                #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # displayFibersCollapsibleButton = ctk.ctkCollapsibleButton()
    # displayFibersCollapsibleButton.text = "Fiber Bundle"
    # self.layout.addWidget(displayFibersCollapsibleButton)

    # # Layout within the dummy collapsible button
    # displayFibersFormLayout = qt.QFormLayout(displayFibersCollapsibleButton)

    # #
    # # Fibers Tree View
    # #
    # # self.inputFiber = slicer.qMRMLTractographyDisplayTreeView()
    # self.inputFiber = slicer.qMRMLNodeComboBox()
    # self.inputFiber.nodeTypes = ["vtkMRMLFiberBundleNode"]
    # self.inputFiber.addEnabled = False
    # self.inputFiber.removeEnabled = True
    # self.inputFiber.noneEnabled = True
    # self.inputFiber.showHidden = True
    # self.inputFiber.showChildNodeTypes = False
    # self.inputFiber.setMRMLScene(slicer.mrmlScene)
    # displayFibersFormLayout.addRow("Input Fiber", self.inputFiber)

    # # self.progress = qt.QProgressDialog()
    # # self.progress.setValue(0)
    # # self.progress.show()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # #                                 FIBER SELECTION AREA                              #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # selectionFibersCollapsibleButton = ctk.ctkCollapsibleButton()
    # selectionFibersCollapsibleButton.text = "Fiber Selection"
    # self.layout.addWidget(selectionFibersCollapsibleButton)

    # # Layout within the dummy collapsible button
    # selectionFibersFormLayout = qt.QFormLayout(selectionFibersCollapsibleButton)

    # self.selectionFiber = self.getWidget('qSlicerTractographyEditorROIWidget')
    # self.ROISelectorDisplay = self.getWidget('ROIForFiberSelectionMRMLNodeSelector')
    # self.ROISelectorDisplay.setMRMLScene(slicer.mrmlScene)
    # self.fiberList = self.getWidget('fiberList')
    # name_labels = ['Select a type of fiber','0','Arc_L_FT','Arc_L_FrontoParietal','Arc_L_TemporoParietal','Arc_R_FT','Arc_R_FrontoParietal','Arc_R_TemporoParietal','CGC_L','CGC_R','CGH_L','CGH_R','CorpusCallosum_Genu',
    #            'CorpusCallosum_Motor','CorpusCallosum_Parietal','CorpusCallosum_PreMotor','CorpusCallosum_Rostrum','CorpusCallosum_Splenium','CorpusCallosum_Tapetum','CorticoFugal-Left_Motor',
    #            'CorticoFugal-Left_Parietal','CorticoFugal-Left_PreFrontal','CorticoFugal-Left_PreMotor','CorticoFugal-Right_Motor','CorticoFugal-Right_Parietal','CorticoFugal-Right_PreFrontal',
    #            'CorticoFugal-Right_PreMotor','CorticoRecticular-Left','CorticoRecticular-Right','CorticoSpinal-Left','CorticoSpinal-Right','CorticoThalamic_L_PreFrontal','CorticoThalamic_L_SUPERIOR',
    #            'CorticoThalamic_Left_Motor','CorticoThalamic_Left_Parietal','CorticoThalamic_Left_PreMotor','CorticoThalamic_R_PreFrontal','CorticoThalamic_R_SUPERIOR',
    #            'CorticoThalamic_Right_Motor','CorticoThalamic_Right_Parietal','CorticoThalamic_Right_PreMotor','Fornix_L','Fornix_R','IFOF_L','IFOF_R','ILF_L','ILF_R',
    #            'OpticRadiation_Left','OpticRadiation_Right','Optic_Tract_L','Optic_Tract_R','SLF_II_L','SLF_II_R','UNC_L','UNC_R']
    # self.fiberList.addItems(name_labels)
    # self.fiberList.setMaxVisibleItems(5)
    # # selectionFibersFormLayout.addRow(self.selectionFiber)
    # selectionFibersFormLayout.addRow(self.selectionFiber)

    # self.disROI = self.getWidget('DisableROI')
    # self.posROI = self.getWidget('PositiveROI')
    # self.negROI = self.getWidget('NegativeROI')
    # self.interROI = self.getWidget('InteractiveROI')
    # self.showROI = self.getWidget('ROIVisibility')

    # # self.accEditOn = self.getWidget('EnableAccurateEdit')
    # self.extractFiber = self.getWidget('CreateNewFiberBundle')

    # self.ROISelector = slicer.qSlicerTractographyEditorROIWidget()
    # self.ROISelector.setFiberBundleNode(self.inputFiber.currentNode())
    # self.ROISelector.setMRMLScene(slicer.mrmlScene)
    # self.ROISelector.setAnnotationMRMLNodeForFiberSelection(self.ROISelectorDisplay.currentNode())
    # self.ROISelector.setAnnotationROIMRMLNodeToFiberBundleEnvelope(self.ROISelectorDisplay.currentNode())


    # # self.layout.addWidget(self.ROISelector)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # #                                 FIBER REVIEW AREA                                 #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # reviewsCollapsibleButton = ctk.ctkCollapsibleButton()
    # reviewsCollapsibleButton.text = "Reviews"
    # self.layout.addWidget(reviewsCollapsibleButton)

    # self.reviewsFormLayout = qt.QFormLayout(reviewsCollapsibleButton)
    # self.reviewsList = slicer.qMRMLTractographyDisplayTreeView()
    # self.reviewsList.setMRMLScene(slicer.mrmlScene)
    # self.reviewsFormLayout.addRow(self.reviewsList)


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # #                                 CLEAR AND SAVE AREA                               #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # self.dFPath = qt.QLineEdit("Select displacement field for the fiber")
    # # self.dFPath.setEnabled(False)

    # self.atalsSelector = qt.QPushButton("Browse")
    # self.clearButton = qt.QPushButton("CLEAR")
    # self.clearButton.toolTip = "Clear everything."
    # self.clearButton.enabled = True
    # self.saveButton = qt.QPushButton("SAVE")
    # self.saveButton.toolTip = "Save and update Traffic database."
    # self.saveButton.enabled = True

    #     # self.layout.addWidget(self.ROISelector)
    # gridLayoutdF = qt.QGridLayout()
    # gridLayoutClearSave = qt.QGridLayout()

    # gridLayoutdF.addWidget(qt.QLabel("Displacement field"), 0, 0)
    # gridLayoutdF.addWidget(self.dFPath, 0, 1)
    # gridLayoutdF.addWidget(self.atalsSelector, 0, 2)
    # gridLayoutClearSave.addWidget(self.clearButton, 0, 0)
    # gridLayoutClearSave.addWidget(self.saveButton, 0, 2)
    # self.layout.addLayout(gridLayoutdF)
    # self.layout.addLayout(gridLayoutClearSave)

    # self.nodeDict = {}

    # # Initialization of the dictionnary that will contains the Node ID and their type
    # for i in xrange(1, len(name_labels)):
    #   self.nodeDict[name_labels[i]] = []


    # # self.layout.addStretch(1)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # #                                 CONNECTIONS                                       #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # self.inputFiber.connect("currentNodeChanged(vtkMRMLNode*)", self.onChangeCurrentNode)
    # self.disROI.connect("toggled(bool)", self.onDisROI)
    # self.posROI.connect("toggled(bool)", self.onPosROI)
    # self.negROI.connect("toggled(bool)", self.onNegROI)
    # self.interROI.connect("toggled(bool)", self.onInterROI)
    # self.showROI.connect("toggled(bool)", self.onShowROI)
    # # self.accEditOn.connect("toggled(bool)", self.onAccEditOn)

    # self.ROISelectorDisplay.connect("currentNodeChanged(vtkMRMLNode*)", self.onChangeCurrentNode)
    # self.ROISelectorDisplay.connect("nodeAddedByUser(vtkMRMLNode*)", self.onAddNode)
    # self.saveButton.connect("clicked(bool)", self.onSaveButton)
    # self.clearButton.connect("clicked(bool)", self.onClearButton)

    # self.extractFiber.connect("clicked(bool)", self.OnExtractFiber)
    # self.atalsSelector.connect("clicked(bool)", self.OndFSelector)
    # self.dFPath.connect("editingFinished()", self.checkdFPath)


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

  def OndFSelector(self):
    fileDialog = qt.QFileDialog()
    fileDialog.setFileMode(qt.QFileDialog.ExistingFile)
    fileDialog.setNameFilter("displacement field (*.nrrd)")
    if fileDialog.exec_():
      text = fileDialog.selectedFiles()
      self.dFPath.setText(text[0])

  def checkdFPath(self):
    if self.dFPath.text.rfind(".nrrd") == -1:
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("Invalid File Format. Must be a .nrrd file. Please correct the displacement field filename")
      msg.exec_()
      return False
    if not os.path.isfile(self.dFPath.text):
      msg = qt.QMessageBox()
      msg.setIcon(3)
      msg.setText("Invalid File Format. File doesn't exist. Please correct the displacement field filename")
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
    if self.checkdFPath():
      warning_msg = qt.QMessageBox()
      warning_msg.setIcon(2)
      warning_msg.setText("Your selection will directly be add to the\n"
                          "training database of the Traffic tool and will\n" 
                          "have an impact on the resulting training model.\n"
                          "Are you sure this is what you want?")
      warning_msg.setStandardButtons(qt.QMessageBox.Save | qt.QMessageBox.Cancel)
      choice = warning_msg.exec_()
      if(choice == qt.QMessageBox.Save):
        logic = TrafficMultiLogic()
        logic.runSaveFiber(self.nodeDict, TMP_DIR)
        self.removeNodeExtracted()
        # Initialization of the dictionnary
        for key in self.nodeDict.keys():
          self.nodeDict[key] = []

        logic.runPreProcess(self.dFPath.displayText, TMP_DIR)
        # logic.runStore()


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
      
      logic = TrafficMultiLogic()
      logic.runExtractFiber(self.ROISelector, self.posROI.isChecked(), self.negROI.isChecked())

    return
#
# TrafficMultiLogic
#

class TrafficMultiLogic(ScriptedLoadableModuleLogic):
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

  def runPreProcess(self, dF_path, input_dir):

      #TO CHANGE: LOCATION OF CLI AND VARIABLES
      polydatatransform = "/work/dprince/TRAFIC/src/cxx/polydatatransform/bin/bin/polydatatransform"
      dti_reg = "/tools/bin_linux64/DTI-Reg"
      dti_ped = "/work/dprince/Data/TrainingData/Ped_1y_2y/PediatricAtlas_071714FinalAtlasDTI.nrrd"
      lm_ped = "/work/dprince/Multiclass/Landmarks/landmarks_32pts_afprop.fcsv"
      tmp_dir = "/work/dprince/tmp_dir"

      logging.info('Preprocessing started')
      dF_path = os.path.join(tmp_dir, "displacementField.nrrd")
      new_lm_path = os.path.join(tmp_dir, "landmarks_fibers_extracted.fcsv")
      if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)

      # Registration between target and source atlases
      # cmd_dti_reg = [dti_reg, "--outputFolder", tmp_dir, "--fixedVolume", dti_fix, "--movingVolume", dti_ped, "--outputDisplacementField", dF_path, "--ResampleDTIPath", 
      # "/tools/bin_linux64/ResampleDTIlogEuclidean", "--ITKTransformToolsPath", "/tools/bin_linux64/ITKTransformTools"]
      # out, err = subprocess.Popen(cmd_dti_reg, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
      # # print("\nout : " + str(out))
      # if err != "":
      #   print("\nerr : " + str(err))
      # Propagation of landmarks to the target space
      logging.info('Polydata transform')
      cmd_polydatatransform = [polydatatransform, "--invertx", "--inverty", "--fiber_file", lm_ped, "-D", dF_path, "-o", new_lm_path]
      out, err = subprocess.Popen(cmd_polydatatransform, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
      # print("\nout : " + str(out))
      if err != "":
        print("\nerr : " + str(err))
      logging.info('Make Dataset')
      run_make_dataset(input_dir, TRAIN_DIR, new_lm_path, landmarksOn=True)
      # p_pdt = subprocess.Popen(cmd_polydatatransform, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      # out, err = p_pdt.communicate()
      # print("\nout : " + str(out) + "\nerr : " + str(err))

      # p= subprocess.Popen(cmd_test, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      # out, err = p.communicate()
      # print("\nout : " + str(out) + "\nerr : " + str(err))
      # run_preprocess(TMP_DIR, TRAIN_DIR, str(dti_fix), landmarksOn=True, curvatureOn=True, torsionOn=True)
      # check_call(cmd_polydatatransform)
      logging.info('Preprocessing completed')

      return

  def runStore(self):

    return
    # selector.createNewBundleFromSelection()
    # selector.negativeROISelection()







    # if not self.isValidInputOutputData(inputVolume, outputVolume):
    #   slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
    #   return False

 

    # # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    # cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    # cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # # Capture screenshot
    # if enableScreenshots:
    #   self.takeScreenshot('TrafficMultiTest-Start','MyScreenshot',-1)

    # logging.info('Processing completed')

    # return True


class TrafficMultiTest(ScriptedLoadableModuleTest):
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
    self.test_TrafficMulti1()

  def test_TrafficMulti1(self):
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
    logic = TrafficMultiLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
