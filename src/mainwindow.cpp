#include "mainwindow.h"
#include "./ui_mainwindow.h"

#include <QTimer>

float PowerSum;
uint8_t powerCounter;

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent), ui(new Ui::dashboard_window),
      m_serial(new QSerialPort(this)) {
  ui->setupUi(this);

  // Set default background colors
  QPalette pal = QPalette();
  pal.setColor(QPalette::Window, this->m_light_gray);
  this->setAutoFillBackground(true);
  this->setPalette(pal);
  pal.setColor(QPalette::Base, this->m_dark_gray);
  ui->battery_icon->setStyleSheet(
      "border: 0; background-color: rgba(0,0,0,0);");
  ui->state_of_charge->setAutoFillBackground(true);
  ui->state_of_charge->setBackgroundRole(QPalette::Base);
  ui->state_of_charge->setPalette(pal);
  ui->temp_icon->setStyleSheet("border: 0; background-color: rgba(0,0,0,0);");
  ui->temperature->setAutoFillBackground(true);
  ui->temperature->setBackgroundRole(QPalette::Base);
  ui->temperature->setPalette(pal);
  ui->volt_icon->setStyleSheet("border: 0; background-color: rgba(0,0,0,0);");
  ui->voltage_steps->setAutoFillBackground(true);
  ui->voltage_steps->setBackgroundRole(QPalette::Base);
  ui->voltage_steps->setPalette(pal);
  ui->power_consumption->setAutoFillBackground(true);
  ui->power_consumption->setBackgroundRole(QPalette::Base);
  ui->power_consumption->setPalette(pal);

  // Set up video output screen
  m_camera = new QCamera(QMediaDevices::defaultVideoInput());
  m_camera->start();
  m_media_session = new QMediaCaptureSession;
  m_media_session->setCamera(m_camera);
  m_media_session->setVideoOutput(ui->video_screen);

  // Set up scenes
  ui->battery_icon->setScene(new QGraphicsScene);
  ui->temp_icon->setScene(new QGraphicsScene);
  ui->volt_icon->setScene(new QGraphicsScene);

  // Setup battery SVG
  QGraphicsSvgItem *battery_svg = new QGraphicsSvgItem();
  ui->battery_icon->scene()->addItem(battery_svg);
  m_renderer->load(QString(":/resource/battery.svg"));
  battery_svg->setSharedRenderer(m_renderer);
  battery_svg->setScale(0.2);

  // Setup voltage steps SVG
  //  QGraphicsSvgItem *volt_svg = new QGraphicsSvgItem();
  //  m_renderer->load(QString(":/resource/lightning.svg"));
  //  volt_svg->setSharedRenderer(m_renderer);
  //  ui->volt_icon->scene()->addItem(volt_svg);

  // Setup thermomter SVG
  //  QGraphicsSvgItem *temp_svg = new QGraphicsSvgItem();
  //  m_renderer->load(QString(":/resource/thermometer.svg"));
  //  temp_svg->setSharedRenderer(m_renderer);
  //  ui->temp_icon->scene()->addItem(temp_svg);

  // Setup power consumption SVG
  ui->test_icon->load(QString(":/resource/lightning.svg"));

  // Conenctors
  connect(m_serial, &QSerialPort::readyRead, this, &MainWindow::readData);
}

MainWindow::~MainWindow() {
  m_camera->stop();
  m_serial->close();
  delete ui;
}

void MainWindow::openSerialPort() {
  m_serial->setPortName("COM3");
  m_serial->setBaudRate(QSerialPort::Baud9600);
  m_serial->setDataBits(QSerialPort::Data8);
  m_serial->setParity(QSerialPort::NoParity);
  m_serial->setStopBits(QSerialPort::OneStop);
  m_serial->setFlowControl(QSerialPort::NoFlowControl);
  m_serial->open(QIODevice::ReadWrite);
}

void MainWindow::setStateOfCharge(short state_of_charge) {
  // Update battery SVG path and stroke colors
  if (state_of_charge > 80) {
    // Dark green color
  } else if (state_of_charge > 60) {
    // Light green color
  } else if (state_of_charge > 40) {
    // Yellow color
  } else if (state_of_charge > 20) {
    // Orange color
  } else {
    // Red color
  }
  // Set state of charge label
}

void MainWindow::setTemperatures(short l_id, short l_temp, short h_id,
                                 short h_temp) {}

void MainWindow::setVoltageSteps(short l_id, float l_volt, short h_id,
                                 float h_volt) {}

void MainWindow::setSpeed(short speed) {}

void MainWindow::setSlowPowerConsumption(float power) {}

void MainWindow::setFastPowerConsumption(float power) {}

void MainWindow::reset() { QTextStream(stdout) << "\n"; }

