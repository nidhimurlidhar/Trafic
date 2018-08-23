FROM tensorflow/tensorflow:1.5.0-gpu-py3

WORKDIR "/"

RUN apt-get update

## install vtk for python and dependencies
RUN pip3 install vtk
RUN apt-get install -y libsm6 libxt6 libxext6

## install git and cmake
RUN apt-get install -y --no-install-recommends git cmake

## clone trafic
RUN git clone https://github.com/lopezmt/Trafic.git

## install dependencies and setup the environment
RUN pip3 install imblearn

## build bin utilities
RUN mkdir /builds /utils

WORKDIR "/utils"
RUN git clone https://github.com/NIRALUser/niral_utilities.git
RUN git clone https://github.com/InsightSoftwareConsortium/ITK.git
RUN git clone https://github.com/Slicer/SlicerExecutionModel.git
RUN git clone https://gitlab.kitware.com/vtk/vtk.git

WORKDIR "/utils/vtk"
RUN git checkout tags/v6.3.0
WORKDIR "/utils/ITK"
RUN git checkout tags/v4.12.2

WORKDIR "/builds"
RUN mkdir ITK_build VTK_build niral_utilities_build trafic_build SEM_build

WORKDIR "/builds/ITK_build"
RUN cmake /utils/ITK/ -DBUILD_TESTING:BOOL=FALSE -DModule_MGHIO:BOOL=TRUE && make -j12

WORKDIR "/builds/VTK_build"
RUN cmake /utils/vtk/ -DBUILD_TESTING:BOOL=FALSE -DVTK_Group_Rendering:BOOL=FALSE -DVTK_Group_StandAlone:BOOL=FALSE -DVTK_BUILD_ALL_MODULES_FOR_TESTS:BOOL=FALSE -DModule_vtkCommonCore:BOOL=TRUE -DModule_vtkIOXML:BOOL=TRUE -DModule_vtkIOLegacy:BOOL=TRUE -DModule_vtkFiltersGeneral:BOOL=TRUE -DBUILD_EXAMPLES:BOOL=FALSE && make -j12

WORKDIR "/builds/SEM_build"
RUN cmake /utils/SlicerExecutionModel -DITK_DIR:PATH=/builds/ITK_build -DBUILD_TESTING:BOOL=FALSE && make -j12

WORKDIR "/builds/niral_utilities_build"
RUN cmake /utils/niral_utilities/ -DBUILD_TESTING:BOOL=FALSE -DITK_DIR:PATH=/builds/ITK_build -DVTK_DIR:PATH=/builds/VTK_build -DCOMPILE_IMAGEMATH:BOOL=FALSE -DSlicerExecutionModel_DIR:PATH=/builds/SEM_build && make -j12 && make install

WORKDIR "/builds/trafic_build"
RUN export CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}:/builds/niral_utilities_build
RUN cp /utils/niral_utilities/niral_utilitiesConfig.cmake.in /builds/niral_utilities_build/niral_utilitiesConfig.cmake
RUN cmake /Trafic -DUSE_SYSTEM_VTK:BOOL=TRUE  -DUSE_SYSTEM_ITK:BOOL=TRUE  -DUSE_SYSTEM_SlicerExecutionModel:BOOL=TRUE  -DUSE_SYSTEM_niral_utilities:BOOL=TRUE -DVTK_DIR:PATH=/builds/VTK_build -DITK_DIR:PATH=/builds/ITK_build -Dniral_utilities_DIR:PATH=/builds/niral_utilities_build -DSlicerExecutionModel_DIR:PATH=/builds/SEM_build && make -j12


# copy all cli tools used by trafic in the cli-modules directory, then add it to $PATH
RUN mkdir /cli-modules
RUN cp /builds/trafic_build/Trafic-build/CLI/cxx/fiber*/bin/* /cli-modules
RUN cp /builds/trafic_build/Trafic-build/CLI/cxx/createLandmarks/bin/* /cli-modules
RUN ln -s /builds/niral_utilities_build/bin/polydatatransform /cli-modules/polydatatransform
ENV PATH "$PATH:/cli-modules"