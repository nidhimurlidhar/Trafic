#-----------------------------------------------------------------------------
set(MODULE_NAME TraficBi)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  Resources/UI/TraficBiEditionTab.ui
  Resources/Landmarks/Arc_L_FrontoParietal_bundle_clean_landmarks.fcsv
  Resources/Landmarks/Arc_L_FT_bundle_clean_landmarks.fcsv
  Resources/Landmarks/Arc_L_TemporoParietal_bundle_clean_landmarks.fcsv
  Resources/Landmarks/Arc_R_FrontoParietal_bundle_clean_landmarks.fcsv
  Resources/Landmarks/Arc_R_FT_bundle_clean_landmarks.fcsv
  Resources/Landmarks/Arc_R_TemporoParietal_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CGC_L_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CGC_R_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CGH_L_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CGH_R_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorpusCallosum_BODY_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorpusCallosum_Genu_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorpusCallosum_Parietal_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorpusCallosum_PreMotor_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorpusCallosum_Splenium_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorpusCallosum_Tapetum_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoFugal-Left_Motor_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoFugal-Left_Parietal_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoFugal-Left_PreFrontal_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoFugal-Left_PreMotor_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoFugal-Right_Motor_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoFugal-Right_Parietal_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoFugal-Right_PreFrontal_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoFugal-Right_PreMotor_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoRecticular-Left_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoRecticular-Right_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoSpinal-Left_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoSpinal-Right_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoThalamic_Left_Motor_bundle_final_clean_landmarks.fcsv
  Resources/Landmarks/CorticoThalamic_Left_Parietal_bundle_final_clean_landmarks.fcsv
  Resources/Landmarks/CorticoThalamic_Left_PreMotor_bundle_final_clean_landmarks.fcsv
  Resources/Landmarks/CorticoThalamic_L_PreFrontal_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoThalamic_L_SUPERIOR_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoThalamic_Right_Motor_bundle_final_clean_landmarks.fcsv
  Resources/Landmarks/CorticoThalamic_Right_Parietal_bundle_final_clean_landmarks.fcsv
  Resources/Landmarks/CorticoThalamic_Right_PreMotor_bundle_final_clean_landmarks.fcsv
  Resources/Landmarks/CorticoThalamic_R_PreFrontal_bundle_clean_landmarks.fcsv
  Resources/Landmarks/CorticoThalamic_R_SUPERIOR_bundle_clean_landmarks.fcsv
  Resources/Landmarks/Fornix_R_bundle_clean_landmarks.fcsv
  Resources/Landmarks/IFOF_L_bundle_clean_landmarks.fcsv
  Resources/Landmarks/IFOF_R_bundle_clean_landmarks.fcsv
  Resources/Landmarks/ILF_L_bundle_final_clean_landmarks.fcsv
  Resources/Landmarks/ILF_R_bundle_final_clean_landmarks.fcsv
  Resources/Landmarks/OpticRadiation_Left_bundle_clean_landmarks.fcsv
  Resources/Landmarks/OpticRadiation_Right_bundle_clean_landmarks.fcsv
  Resources/Landmarks/Optic_Tract_L_bundle_clean_landmarks.fcsv
  Resources/Landmarks/Optic_Tract_R_bundle_clean_landmarks.fcsv
  Resources/Landmarks/SLF_II_L_bundle_clean_landmarks.fcsv
  Resources/Landmarks/SLF_II_R_bundle_clean_landmarks.fcsv
  Resources/Landmarks/UNC_L_bundle_clean_landmarks.fcsv
  Resources/Landmarks/UNC_R_bundle_clean_landmarks.fcsv
  )

if(${LOCAL_PROJECT_NAME}_BUILD_SLICER_EXTENSION)
  #-----------------------------------------------------------------------------
  slicerMacroBuildScriptedModule(
    NAME ${MODULE_NAME}
    SCRIPTS ${MODULE_PYTHON_SCRIPTS}
    RESOURCES ${MODULE_PYTHON_RESOURCES}
    WITH_GENERIC_TESTS
    )
endif()

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Register the unittest subclass in the main script as a ctest.
  # Note that the test will also be available at runtime.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # Additional build-time testing
  add_subdirectory(Testing)
endif()
