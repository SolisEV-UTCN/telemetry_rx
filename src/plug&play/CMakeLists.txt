cmake_minimum_required(3.25)

project(solis_pp)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_executable(solis
  ${CMAKE_SOURCE_DIR}/main.cpp
  ${CMAKE_SOURCE_DIR}/helper/database.hpp
  ${CMAKE_SOURCE_DIR}/helper/database.cpp
  ${CMAKE_SOURCE_DIR}/helper/listener.hpp
  ${CMAKE_SOURCE_DIR}/helper/listener.cpp
)