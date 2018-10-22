
cmake_minimum_required(VERSION 2.8)

PROJECT(DistanceMapFilter)

#Find VTK Package
find_package(VTK REQUIRED)

#Find ITK Package
find_package(ITK REQUIRED)

#Find Slicer Execution Model Package
find_package(SlicerExecutionModel REQUIRED)

include(${VTK_USE_FILE})
include(${ITK_USE_FILE})
include(${SlicerExecutionModel_USE_FILE})


file(
GLOB
source_files
*.[ch]pp
*.[ch]xx
*.[ch]
)

SEMMacroBuildCLI(
  NAME distancemapfilter
  ADDITIONAL_SRCS ${source_files}
  EXECUTABLE_ONLY
  TARGET_LIBRARIES ${ITK_LIBRARIES} ${VTK_LIBRARIES}
  )

file(GLOB LIBRARY_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/*.txx ${CMAKE_CURRENT_SOURCE_DIR}/*.hxx ${CMAKE_CURRENT_SOURCE_DIR}/*.h)

set_target_properties(distancemapfilter PROPERTIES
  PUBLIC_HEADER "${LIBRARY_HEADERS}"
  )

install( TARGETS distancemapfilter 
  EXPORT TraficTargets
  RUNTIME DESTINATION ${INSTALL_RUNTIME_DESTINATION} 
  PUBLIC_HEADER DESTINATION include
  )
# Add all targets to the build-tree export set

set_property(GLOBAL APPEND PROPERTY Trafic_LIBRARIES distancemapfilter)