#include "mainwindow.h"

#include <QApplication>
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QSerialPort>
#include <QSerialPortInfo>

int main(int argc, char *argv[]) {
  QApplication a(argc, argv);

  QQmlApplicationEngine engine;
  const QUrl url(QStringLiteral("qrc:/main.qml"));
  MainWindow w;
  QSize windowSize(1920, 1080);
  w.resize(windowSize);
  w.setStyleSheet("QMainWindow {background: rgb(48,48,47);}");
  w.show();
  w.openSerialPort();
  w.readData();

  return a.exec();
}
