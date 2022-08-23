import QtQuick 2.15
import QtQuick.Window 2.15
import com.alex.speedometer 1.0
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.1

Window {
    width: 640
    height: 480
    visible: true
    title: qsTr("Speedometer")
    color: "#000000"

    Speedometer
    {
        objectName: "speedoMeter"
        anchors.horizontalCenter: pafrent.horizontalCenter
        width: speedometerSize
        height: speedometerSize
        startAngle: startAngle
        alignAngle: alignAngle
        lowestRange: lowestRange
        highestRange: highestRange
        speed: speed
        arcWidth : arcWidth
        outerColor: outerColor
        innerColor: innerColor
        textColor: textColor
        backgroundColor: backgroundColor
    }
}
