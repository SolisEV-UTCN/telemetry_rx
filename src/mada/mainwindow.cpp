#include "mainwindow.h"
#include "./ui_mainwindow.h"

#include <QCamera>
#include <QMediaDevices>
#include <QMediaCaptureSession>
#include <QVideoWidget>
#include <QHBoxLayout>
#include <QPixmap>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
    ,m_serial(new QSerialPort(this))
{
    ui->setupUi(this);

    connect(m_serial, &QSerialPort::readyRead, this, &MainWindow::readData);

    videoWidget=new QVideoWidget;
    camera=new QCamera(QMediaDevices::defaultVideoInput());
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

    //ui->leftWidget.set
    ui->leftLabel->setPixmap(pix_turn_off);
    ui->rightLabel->setPixmap(QPixmap().fromImage(img_turn_right));
    ui->leftLabel->setFixedHeight(40);
    ui->rightLabel->setFixedHeight(40);
    ui->rightLabel->setStyleSheet("QLabel {background: rgb(48,48,47);}");
    ui->leftLabel->setStyleSheet("QLabel {background: rgb(48,48,47);}");


    //now setting up the SoC label
    QFont font = ui->soCLabel->font();
    font.setBold(true);
    font.setPointSize(16);
    ui->soCLabel->setFont(font);
    ui->soCLabel->setText("State of Charge");
    ui->soCLabel->setStyleSheet("QLabel{color: white;}");
    ui->progressBar->setMaximum(100);
    ui->progressBar->setMinimum(0);
    ui->progressBar->setAlignment(Qt::AlignCenter);
    //ui->progressBar->setStyleSheet("QLabel{color: white;}");


    //Module voltage/temperature groupBox
    QFont moduleDataFont = ui->moduleBox->font();
    moduleDataFont.setBold(true);
    moduleDataFont.setPointSize(12);
    ui->moduleBox->setFont(moduleDataFont);
    ui->moduleBox->setStyleSheet("QGroupBox{color: white}");


    //settsetTemphe hazard bar, with the hazard sign, headlights, and more

    QPixmap pix_panel("C:/Qt/Projects/turnLights/BottomPanel.png");
    QPixmap pix_hazard("C:/Qt/Projects/turnLights/hazard.png");
    QPixmap pix_alt_hazard("C:/Qt/Projects/turnLights/hazard2.png");
    QPixmap pix_headlight("C:/Qt/Projects/turnLights/headlight.png");
    ui->hazardBar->setFixedHeight(50);
    ui->hazardBar->setFixedWidth(1000);
    ui->hazardBar->setPixmap(pix_panel);

    //pix_hazard.
    ui->hazardLabel->setFixedHeight(40);
    ui->hazardLabel->setFixedWidth(40);
    int w = ui->hazardLabel->width();
    int h = ui->hazardLabel->height();
    ui->hazardLabel->setPixmap(pix_hazard.scaled(w, h, Qt::KeepAspectRatio));

    ui->headlightsLabel->setFixedHeight(40);
    ui->headlightsLabel->setFixedWidth(40);
    w = ui->headlightsLabel->width();
    h = ui->headlightsLabel->height();
    ui->headlightsLabel->setPixmap(pix_headlight.scaled(w, h, Qt::KeepAspectRatio));

    ui->mpptLabel->setText("MPPT\n OFF");
    QFont mpptFont = ui->mpptLabel->font();
    mpptFont.setBold(true);
    mpptFont.setPointSize(12);
    ui->mpptLabel->setStyleSheet("QLabel{color: black;}");
    ui->mpptLabel->setFont(mpptFont);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::modifyNumber(int num) {
    ui->voltageNum->display(num);
}

void MainWindow::openSerialPort()
{

    m_serial->setPortName("COM4");
    m_serial->setBaudRate(QSerialPort::Baud9600);
    m_serial->setDataBits(QSerialPort::Data8);
    m_serial->setParity(QSerialPort::NoParity);
    m_serial->setStopBits(QSerialPort::OneStop);
    m_serial->setFlowControl(QSerialPort::NoFlowControl);
    m_serial->open(QIODevice::ReadWrite);
}

void MainWindow::readData()
{
    const QByteArray data = m_serial->readAll();
    for(int i = 0; i < data.size(); i++)
    {
        unsigned int j = data.at(i);

      QTextStream(stdout) << (uint8_t)j<<"  ";
      //m_console->putData(j);
    }
QTextStream(stdout) <<" \n ";
}

void MainWindow::turn(bool direction) {

    QPixmap pix_turn_on("C:/Qt/Projects/turnLights/Icon_TurnLeft_ON.png");

    QImage img_turn_right = pix_turn_on.toImage().mirrored(true, true);

    this->noTurn();

    //turn left
    if (direction == false)
        ui->leftLabel->setPixmap(pix_turn_on);

    //turn right
    if (direction == true)
        ui->rightLabel->setPixmap(QPixmap().fromImage(img_turn_right));
}

void MainWindow::noTurn(){
    QPixmap pix_turn_off("C:/Qt/Projects/turnLights/Icon_TurnLeft_OFF.png");

    QImage img_turn_right = pix_turn_off.toImage().mirrored(true, true);

    //ui->leftWidget.set
    ui->leftLabel->setPixmap(pix_turn_off);
    ui->rightLabel->setPixmap(QPixmap().fromImage(img_turn_right));
    ui->leftLabel->setFixedHeight(40);
    ui->rightLabel->setFixedHeight(40);
}

void MainWindow::setSoC(int soC){
    if (soC >= 0 && soC <= 100) {

        ui->progressBar->setValue(soC);

        QPalette pal = palette();
        pal.setColor(QPalette::Base, Qt::green);

        if (soC > 70)
            ui->progressBar->setStyleSheet("QProgressBar::chunk {background:  rgb(0,255,0)}");//pal.setColor(QPalette::Base, Qt::green);
            else if (soC > 30)
                ui->progressBar->setStyleSheet("QProgressBar::chunk {background:  rgb(255,255,0)}");
            else //(soC < 30)
                ui->progressBar->setStyleSheet("QProgressBar::chunk {background:  rgb(255,0,0)}");

        ui->progressBar->setPalette(pal);
    }
}

void MainWindow::headlightsOn() {
    ui->headlightsLabel->setVisible(true);
}

void MainWindow::headlightsOff() {
    ui->headlightsLabel->setVisible(false);
}

void MainWindow::hazardOn() {
    ui->hazardLabel->setVisible(true);
}

void MainWindow::hazardOff() {
    ui->hazardLabel->setVisible(false);
}

void MainWindow::setTemp(int temp) {
    ui->tempNum->display(temp);
}

void MainWindow::setVoltage(int voltage) {
    ui->voltageNum->display(voltage);
}

void MainWindow::setMPPT(bool isOn) {

    //QFont mpptFont = ui->mpptLabel->font();

    if (isOn) {
        ui->mpptLabel->setText("MPPT\n ON");
        ui->mpptLabel->setStyleSheet("QLabel{color: rgb(0,130,0);}");
    }

    else {
        ui->mpptLabel->setText("MPPT\n OFF");
        ui->mpptLabel->setStyleSheet("QLabel{color: black;}");
    }
}
