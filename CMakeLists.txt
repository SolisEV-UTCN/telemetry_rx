cmake_minimum_required(VERSION 3.23)
project(solis VERSION 1.0.0 LANGUAGES CXX)

set(BUILD_PATH "./build")
set(SOURCE_PATH "./src")

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS
  Core
  Gui
  Multimedia
  MultimediaWidgets
  SerialPort
  Svg
  SvgWidgets
  Widgets
)


add_executable(solis
  ${SOURCE_PATH}/helper.cpp
  ${SOURCE_PATH}/helper.h
  ${SOURCE_PATH}/main.qrc
  ${SOURCE_PATH}/main.cpp
  ${SOURCE_PATH}/mainwindow.cpp
  ${SOURCE_PATH}/mainwindow.h
  ${SOURCE_PATH}/mainwindow.ui
)
target_link_libraries(solis PRIVATE
  Qt6::Core
  Qt6::Gui
  Qt6::Multimedia
  Qt6::MultimediaWidgets
  Qt6::SerialPort
  Qt6::Svg
  Qt6::SvgWidgets
  Qt6::Widgets
)

set_target_properties(solis PROPERTIES
  WIN32_EXECUTABLE TRUE
)

qt_finalize_executable(solis)
