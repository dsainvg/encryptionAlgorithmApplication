# CMakeLists.txt for encryption backend
# Build instructions (Windows example):
#   mkdir build && cd build
#   cmake -G "Visual Studio 17 2022" -A x64 -DPYBIND11_FINDPYTHON=ON ..
#   cmake --build . --config Release
# The resulting encryption_backend.* module (Release folder) can be copied into python/ or added to PYTHONPATH.
# Ensure pybind11 is available (installed via pip install pybind11 or provided as a submodule).

cmake_minimum_required(VERSION 3.15)
project(encryption_backend LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Target Python 3.13 explicitly
find_package(Python3 3.13 EXACT COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG QUIET)
if(NOT pybind11_FOUND)
    message(STATUS "pybind11 not found via CONFIG; using FetchContent to retrieve it")
    include(FetchContent)
    FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG v2.12.0
    )
    FetchContent_MakeAvailable(pybind11)
endif()

add_library(encryption_backend MODULE binding.cpp password_hasher.cpp crypto_operations.cpp)
# On Windows, ensure no 'lib' prefix and proper extension
if (MSVC)
    set_target_properties(encryption_backend PROPERTIES OUTPUT_NAME "encryption_backend" PREFIX "")
endif()

# Include current directory for headers
target_include_directories(encryption_backend PRIVATE ${CMAKE_CURRENT_SOURCE_DIR} ${Python3_INCLUDE_DIRS})

# Link pybind11 (handle different exported target names)
if(TARGET pybind11::module)
    target_link_libraries(encryption_backend PRIVATE pybind11::module)
elseif(TARGET pybind11::pybind11)
    target_link_libraries(encryption_backend PRIVATE pybind11::pybind11)
else()
    message(FATAL_ERROR "pybind11 target not found after FetchContent")
endif()

# Windows specific: set the suffix to .pyd for Python extension modules
if (WIN32)
    set_target_properties(encryption_backend PROPERTIES SUFFIX ".pyd")
    
    # Copy dependent DLLs to the output directory
    add_custom_command(TARGET encryption_backend POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "$<TARGET_RUNTIME_DLLS:encryption_backend>"
        "$<TARGET_FILE_DIR:encryption_backend>"
        COMMAND_EXPAND_LISTS)
endif()

# Optimize in Release
if (CMAKE_BUILD_TYPE STREQUAL "Release")
    if (MSVC)
        target_compile_options(encryption_backend PRIVATE /O2)
    else()
        target_compile_options(encryption_backend PRIVATE -O3)
    endif()
endif()