void MainWindow::startTimer() {
  QTimer *timer = new QTimer(this);
  connect(timer, SIGNAL(timeout()), this, SLOT(reset()));
  timer->start(5000);
}

void MainWindow::readData() {
  char nucleoData[203];
  int byteCounter = 0;
  QByteArray data = m_serial->read(1);
  QByteArray data1 = data;

  if (data1.size() > 0) {

    unsigned int j = data1.at(0);

    if ((uint8_t)j == 254) {

      data = m_serial->read(16);
      data1 = data;
      if (data1.size() > 0) {
        byteCounter = data1.size() + byteCounter + 1;
        for (int i = 0; i < data1.size(); i++) {
          nucleoData[byteCounter - data1.size() + 1] = data1.at(i);
        }

        if (byteCounter == 17 && (uint8_t)j == 254 &&
            (uint8_t)data1.at(15) == 255) {
          QTextStream(stdout) << (uint8_t)j << "  ";
          nucleoData[0] = (uint8_t)j;
          for (int i = 0; i < byteCounter - 1; i++) {

            nucleoData[i] = (uint8_t)data1.at(i);
            QTextStream(stdout) << (uint8_t)nucleoData[i] << "  ";
          }
          QTextStream(stdout) << "\n";

          uint8_t HighTemp = (uint8_t)nucleoData[0];
          uint8_t InternalTemp = (uint8_t)nucleoData[1];
          uint8_t LowCellVoltageLsb = (uint8_t)nucleoData[2];
          uint8_t LowCellVoltageMsb = (uint8_t)nucleoData[3];
          uint8_t HighCellVoltageLsb = (uint8_t)nucleoData[4];
          uint8_t HighCellVoltageMsb = (uint8_t)nucleoData[5];
          uint8_t LowCellVoltageId = (uint8_t)nucleoData[6];
          uint8_t HighCellVoltageId = (uint8_t)nucleoData[7];
          uint8_t PackSOC = (uint8_t)nucleoData[8];
          uint8_t RelayState = (uint8_t)nucleoData[9];
          uint8_t PackAvgTemp = (uint8_t)nucleoData[10];
          uint8_t LowCellTemp = (uint8_t)nucleoData[11];
          uint8_t HighCellTemp = (uint8_t)nucleoData[12];
          uint8_t LowCellTempId = (uint8_t)nucleoData[13];
          uint8_t HighCellTempId = (uint8_t)nucleoData[14];
          uint16_t LowCellVoltage =
              ((uint16_t)LowCellVoltageMsb << 8) | LowCellVoltageLsb;
          uint16_t HighCellVoltage =
              ((uint16_t)HighCellVoltageMsb << 8) | HighCellVoltageLsb;

          byteCounter = 0;
          this->setVoltageSteps(LowCellVoltageId, LowCellVoltage,
                                HighCellVoltageId, HighCellVoltage);
          this->setTemperatures(LowCellTempId, LowCellTemp, HighCellTempId,
                                HighCellTemp);
          this->setStateOfCharge(PackSOC);
        }
      }

    } else if ((uint8_t)j == 252) {
      nucleoData[0] = j;
      data = m_serial->read(7);
      data1 = data;
      if (data1.size() > 0) {
        byteCounter = data1.size() + byteCounter + 1;

        for (int i = 0; i < data1.size(); i++) {
          nucleoData[byteCounter - data1.size() + 1] = data1.at(i);
        }

        if (byteCounter == 8 && (uint8_t)j == 252 &&
            (uint8_t)data1.at(6) == 253)
          QTextStream(stdout) << (uint8_t)j << "  ";
        nucleoData[0] = (uint8_t)j;
        for (int i = 0; i < byteCounter - 1; i++) {

          nucleoData[i] = (uint8_t)data1.at(i);
          QTextStream(stdout) << (uint8_t)nucleoData[i] << "  ";
        }
        uint8_t PackCurrentLsb = (uint8_t)nucleoData[0];
        uint8_t PackCurrentMsb = (uint8_t)nucleoData[1];
        uint8_t PackVoltageLsb = (uint8_t)nucleoData[2];
        uint8_t PackVoltageMsb = (uint8_t)nucleoData[3];
        uint8_t FrameCount = (uint8_t)nucleoData[4];
        uint8_t Speed = (uint8_t)nucleoData[5];

        uint16_t PackCurrent = ((uint16_t)PackCurrentMsb << 8) | PackCurrentLsb;
        uint16_t PackVoltage = ((uint16_t)PackVoltageMsb << 8) | PackVoltageLsb;

        QTextStream(stdout) << "\n";
        byteCounter = 0;
        this->setSpeed(Speed);
      }
    }
  }
}
