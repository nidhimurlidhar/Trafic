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
endif()

find_package(niral_utilities REQUIRED
	HINTS ${niral_utilities_DIR})

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