#-----------------------------------------------------------------------------
set(MODULE_NAME TraficLib)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  PipelineTrain.py
  envTensorFlow.py
  extractClassifiedFibers.py
  fiber_preprocessing.py
  fiberfileIO.py
  makeDataset.py
  networkDef.py
  runClassification.py
  runPCA.py
  runStore.py
  runTraining.py
  smote.py
  storeDef.py
  )
set(MODULE_PYTHON_RESOURCES
  Resources/envInstall.sh
  Resources/envInstallTFLinux.sh
  Resources/envInstallTFMacOS.sh

  )

if(${LOCAL_PROJECT_NAME}_BUILD_SLICER_EXTENSION)
  #-----------------------------------------------------------------------------
  slicerMacroBuildScriptedModule(
    NAME ${MODULE_NAME}
    SCRIPTS ${MODULE_PYTHON_SCRIPTS}
    RESOURCES ${MODULE_PYTHON_RESOURCES}
    WITH_GENERIC_TESTS
    )
else()
  install( FILES ${MODULE_PYTHON_SCRIPTS}
    DESTINATION ${INSTALL_LIBRARY_DESTINATION}/Trafic/TraficLib
  )
endif()

