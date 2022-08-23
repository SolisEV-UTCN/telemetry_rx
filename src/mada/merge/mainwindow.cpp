#include "mainwindow.h"
#include "./ui_mainwindow.h"
#include "qthread.h"

#include <QCamera>
#include <QHBoxLayout>
#include <QMediaCaptureSession>
#include <QMediaDevices>
#include <QPixmap>
#include <QVideoWidget>

class Sleeper : public QThread {
public:
  static void usleep(unsigned long usecs) { QThread::usleep(usecs); }
  static void msleep(unsigned long msecs) { QThread::msleep(msecs); }
  static void sleep(unsigned long secs) { QThread::sleep(secs); }
};

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent), ui(new Ui::MainWindow),
      m_serial(new QSerialPort(this)) {
  ui->setupUi(this);

  connect(m_serial, &QSerialPort::readyRead, this, &MainWindow::readData);

  videoWidget = new QVideoWidget;
  camera = new QCamera(QMediaDevices::defaultVideoInput());
  camera->start();
  mediaCaptureSession = new QMediaCaptureSession;
  mediaCaptureSession->setCamera(camera);

  mediaCaptureSession->setVideoOutput(videoWidget);

  QHBoxLayout layout;
  layout.setAlignment(Qt::AlignCenter);
  layout.addWidget(videoWidget);

  ui->scrollArea->setLayout(&layout);

  QPixmap pix_turn_on("C:/Qt/Projects/turnLights/Icon_TurnLeft_ON.png");
  QPixmap pix_turn_off("C:/Qt/Projects/turnLights/Icon_TurnLeft_OFF.png");

  QImage img_turn_right = pix_turn_off.toImage().mirrored(true, true);

  // ui->leftWidget.set
  ui->leftLabel->setPixmap(pix_turn_off);
  ui->rightLabel->setPixmap(QPixmap().fromImage(img_turn_right));
  ui->leftLabel->setFixedHeight(40);
  ui->rightLabel->setFixedHeight(40);
  ui->rightLabel->setStyleSheet("QLabel {background: rgb(48,48,47);}");
  ui->leftLabel->setStyleSheet("QLabel {background: rgb(48,48,47);}");

  // now setting up the SoC label
  QFont font = ui->soCLabel->font();
  font.setBold(true);
  font.setPointSize(16);
  ui->soCLabel->setFont(font);
  ui->soCLabel->setText("State of Charge");
  ui->soCLabel->setStyleSheet("QLabel{color: white;}");
  ui->progressBar->setMaximum(100);
  ui->progressBar->setMinimum(0);
  ui->progressBar->setAlignment(Qt::AlignCenter);
  // ui->progressBar->setStyleSheet("QLabel{color: white;}");

  // Module voltage/temperature groupBox
  QFont moduleDataFont = ui->moduleBox->font();
  moduleDataFont.setBold(true);
  moduleDataFont.setPointSize(12);
  ui->moduleBox->setFont(moduleDataFont);
  ui->moduleBox->setStyleSheet("QGroupBox{color: white}");

  // settsetTemphe hazard bar, with the hazard sign, headlights, and more

  QPixmap pix_panel("C:/Qt/Projects/turnLights/BottomPanel.png");
  QPixmap pix_hazard("C:/Qt/Projects/turnLights/hazard.png");
  QPixmap pix_alt_hazard("C:/Qt/Projects/turnLights/hazard2.png");
  QPixmap pix_headlight("C:/Qt/Projects/turnLights/headlight.png");
  ui->hazardBar->setFixedHeight(50);
  ui->hazardBar->setFixedWidth(1000);
  ui->hazardBar->setPixmap(pix_panel);

  // pix_hazard.
  ui->hazardLabel->setFixedHeight(40);
  ui->hazardLabel->setFixedWidth(40);
  int w = ui->hazardLabel->width();
  int h = ui->hazardLabel->height();
  ui->hazardLabel->setPixmap(pix_hazard.scaled(w, h, Qt::KeepAspectRatio));

  ui->headlightsLabel->setFixedHeight(40);
  ui->headlightsLabel->setFixedWidth(40);
  w = ui->headlightsLabel->width();
  h = ui->headlightsLabel->height();
  ui->headlightsLabel->setPixmap(
      pix_headlight.scaled(w, h, Qt::KeepAspectRatio));

  ui->mpptLabel->setText("MPPT\n OFF");
  QFont mpptFont = ui->mpptLabel->font();
  mpptFont.setBold(true);
  mpptFont.setPointSize(12);
  ui->mpptLabel->setStyleSheet("QLabel{color: black;}");
  ui->mpptLabel->setFont(mpptFont);
}

MainWindow::~MainWindow() { delete ui; }

void MainWindow::modifyNumber(int num) { ui->voltageNum->display(num); }

void MainWindow::openSerialPort() {

  m_serial->setPortName("COM4");
  m_serial->setBaudRate(QSerialPort::Baud9600);
  m_serial->setDataBits(QSerialPort::Data8);
  m_serial->setParity(QSerialPort::NoParity);
  m_serial->setStopBits(QSerialPort::OneStop);
  m_serial->setFlowControl(QSerialPort::NoFlowControl);
  m_serial->open(QIODevice::ReadWrite);
}

