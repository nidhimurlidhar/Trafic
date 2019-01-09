#-----------------------------------------------------------------------------
set(MODULE_NAME TraficMulti)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  Resources/UI/TraficMultiEditionTab.ui
  Resources/Landmarks/landmarks_32pts_afprop.fcsv

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
  install(FILES TraficMulti_cli.py
    DESTINATION ${INSTALL_LIBRARY_DESTINATION}/TraficMulti)
    
endif()

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Register the unittest subclass in the main script as a ctest.
  # Note that the test will also be available at runtime.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # Additional build-time testing
  add_subdirectory(Testing)
endif()
