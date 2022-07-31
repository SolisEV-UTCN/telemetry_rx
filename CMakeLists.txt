cmake_minimum_required(VERSION 3.23)
project(solis VERSION 0.1.0 LANGUAGES CXX)

include(CTest)
enable_testing()

set(BUILD_PATH "./build")
set(SOURCE_PATH "./src")
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_FIND_PACKAGE_PREFER_CONFIG TRUE)

find_package(Qt6 REQUIRED COMPONENTS Core)

add_executable(solis ${SOURCE_PATH}/main.cpp)
target_link_libraries(solis PRIVATE Qt6::Core)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
