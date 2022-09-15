#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QCamera>
#include <QGraphicsSvgItem>
#include <QMainWindow>
#include <QMediaCaptureSession>
#include <QMediaDevices>
#include <QPainter>
#include <QSerialPort>
#include <QSvgRenderer>
#include <QVideoWidget>
#include <QWidget>

QT_BEGIN_NAMESPACE
class QLabel;
namespace Ui {
class dashboard_window;
}
QT_END_NAMESPACE

class Console;
class SettingsDialog;
class MainWindow : public QMainWindow {
  Q_OBJECT

public:
  MainWindow(QWidget *parent = nullptr);
  ~MainWindow();

  // Setters
  void setStateOfCharge(short);
  void setTemperatures(short, short, short, short);
  void setVoltageSteps(short, float, short, float);
  void setSpeed(short);
  void setSlowPowerConsumption(float);
  void setFastPowerConsumption(float);
  // Serial communication
  void openSerialPort();
  void readData();
  void startTimer();

public slots:
  void reset();

private:
  Ui::dashboard_window *ui;
  QCamera *m_camera = nullptr;
  QMediaCaptureSession *m_media_session = nullptr;
  QSerialPort *m_serial = nullptr;
  QVideoWidget *m_video_widget = nullptr;

  // Colors
  const QColor m_dark_green = 0x2c9977;
  const QColor m_light_green = 0x73c05c;
  const QColor m_yellow = 0xffcc3f;
  const QColor m_orange = 0xff6a40;
  const QColor m_red = 0xff4099;
  const QColor m_dark_gray = 0x333333;
  const QColor m_light_gray = 0x555555;
  const QColor m_dark_blue = 0x177bbd;
  const QColor m_light_blue = 0x33b5e5;
  const QColor m_off_black = 0x1c1c1c;
  const QColor m_off_white = 0xaaaaaa;

  // SVG
  QSvgRenderer *m_rend_volt_h = new QSvgRenderer(QString(":/resource/volt_high.svg"));
  QSvgRenderer *m_rend_volt_l = new QSvgRenderer(QString(":/resource/volt_low.svg"));
  QSvgRenderer *m_rend_temp_h = new QSvgRenderer(QString(":/resource/temp_high.svg"));
  QSvgRenderer *m_rend_temp_l = new QSvgRenderer(QString(":/resource/temp_low.svg"));
  QSvgRenderer *m_rend_avg_pwr = new QSvgRenderer(QString(":/resource/power_avg.svg"));
  QSvgRenderer *m_rend_inst_pwr = new QSvgRenderer(QString(":/resource/power_inst.svg"));
};
#endif // MAINWINDOW_H
