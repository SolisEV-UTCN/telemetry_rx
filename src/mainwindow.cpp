#include "mainwindow.h"
#include "./ui_mainwindow.h"


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
  connect(m_serial, &QSerialPort::readyRead, this, &MainWindow::readSerial);
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
  m_serial->setParity(QSerialPort::EvenParity);
  m_serial->setStopBits(QSerialPort::OneStop);
  m_serial->setFlowControl(QSerialPort::NoFlowControl);
  m_serial->open(QIODevice::ReadOnly);
}

void MainWindow::setStateOfCharge(uint8_t state_of_charge) {
  // Normalize
  float charge = (float)state_of_charge / 2;
  QPalette pal = QPalette();
  // Update battery SVG path and stroke colors
  if (charge > 80.0f) {
    // Light green color
    ui->battery_icon->load(rezolve_link(Battery::FULL));
    pal.setColor(QPalette::Text, m_light_green);
  } else if (charge > 60.0f) {
    // Light green color
    ui->battery_icon->load(rezolve_link(Battery::PARTIAL_80));
    pal.setColor(QPalette::Text, m_light_green);
  } else if (charge > 40.0f) {
    // Yellow color
    ui->battery_icon->load(rezolve_link(Battery::PARTIAL_60));
    pal.setColor(QPalette::Text, m_yellow);
  } else if (charge > 20.0f) {
    // Orange color
    ui->battery_icon->load(rezolve_link(Battery::PARTIAL_40));
    pal.setColor(QPalette::Text, m_orange);
  } else {
    // Red color
    ui->battery_icon->load(rezolve_link(Battery::EMPTY));
    pal.setColor(QPalette::Text, m_red);
  }
  // Set state of charge label
  int num = qFloor(charge);
  QString text = QStringLiteral("%1").arg(num, 3, 10, QLatin1Char('0'));
  ui->battery_label->setText(text + "%");
  ui->battery_label->setPalette(pal);
}

void MainWindow::setTemperatures(uint8_t l_id, uint8_t l_temp, uint8_t h_id, uint8_t h_temp) {
    ui->low_temp_label_id->setText("##" + QString::number((int)l_id));
    ui->low_temp_label_value->setText(QString::number((int)l_temp) + "°C");
    ui->high_temp_label_id->setText("##" + QString::number((int)h_id));
    ui->high_temp_label_value->setText(QString::number((int)h_temp) + "°C");
}

void MainWindow::setVoltageSteps(uint8_t l_id, uint16_t l_volt, uint8_t h_id, uint16_t h_volt) {
    // Normalize
    float voltage = (float)l_volt * 0.0001f;
    ui->low_volt_label_id->setText("##" + QString::number((int)l_id));
    ui->low_volt_label_value->setText(QString::number(voltage, 'f', 2));
    // Normalize
    voltage = (float)h_volt * 0.0001f;
    ui->high_volt_label_id->setText("##" + QString::number(h_id));
    ui->high_volt_label_value->setText(QString::number(voltage, 'f', 2));
}

void MainWindow::setSpeed(uint8_t speed) {
    ui->speed_label->setText(QString::number(speed) + " km/h");
}

void MainWindow::setSlowPowerConsumption(float power) {
    ui->power_avg_label->setText(QString::number(power, 'f', 2));
}

void MainWindow::setFastPowerConsumption(float power) {
    ui->power_inst_label->setText(QString::number(power, 'f', 2));
}

void MainWindow::updateLabels(const SerialBuffer &data) {
    this->setVoltageSteps(data.LowCellVoltageId, data.LowCellVoltage, data.HighCellVoltageId, data.HighCellVoltage);
    this->setTemperatures(data.LowCellTempId, data.LowCellTemp, data.HighCellTempId, data.HighCellTemp);
    this->setStateOfCharge(data.PackSOC);
    this->setSpeed(data.Speed);
    float power = (float)data.PackCurrent * 0.0001f * (float)data.PackVoltage * 0.0001f;
    this->setSlowPowerConsumption(power);
    power_average->append(power);
    if (power_average->size() == 3000) {
        float sum = 0;
        for (size_t i = 0; i < 3000; ++i) {
            sum += power_average->at(i);
            power = sum / 3000;
            this->setFastPowerConsumption(power);
        }
    }
}

void MainWindow::readSerial() {
  const QByteArray serial_prefix = QByteArray::fromHex("FFFF");
  QByteArray serial_read = m_serial->read(sizeof(SerialBuffer) + 1);
  QString print = (serial_read.startsWith(serial_prefix)) ? "true" : "false";
  QTextStream(stdout) << print;
  if (!serial_read.isEmpty() && serial_read.startsWith(serial_prefix)) {
      SerialBuffer data;
      data.HighTemp = (uint8_t)serial_read[2];
      data.InternalTemp = (uint8_t)serial_read[3];
      data.LowCellVoltage = ((uint16_t)serial_read[4] << 8) | serial_read[5];
      data.HighCellVoltage = ((uint16_t)serial_read[6] << 8) | serial_read[7];
      data.LowCellVoltageId = (uint8_t)serial_read[8];
      data.HighCellVoltageId = (uint8_t)serial_read[9];
      data.PackSOC = (uint8_t)serial_read[10];
      data.RelayState = (uint8_t)serial_read[11];
      data.PackAvgTemp = (uint8_t)serial_read[12];
      data.LowCellTemp = (uint8_t)serial_read[13];
      data.HighCellTemp = (uint8_t)serial_read[14];
      data.LowCellTempId = (uint8_t)serial_read[15];
      data.HighCellTempId = (uint8_t)serial_read[16];
      data.PackCurrent = ((uint16_t)serial_read[17] << 8) | serial_read[18];
      data.PackVoltage = ((uint16_t)serial_read[19] << 8) | serial_read[20];
      data.FrameCount = (uint8_t)serial_read[21];
      data.Speed = (uint8_t)serial_read[22];
      this->updateLabels(data);
  }
}
