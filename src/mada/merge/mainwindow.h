#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

#include <QCamera>
#include <QMediaCaptureSession>
#include <QMediaDevices>
#include <QSerialPort>
#include <QVideoWidget>
#include <QWidget>

QT_BEGIN_NAMESPACE
class QLabel;
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class Console;
class SettingsDialog;
class MainWindow : public QMainWindow {
  Q_OBJECT

public:
  MainWindow(QWidget *parent = nullptr);
  ~MainWindow();

  void modifyNumber(int num);
  void turn(bool direction);
  void noTurn();
  void setSoC(int soC);
  void headlightsOn();
  void headlightsOff();
  void hazardOn();
  void hazardOff();
  void setTemp(int temp);
  void setVoltage(int voltage);
  void setMPPT(bool isOn);
  void openSerialPort();
  void closeSerialPort();
  void about();
  void writeData(const QByteArray &data);
  void readData();

  void handleError(QSerialPort::SerialPortError error);

private:
  Ui::MainWindow *ui;
  QCamera *camera;
  QMediaCaptureSession *mediaCaptureSession;
  QVideoWidget *videoWidget;
  void showStatusMessage(const QString &message);

  Ui::MainWindow *m_ui = nullptr;
  QLabel *m_status = nullptr;
  Console *m_console = nullptr;
  SettingsDialog *m_settings = nullptr;
  QSerialPort *m_serial = nullptr;
};
#endif // MAINWINDOW_H
