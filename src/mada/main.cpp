#include "mainwindow.h"

#include <QApplication>
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QThread>
#include <QTimer>
#include <QSerialPort>
#include <QSerialPortInfo>

static QString sensor = "";
static QList<QSerialPortInfo> portList;
static QSerialPortInfo sensorport;
static QSerialPort s_sensor;
class Sleeper : public QThread
{
public:
    static void usleep(unsigned long usecs){QThread::usleep(usecs);}
    static void msleep(unsigned long msecs){QThread::msleep(msecs);}
    static void sleep(unsigned long secs){QThread::sleep(secs);}
};

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    QQmlApplicationEngine engine;
    const QUrl url(QStringLiteral("qrc:/main.qml"));

    MainWindow w;
    QSize windowSize(1920,1080);
    w.resize(windowSize);
    w.setStyleSheet("QMainWindow {background: rgb(48,48,47);}");
    //w.setStyleSheet("QMainWindow {background: black;}");
    w.show();

    portList = QSerialPortInfo::availablePorts();

    int size = portList.size();
    QTextStream(stdout) <<portList[0].portName()<<"\n";
    QTextStream(stdout) <<portList[1].portName()<<"\n";
    QTextStream(stdout) <<portList[2].portName()<<"\n";

    if(portList[2].portName().toStdString()=="COM6")//&&portList[0].description().toStdString()=="USB-Serial Controller D")
    {
        sensor.append(portList[2].portName());
        sensorport = portList[2];
    }

    QTextStream(stdout) << sensor << "\n";
    QTextStream(stdout) << sensorport.manufacturer() << "\n";
    s_sensor.setPort(sensorport);
    QTextStream(stdout) << s_sensor.open(QIODevice::ReadOnly) << "\n";
    QTextStream(stdout) << s_sensor.portName()<< "\n";
    QTextStream(stdout) << s_sensor.parity() << "\n";
    QTextStream(stdout) << s_sensor.baudRate() << "\n";
    QTextStream(stdout) << s_sensor.dataBits() << "\n";
    QTextStream(stdout) << s_sensor.stopBits() << "\n";
    QTextStream(stdout) <<"open: "<< s_sensor.isOpen() << "\n";
    //QTextStream(stdout) << s_sensor.canReadLine() << "\n";*/

    char buf[1200];
    char nucleoData[203];
    QString buff;
    static QByteArray byteArray;
    uint8_t numRead = 0;
    uint8_t byteCounter =0;
    QElapsedTimer elapsed_timer;

    w.setSoC(0);
    w.setTemp(0);
    w.setVoltage(0);
    QApplication::processEvents();

    while(s_sensor.isOpen())
    {
        s_sensor.setReadBufferSize(200);

        elapsed_timer.start();
        numRead = s_sensor.read(buf,1);

        if((uint8_t)buf[0]==254)
        {
            nucleoData[0]=buf[0];
            buf[0]=0;
            numRead=s_sensor.read(buf,11);
            byteCounter = byteCounter + numRead+1;
            for (int i = 1; i <= numRead; i++) {
                nucleoData[byteCounter-numRead+i]=buf[i];
                buf[i] = 0;
            }

            if(byteCounter == 12  && (uint8_t)nucleoData[0]==254 && (uint8_t)nucleoData[11]==255 )//change to 202 for start and stop byte
            {
                for (int i = 0; i < byteCounter; i++) {
                    QTextStream(stdout) << (uint8_t)nucleoData[i]<<"  ";
                }
                Sleeper::sleep(1);
                w.setSoC(nucleoData[2]);
                w.setTemp(nucleoData[3]);
                w.setVoltage(nucleoData[4]);
                QApplication::processEvents();


                byteCounter =0;
            }
        }
        else if((uint8_t)buf[0]==252)
        {
            nucleoData[0]=buf[0];
            buf[0]=0;
            numRead=s_sensor.read(buf,2);
            byteCounter = byteCounter + numRead+1;
            for (int i = 1; i <= numRead; i++) {
                nucleoData[byteCounter-numRead+i]=buf[i];
                buf[i] = 0;

            }

            if(byteCounter == 3  && (uint8_t)nucleoData[0]==252 && (uint8_t)nucleoData[2]==253 )//change to 202 for start and stop byte
            {


                for (int i = 0; i < byteCounter; i++) {
                    QTextStream(stdout) << (uint8_t)nucleoData[i]<<"  ";


                }
                Sleeper::sleep(1);

                QString test = QString::number((uint8_t)nucleoData[1]);
                w.setSoC(nucleoData[2]);
                QApplication::processEvents();
                byteCounter =0;
            }
        }
    }
    return a.exec();
}
