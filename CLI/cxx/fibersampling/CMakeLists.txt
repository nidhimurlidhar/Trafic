
cmake_minimum_required(VERSION 2.8)

PROJECT(FiberSampling)

enable_testing()
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
  NAME fibersampling
  ADDITIONAL_SRCS ${source_files}
  EXECUTABLE_ONLY
  TARGET_LIBRARIES ${ITK_LIBRARIES} ${VTK_LIBRARIES} ${ITK_LIBRARIES}
  )