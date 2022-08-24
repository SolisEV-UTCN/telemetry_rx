cmake_minimum_required(VERSION 3.23)
project(solis VERSION 0.1.0 LANGUAGES CXX)

set(BUILD_PATH "./build")
set(SOURCE_PATH "./src")
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS
  Core
  Concurrent
  Gui
  Multimedia
  MultimediaWidgets
  Qml
  Quick
  SerialPort
  Widgets
)

add_library(speedometer STATIC 
  ${SOURCE_PATH}/speedometer.h
  ${SOURCE_PATH}/speedometer.cpp
)
target_link_libraries(speedometer PRIVATE
  Qt6::Core
  Qt6::Quick
)

add_executable(soils 
  ${SOURCE_PATH}/mainwindow.ui
  ${SOURCE_PATH}/mainwindow.h
  ${SOURCE_PATH}/mainwindow.cpp
  ${SOURCE_PATH}/main.cpp
)
target_link_libraries(soils PRIVATE
  speedometer
  Qt6::Core
  Qt6::Concurrent
  Qt6::Gui
  Qt6::Multimedia
  Qt6::MultimediaWidgets
  Qt6::Qml
  Qt6::Quick
  Qt6::SerialPort
  Qt6::Widgets
)

set_target_properties(soils PROPERTIES
  WIN32_EXECUTABLE ON
  VS_SOLUTION_DEPLOY ON
)
