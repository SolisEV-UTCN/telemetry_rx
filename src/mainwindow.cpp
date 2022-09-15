#include "mainwindow.h"
#include "./ui_mainwindow.h"
#include "helper.h"

#include <QTimer>

float PowerSum;
uint8_t powerCounter;

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent), ui(new Ui::dashboard_window),
      m_serial(new QSerialPort(this)) {
  ui->setupUi(this);

  // Set default background colors
  QPalette pal = QPalette();
  pal.setColor(QPalette::Window, m_light_gray);
  this->setAutoFillBackground(true);
  this->setPalette(pal);
  pal.setColor(QPalette::Base, m_dark_gray);
  ui->state_of_charge->setAutoFillBackground(true);
  ui->state_of_charge->setBackgroundRole(QPalette::Base);
  ui->state_of_charge->setPalette(pal);
  ui->high_temp_icon->setStyleSheet("border: 0; background-color: rgba(0,0,0,0);");
  ui->low_temp_icon->setStyleSheet("border: 0; background-color: rgba(0,0,0,0);");
  ui->temperature->setAutoFillBackground(true);
  ui->temperature->setBackgroundRole(QPalette::Base);
  ui->temperature->setPalette(pal);
  ui->high_volt_icon->setStyleSheet("border: 0; background-color: rgba(0,0,0,0);");
  ui->low_volt_icon->setStyleSheet("border: 0; background-color: rgba(0,0,0,0);");
  ui->voltage_steps->setAutoFillBackground(true);
  ui->voltage_steps->setBackgroundRole(QPalette::Base);
  ui->voltage_steps->setPalette(pal);
  ui->power_consumption->setAutoFillBackground(true);
  ui->power_consumption->setBackgroundRole(QPalette::Base);
  ui->power_consumption->setPalette(pal);
  ui->power_avg_icon->setStyleSheet("border: 0; background-color: rgba(0,0,0,0);");
  ui->power_inst_icon->setStyleSheet("border: 0; background-color: rgba(0,0,0,0);");

  // Set font colors
  pal.setColor(QPalette::Text, m_light_blue);
  ui->low_temp_label_id->setPalette(pal);
  ui->low_temp_label_value->setPalette(pal);
  ui->low_volt_label_id->setPalette(pal);
  ui->low_volt_label_value->setPalette(pal);
  pal.setColor(QPalette::Text, m_red);
  ui->high_temp_label_id->setPalette(pal);
  ui->high_temp_label_value->setPalette(pal);
  ui->high_volt_label_id->setPalette(pal);
  ui->high_volt_label_value->setPalette(pal);
  pal.setColor(QPalette::Text, m_off_black);
  ui->speed_label->setPalette(pal);
  pal.setColor(QPalette::Text, m_off_white);
  ui->power_avg->setPalette(pal);
  ui->power_avg_label->setPalette(pal);
  ui->power_inst->setPalette(pal);
  ui->power_inst_label->setPalette(pal);

  // Set up video output screen
  m_camera = new QCamera(QMediaDevices::defaultVideoInput());
  m_camera->start();
  m_media_session = new QMediaCaptureSession;
  m_media_session->setCamera(m_camera);
  m_media_session->setVideoOutput(ui->video_screen);

  // Set up scenes
  ui->high_temp_icon->setScene(new QGraphicsScene);
  ui->low_temp_icon->setScene(new QGraphicsScene);
  ui->high_volt_icon->setScene(new QGraphicsScene);
  ui->low_volt_icon->setScene(new QGraphicsScene);
  ui->power_avg_icon->setScene(new QGraphicsScene);
  ui->power_inst_icon->setScene(new QGraphicsScene);

  // Setup battery SVG
  ui->battery_icon->load(rezolve_link(Battery::FULL));

  // Setup voltage steps SVG
  QGraphicsSvgItem *high_volt_svg = new QGraphicsSvgItem();
  QGraphicsSvgItem *low_volt_svg = new QGraphicsSvgItem();
  high_volt_svg->setSharedRenderer(m_rend_volt_h);
  high_volt_svg->setScale(0.1);
  low_volt_svg->setSharedRenderer(m_rend_volt_l);
  low_volt_svg->setScale(0.1);
  ui->high_volt_icon->scene()->addItem(high_volt_svg);
  ui->low_volt_icon->scene()->addItem(low_volt_svg);

  // Setup thermometer SVG
  QGraphicsSvgItem *high_temp_svg = new QGraphicsSvgItem();
  QGraphicsSvgItem *low_temp_svg = new QGraphicsSvgItem();
  high_temp_svg->setSharedRenderer(m_rend_temp_h);
  high_temp_svg->setScale(0.1);
  low_temp_svg->setSharedRenderer(m_rend_temp_l);
  low_temp_svg->setScale(0.1);
  ui->high_temp_icon->scene()->addItem(high_temp_svg);
  ui->low_temp_icon->scene()->addItem(low_temp_svg);

  // Setup power consumption SVG
  QGraphicsSvgItem *avg_power_svg = new QGraphicsSvgItem();
  QGraphicsSvgItem *inst_power_svg = new QGraphicsSvgItem();
  avg_power_svg->setSharedRenderer(m_rend_avg_pwr);
  avg_power_svg->setScale(0.08);
  inst_power_svg->setSharedRenderer(m_rend_inst_pwr);
  inst_power_svg->setScale(0.08);
  ui->power_avg_icon->scene()->addItem(avg_power_svg);
  ui->power_inst_icon->scene()->addItem(inst_power_svg);

  // Conenctors
  connect(m_serial, &QSerialPort::readyRead, this, &MainWindow::readData);
}

