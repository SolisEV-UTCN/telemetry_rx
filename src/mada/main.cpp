#include "mainwindow.h"

#include "worker.h"
#include <QApplication>
#include <QDebug>
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QSerialPort>
#include <QSerialPortInfo>
#include <QThread>
#include <QThreadPool>
#include <QTimer>
#include <QtConcurrent>

class Sleeper : public QThread {
public:
  static void usleep(unsigned long usecs) { QThread::usleep(usecs); }
  static void msleep(unsigned long msecs) { QThread::msleep(msecs); }
  static void sleep(unsigned long secs) { QThread::sleep(secs); }
};

int main(int argc, char *argv[]) {
  QApplication a(argc, argv);

  // trying something here
  /*
      QQmlApplicationEngine engine;
      const QUrl url(QStringLiteral("qrc:/main.qml"));
      QObject::connect(&engine, &QQmlApplicationEngine::objectCreated,
                       &a, [url](QObject *obj, const QUrl &objUrl) {
          if (!obj && url == objUrl)
              QCoreApplication::exit(-1);
      }, Qt::QueuedConnection);
      engine.load(url);
  */
  // ending here

  // Multithreading code starts here

  QQmlApplicationEngine engine;
  const QUrl url(QStringLiteral("qrc:/main.qml"));

  MainWindow w;
  QSize windowSize(1920, 1080);
  w.resize(windowSize);
  w.setStyleSheet("QMainWindow {background: rgb(48,48,47);}");
  // w.setStyleSheet("QMainWindow {background: black;}");
  w.show();
  w.openSerialPort();
  w.readData();

  // Sleeper::sleep(5);
  for (int i = 1; i < 20; i++) {
    // Sleeper::sleep(2);
    w.modifyNumber(i);
    QApplication::processEvents();
  }
  // w.modifyNumber(69);
  w.turn(false);
  w.setSoC(50);

  QTimer timer1;

  int soC = 0;
  int speed = 0;
  bool turnLeft = true;

  QObject::connect(&timer1, &QTimer::timeout, [&]() {
    turnLeft = turnLeft == false;
    soC = soC + 1;
    speed = speed + 1;
    w.setSoC(soC);
    w.setTemp(speed);
    w.setVoltage(speed);
    w.turn(turnLeft);
    w.setMPPT(turnLeft);

    if (turnLeft) {
      w.headlightsOn();
      w.hazardOff();
    } else {
      w.headlightsOff();
      w.hazardOn();
    }
  });

  timer1.start(100);

  return a.exec();
}
