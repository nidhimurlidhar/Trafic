#-----------------------------------------------------------------------------
set(MODULE_NAME TraficLib)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  envInstallTF.py
  fiberfileIO.py
  makeDataset.py
  networkDef.py
  PipelineEval.py
  PipelineTrain.py
  runClassification.py
  runStore.py
  runTraining.py
  storeDef.py
  )
set(MODULE_PYTHON_RESOURCES
  Resources/envInstall.sh
  Resources/envInstallTFLinux.sh
  Resources/envInstallTFMacOS.sh

  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

