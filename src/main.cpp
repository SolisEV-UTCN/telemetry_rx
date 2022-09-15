#include "mainwindow.h"

#include <QApplication>
#include <QGuiApplication>
#include <QScreen>
#include <QSerialPort>
#include <QSerialPortInfo>
#include <QSettings>
#include <QTimer>

int main(int argc, char *argv[]) {
  QApplication a(argc, argv);
  QSettings settings(
      "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
      QSettings::NativeFormat);
  settings.setValue("dashboard_window",
                    QCoreApplication::applicationFilePath().replace('/', '\\'));
  MainWindow w;
  w.show();
  w.startTimer();
  w.openSerialPort();
  w.readData();
  return a.exec();
}
