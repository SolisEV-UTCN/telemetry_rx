#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

#include <QWidget>
#include <QCamera>
#include <QMediaDevices>
#include <QMediaCaptureSession>
#include <QVideoWidget>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
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

private:
    Ui::MainWindow *ui;
    QCamera *camera;
    QMediaCaptureSession *mediaCaptureSession;
    QVideoWidget *videoWidget;


};
#endif // MAINWINDOW_H