MainWindow::~MainWindow() {
  m_camera->stop();
  m_serial->close();
  delete ui;
}

void MainWindow::openSerialPort() {
  m_serial->setPortName("COM2");
  m_serial->setBaudRate(QSerialPort::Baud9600);
  m_serial->setDataBits(QSerialPort::Data8);
  m_serial->setParity(QSerialPort::NoParity);
  m_serial->setStopBits(QSerialPort::OneStop);
  m_serial->setFlowControl(QSerialPort::NoFlowControl);
  m_serial->open(QIODevice::ReadWrite);
}

void MainWindow::setStateOfCharge(short state_of_charge) {
  QPalette pal = QPalette();
  // Update battery SVG path and stroke colors
  if (state_of_charge > 80) {
    // Light green color
    ui->battery_icon->load(rezolve_link(Battery::FULL));
    pal.setColor(QPalette::Text, m_light_green);
  } else if (state_of_charge > 60) {
    // Light green color
    ui->battery_icon->load(rezolve_link(Battery::PARTIAL_80));
    pal.setColor(QPalette::Text, m_light_green);
  } else if (state_of_charge > 40) {
    // Yellow color
    ui->battery_icon->load(rezolve_link(Battery::PARTIAL_60));
    pal.setColor(QPalette::Text, m_yellow);
  } else if (state_of_charge > 20) {
    // Orange color
    ui->battery_icon->load(rezolve_link(Battery::PARTIAL_40));
    pal.setColor(QPalette::Text, m_orange);
  } else {
    // Red color
    ui->battery_icon->load(rezolve_link(Battery::EMPTY));
    pal.setColor(QPalette::Text, m_red);
  }
  // Set state of charge label
  QString number = QStringLiteral("%1\%").arg(state_of_charge, 3, 10, QLatin1Char('0'));
  ui->battery_label->setText(number);
  ui->battery_label->setPalette(pal);
}

void MainWindow::setTemperatures(short l_id, short l_temp, short h_id, short h_temp) {
    ui->low_temp_label_id->setText("##" + QString::number(l_id));
    ui->low_temp_label_value->setText(QString::number(l_temp) + "°C");
    ui->high_temp_label_id->setText("##" + QString::number(h_id));
    ui->high_temp_label_value->setText(QString::number(h_temp) + "°C");
}

void MainWindow::setVoltageSteps(short l_id, float l_volt, short h_id, float h_volt) {
    ui->low_volt_label_id->setText("##" + QString::number(l_id));
    ui->low_volt_label_value->setText(QString::number(l_volt));
    ui->high_volt_label_id->setText("##" + QString::number(h_id));
    ui->high_volt_label_value->setText(QString::number(h_volt));
}

void MainWindow::setSpeed(short speed) {
    ui->speed_label->setText(QString::number(speed) + " km/h");
}

void MainWindow::setSlowPowerConsumption(float power) {
    ui->power_avg_label->setText(QString::number(power));
}

void MainWindow::setFastPowerConsumption(float power) {
    ui->power_inst_label->setText(QString::number(power));
}

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
          uint16_t LowCellVoltage = ((uint16_t)LowCellVoltageMsb << 8) | LowCellVoltageLsb;
          uint16_t HighCellVoltage = ((uint16_t)HighCellVoltageMsb << 8) | HighCellVoltageLsb;
          byteCounter = 0;
          this->setVoltageSteps(LowCellVoltageId, LowCellVoltage, HighCellVoltageId, HighCellVoltage);
          this->setTemperatures(LowCellTempId, LowCellTemp, HighCellTempId,HighCellTemp);
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
