#!/bin/sh

# Author : Solar
# Copyright (c) Apache 2.0
# Script follows here:

~/solis/libs/qt6/configure \
 -skip qt3d \
 -skip qt5compact \
 -skip qtcanvas3d \
 -skip qtcharts \
 -skip qtcoap \
 -skip qtactiveqt \
 -skip qtdatavis3d \
 -skip qtdoc \
 -skip qtfeedback \
 -skip qtgamepad \
 -skip qtlanguageserver \
 -skip qtmqtt \
 -skip qtnetworkauth \
 -skip qtopcau \
 -skip qtpim \
 -skip qtpositioning \
 -skip qtqa \
 -skip qtquick3d \
 -skip qtquicktimeline \
 -skip qtremoteobjects \
 -skip qtrepotools \
 -skip qtscxml \
 -skip qtsensors \
 -skip qtserialbus \
 -skip qtspeech \
 -skip qtsvg \
 -skip qtsystems \
 -skip qttranslations \
 -skip qttools \
 -skip qtvirtualkeyboard \
 -skip qtwayland \
 -skip qtwebchannel \
 -skip qtwebengine \
 -skip qtwebglplugin \
 -skip qtwebsockets \
 -skip qtwebview \
 -skip qtxmlpatterns \
 -release \
 -opengl es2 \
 -nomake examples \
 -nomake tests \
 -qt-host-path ~/solis/build/qt6/host \
 -extprefix ~/solis/build/qt6/rasp \
 -prefix /usr/local/qt6 \
 -device linux-rasp-pi4-aarch64 \
 -device-option CROSS_COMPILE=aarch64-linux-gnu- -- \
 -DCMAKE_TOOLCHAIN_FILE=$HOME/solis/toolchain.cmake \
 -DQT_FEATURE_xcb=ON \
 -DFEATURE_xcb_xlib=ON \
 -DQT_FEATURE_xlib=ON
