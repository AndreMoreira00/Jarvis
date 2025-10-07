cmake_minimum_required(VERSION 3.10)
project(JarvisDecoderTest)

set(CMAKE_CXX_STANDARD 11)

# Include directories
include_directories(src/includes/app)

# Try to find OpenCV
set(OpenCV_DIR "C:/opencv/build")
find_package(OpenCV REQUIRED)

if(OpenCV_FOUND)
    message(STATUS "OpenCV found: ${OpenCV_VERSION}")
    include_directories(${OpenCV_INCLUDE_DIRS})
else()
    message(STATUS "OpenCV not found, using local headers")
    include_directories(libs/opencv-4.12.0/opencv-4.12.0/include)
endif()

# Source files
set(SOURCES
    src/app/main.cpp
    src/app/modules/camera/camera.cpp
)

# Create main executable
add_executable(jarvis_main ${SOURCES})

# Link OpenCV libraries
if(OpenCV_FOUND)
    target_link_libraries(jarvis_main ${OpenCV_LIBS})
else()
    # For local build, you need to build OpenCV first
    message(WARNING "OpenCV libraries not linked - please install OpenCV or build from source")
endif()