void MainWindow::turn(bool direction) {

  QPixmap pix_turn_on("C:/Qt/Projects/turnLights/Icon_TurnLeft_ON.png");

  QImage img_turn_right = pix_turn_on.toImage().mirrored(true, true);

  this->noTurn();

  // turn left
  if (direction == false)
    ui->leftLabel->setPixmap(pix_turn_on);

  // turn right
  if (direction == true)
    ui->rightLabel->setPixmap(QPixmap().fromImage(img_turn_right));
}

void MainWindow::noTurn() {
  QPixmap pix_turn_off("C:/Qt/Projects/turnLights/Icon_TurnLeft_OFF.png");

  QImage img_turn_right = pix_turn_off.toImage().mirrored(true, true);

  // ui->leftWidget.set
  ui->leftLabel->setPixmap(pix_turn_off);
  ui->rightLabel->setPixmap(QPixmap().fromImage(img_turn_right));
  ui->leftLabel->setFixedHeight(40);
  ui->rightLabel->setFixedHeight(40);
}

void MainWindow::setSoC(int soC) {
  if (soC >= 0 && soC <= 100) {

    ui->progressBar->setValue(soC);

    QPalette pal = palette();
    pal.setColor(QPalette::Base, Qt::green);

    if (soC > 70)
      ui->progressBar->setStyleSheet("QProgressBar::chunk {background:  "
                                     "rgb(0,255,0)}"); // pal.setColor(QPalette::Base,
                                                       // Qt::green);
    else if (soC > 30)
      ui->progressBar->setStyleSheet(
          "QProgressBar::chunk {background:  rgb(255,255,0)}");
    else //(soC < 30)
      ui->progressBar->setStyleSheet(
          "QProgressBar::chunk {background:  rgb(255,0,0)}");

    ui->progressBar->setPalette(pal);
  }
}

void MainWindow::headlightsOn() { ui->headlightsLabel->setVisible(true); }

void MainWindow::headlightsOff() { ui->headlightsLabel->setVisible(false); }

void MainWindow::hazardOn() { ui->hazardLabel->setVisible(true); }

void MainWindow::hazardOff() { ui->hazardLabel->setVisible(false); }

void MainWindow::setTemp(int temp) { ui->tempNum->display(temp); }

void MainWindow::setVoltage(int voltage) { ui->voltageNum->display(voltage); }

void MainWindow::setMPPT(bool isOn) {

  // QFont mpptFont = ui->mpptLabel->font();

  if (isOn) {
    ui->mpptLabel->setText("MPPT\n ON");
    ui->mpptLabel->setStyleSheet("QLabel{color: rgb(0,130,0);}");
  }

  else {
    ui->mpptLabel->setText("MPPT\n OFF");
    ui->mpptLabel->setStyleSheet("QLabel{color: black;}");
  }
}

void MainWindow::readData() {
  char nucleoData[203];
  int byteCounter = 0;
  QByteArray data = m_serial->read(1);
  QByteArray data1 = data;

  if (data1.size() > 0) {
    unsigned int j = data1.at(0);

    if ((uint8_t)j == 254) {

      data = m_serial->read(11);
      data1 = data;
      if (data1.size() > 0) {
        byteCounter = data1.size() + byteCounter + 1;
        for (int i = 0; i < data1.size(); i++) {
          nucleoData[byteCounter - data1.size() + 1] = data1.at(i);
        }

        if (byteCounter == 12 && (uint8_t)j == 254 &&
            (uint8_t)data1.at(10) == 255) {
          QTextStream(stdout) << (uint8_t)j << "  ";
          nucleoData[0] = (uint8_t)j;
          for (int i = 0; i < byteCounter - 1; i++) {

            nucleoData[i] = (uint8_t)data1.at(i);
            QTextStream(stdout) << (uint8_t)nucleoData[i] << "  ";
          }
          QTextStream(stdout) << "\n";

          byteCounter = 0;
          setTemp((uint8_t)nucleoData[1]);
        }
      }

    } else if ((uint8_t)j == 252) {

      nucleoData[0] = j;
      data = m_serial->read(2);
      data1 = data;
      if (data1.size() > 0) {
        byteCounter = data1.size() + byteCounter + 1;

        for (int i = 0; i < data1.size(); i++) {
          nucleoData[byteCounter - data1.size() + 1] = data1.at(i);
        }

        if (byteCounter == 3 && (uint8_t)j == 252 &&
            (uint8_t)data1.at(1) == 253)
          QTextStream(stdout) << (uint8_t)j << "  ";
        nucleoData[0] = (uint8_t)j;
        for (int i = 0; i < byteCounter - 1; i++) {

          nucleoData[i] = (uint8_t)data1.at(i);
          QTextStream(stdout) << (uint8_t)nucleoData[i] << "  ";
        }
        QTextStream(stdout) << "\n";

        byteCounter = 0;
        setTemp((uint8_t)nucleoData[1]);
      }
    }
  }
}
