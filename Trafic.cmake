cmake_minimum_required(VERSION 2.8.9)

set(LOCAL_PROJECT_NAME Trafic)

project(Trafic)

if(${LOCAL_PROJECT_NAME}_BUILD_SLICER_EXTENSION)
	#-----------------------------------------------------------------------------
	# Extension meta-information
	set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/Trafic")
	set(EXTENSION_CATEGORY "Classification")
	set(EXTENSION_CONTRIBUTORS "Prince Ngattai Lam")
	set(EXTENSION_DESCRIPTION "")
	set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/Trafic.png")
	set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/Trafic/Screenshots/1.png")
	set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

	#-----------------------------------------------------------------------------
	# Extension dependencies
	find_package(Slicer REQUIRED)
	include(${Slicer_USE_FILE})

  SET(INSTALL_RUNTIME_DESTINATION ${Slicer_INSTALL_CLIMODULES_BIN_DIR})
  SET(INSTALL_LIBRARY_DESTINATION ${Slicer_INSTALL_CLIMODULES_LIB_DIR})
  SET(INSTALL_ARCHIVE_DESTINATION ${Slicer_INSTALL_CLIMODULES_LIB_DIR})
endif()

SETIFEMPTY(INSTALL_RUNTIME_DESTINATION bin)
SETIFEMPTY(INSTALL_LIBRARY_DESTINATION bin)
SETIFEMPTY(INSTALL_ARCHIVE_DESTINATION lib/static)
SETIFEMPTY(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)
SETIFEMPTY(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)
SETIFEMPTY(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)

find_package(niral_utilities REQUIRED
	HINTS ${niral_utilities_DIR})
include_directories(${niral_utilities_INCLUDE_DIRS})

if(NOT ${LOCAL_PROJECT_NAME}_BUILD_SLICER_EXTENSION)
  foreach(niral_utilities_lib ${niral_utilities_LIBRARIES})

    get_target_property(niral_utilities_location ${niral_utilities_lib} LOCATION_RELEASE)
    if(NOT EXISTS ${niral_utilities_location})
      message(STATUS "skipping niral_utilities_lib install rule: [${niral_utilities_location}] does not exist")
      continue()
    endif()

    install(PROGRAMS ${niral_utilities_location} 
    	DESTINATION ${INSTALL_RUNTIME_DESTINATION}
    	COMPONENT RUNTIME)
      
  endforeach()
endif()

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(TraficMulti)
add_subdirectory(TraficLib)
add_subdirectory(CLI/cxx)
## NEXT_MODULE

if(${LOCAL_PROJECT_NAME}_BUILD_SLICER_EXTENSION)
	#-----------------------------------------------------------------------------
	include(${Slicer_EXTENSION_GENERATE_CONFIG})
	include(${Slicer_EXTENSION_CPACK})
endif()

### This is the config file for niral_utilities
# Create the FooBarConfig.cmake and FooBarConfigVersion files

if(WIN32 AND NOT CYGWIN)
  set(DEF_INSTALL_CMAKE_DIR CMake)
else()
  set(DEF_INSTALL_CMAKE_DIR lib/CMake/Trafic)
endif()
set(INSTALL_CMAKE_DIR ${DEF_INSTALL_CMAKE_DIR} CACHE PATH
  "Installation directory for CMake files")
set(INSTALL_INCLUDE_DIR include)

# Make relative paths absolute (needed later on)
foreach(p LIB BIN INCLUDE CMAKE)
  set(var INSTALL_${p}_DIR)
  if(NOT IS_ABSOLUTE "${${var}}")
    set(${var} "${CMAKE_INSTALL_PREFIX}/${${var}}")
  endif()
endforeach()

file(RELATIVE_PATH REL_INCLUDE_DIR ${INSTALL_CMAKE_DIR} ${INSTALL_INCLUDE_DIR})
# ... for the build tree
set(CONF_INCLUDE_DIRS "${PROJECT_SOURCE_DIR}" "${PROJECT_BINARY_DIR}")
get_property(CONF_LIBRARIES GLOBAL PROPERTY Trafic_LIBRARIES)

configure_file(TraficConfig.cmake.in
  "${PROJECT_BINARY_DIR}/TraficConfig.cmake" @ONLY)
# ... for the install tree
set(CONF_INCLUDE_DIRS "\${Trafic_CMAKE_DIR}/${REL_INCLUDE_DIR}")
configure_file(TraficConfig.cmake.in
  "${PROJECT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/TraficConfig.cmake" @ONLY)

install(FILES
  "${PROJECT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/TraficConfig.cmake"
  DESTINATION "${INSTALL_CMAKE_DIR}" COMPONENT dev)
 
# Install the export set for use with the install-tree
install(EXPORT TraficTargets DESTINATION
"${INSTALL_CMAKE_DIR}" COMPONENT dev)

export(TARGETS ${CONF_LIBRARIES}
  FILE "${PROJECT_BINARY_DIR}/TraficTargets.cmake"
  )


