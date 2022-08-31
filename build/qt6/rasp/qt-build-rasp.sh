#!/bin/sh

# Author : Solar
# Copyright (c) Apache 2.0
# Script follows here:

~/solis/libs/qt6/configure \
 -release \
 -opengl es2 \
 -nomake examples \
 -nomake tests \
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
 -no-feature-accessibility \
 -no-feature-appstore-compliant \
 -no-feature-pdf \
 -no-feature-qtpdf-build \
 -no-feature-qtpdf-quick-build \
 -no-feature-qtpdf-widgets-build \
 -no-feature-qtwebengine-build \
 -no-feature-qtwebengine-core-build \
 -no-feature-qtwebengine-quick-build \
 -no-feature-qtwebengine-widgets-build \
 -no-feature-translation \
 -no-feature-webengine-developer-build \
 -no-feature-webengine-embedded-build \
 -no-feature-webengine-extensions \
 -no-feature-webengine-full-debug-info \
 -no-feature-webengine-jumbo-build \
 -no-feature-webengine-kerberos \
 -no-feature-webengine-native-spellchecker \
 -no-feature-webengine-pepper-plugins \
 -no-feature-webengine-printing-and-pdf \
 -no-feature-webengine-proprietary-codecs \
 -no-feature-webengine-sanitizer \
 -no-feature-webengine-spellchecker \
 -no-feature-webengine-webchannel \
 -no-feature-webengine-webrtc \
 -no-feature-webengine-webrtc-pipewire \
 -qt-host-path /usr/local/Qt-6.2.4 \
 -extprefix /home/misha/solis/build/qt6/rasp \
 -prefix /usr/local/qt6 \
 -device linux-rasp-pi4-aarch64 \
 -device-option CROSS_COMPILE=aarch64-linux-gnu- -- \
 -DCMAKE_TOOLCHAIN_FILE=/home/misha/solis/toolchain.cmake \
 -DQT_FEATURE_xcb=ON \
 -DFEATURE_xcb_xlib=ON \
 -DQT_FEATURE_xlib=ON
