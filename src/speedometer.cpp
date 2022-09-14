#include "speedometer.h"
#include <QPainter>


Speedometer::Speedometer(QQuickItem *parent)
    :QQuickPaintedItem(parent),
      m_SpeedometerSize(500),
      m_startAngle(240),
      m_alignAngle(220), // should be 360 - 2*m_startAngle
      m_lowestRange(0),
      m_highestRange(4000), // max analog val from adc
      m_speed(2430),
      m_arcWidth(10),
      m_outerColor(QColor(128,255,0)),
      m_innerColor(QColor(51,88,155,80)),
      m_textColor(QColor(255,255,255)),
      m_backgroundColor(Qt::transparent)
{}

void Speedometer::paint(QPainter *painter) {
    QRectF rect = this->boundingRect();
    painter->setRenderHint(QPainter::Antialiasing);
    QPen pen = painter->pen();
    pen.setCapStyle(Qt::FlatCap);

    double startAngle;
    double spanAngle;

    startAngle = m_startAngle - 40;
    spanAngle = 0 - m_alignAngle;

    //all arc
    painter->save();
    pen.setWidth(m_arcWidth);
    pen.setColor(m_innerColor);
    painter->setPen(pen);
    painter->drawArc(rect.adjusted(m_arcWidth, m_arcWidth, -m_arcWidth, -m_arcWidth), startAngle * 16, spanAngle * 16);
    painter->restore();

    //inner pie
    int pieSize = m_SpeedometerSize/5;
    painter->save();
    pen.setWidth(m_arcWidth / 2);
    pen.setColor(m_outerColor);
    painter->setBrush(m_innerColor);
    painter->setPen(pen);
    painter->drawPie(rect.adjusted(pieSize, pieSize, -pieSize, -pieSize), startAngle * 16, spanAngle  * 16);
    painter->restore();

    //text showing the value
    painter->save();
    QFont font("Helvetica", 52, QFont::Bold);
    painter->setFont(font);
    pen.setColor(m_textColor);
    painter->setPen(pen);
    painter->drawText(rect.adjusted(m_SpeedometerSize / 30, m_SpeedometerSize / 30, -m_SpeedometerSize / 30, -m_SpeedometerSize / 4),
                      Qt::AlignCenter, QString::number((m_speed / 40), 'f', 1));
    painter->restore();

    //active process
    painter->save();
    pen.setWidth(m_arcWidth);
    pen.setColor(m_outerColor);
    qreal valueToAngle = ((m_speed - m_lowestRange) / (m_highestRange - m_lowestRange)) * spanAngle;
    painter->setPen(pen);
    painter->drawArc(rect.adjusted(m_arcWidth, m_arcWidth, m_arcWidth, m_arcWidth), startAngle * 16, valueToAngle  * 16);
    painter->restore();
}

qreal Speedometer::getSpeedometerSize() {
    return m_SpeedometerSize;
}

void Speedometer::setSpeedometerSize(qreal size) {
    if (m_SpeedometerSize == size)
        return;
    m_SpeedometerSize = size;
    emit speedometerSizeChanged();
}

qreal Speedometer::getStartAngle() {
    return m_startAngle;
}

void Speedometer::setStartAngle(qreal angle) {
    if (m_startAngle == angle)
        return;
    m_startAngle = angle;
    emit startAngleChanged();
}

qreal Speedometer::getAlignAngle() {
    return m_alignAngle;
}

void Speedometer::setAlignAngle(qreal angle) {
    if (m_alignAngle == angle)
        return;
    m_alignAngle = angle;
    emit alignAngleChanged();
}

qreal Speedometer::getLowestRange() {
    return m_lowestRange;
}

void Speedometer::setLowestRange(qreal range) {
    if (m_lowestRange == range)
        return;
    m_lowestRange = range;
    emit lowestRangeChanged();
}

qreal Speedometer::getHighestRange() {
    return m_highestRange;
}

void Speedometer::setHighestRange(qreal range) {
    if (m_highestRange == range)
        return;
    m_highestRange = range;
    emit highestRangeChanged();
}

qreal Speedometer::getSpeed() {
    return m_speed;
}

void Speedometer::setSpeed(qreal speed) {
    if (m_speed == speed)
        return;
    m_speed = speed;
    emit speedChanged();
}


int Speedometer::getArcWidth() {
    return m_arcWidth;
}

void Speedometer::setArcWidth(int arcW) {
    if (m_arcWidth == arcW)
        return;
    m_arcWidth = arcW;
    emit arcWidthChanged();
}

QColor Speedometer::getOuterColor() {
    return m_outerColor;
}

void Speedometer::setOuterColor(QColor color) {
    if (m_outerColor == color)
        return;
    m_outerColor = color;
    emit outerColorChanged();
}

QColor Speedometer::getInnerColor() {
    return m_innerColor;
}

void Speedometer::setInnerColor(QColor color) {
    if (m_innerColor == color)
        return;
    m_innerColor = color;
    emit innerColorChanged();
}

QColor Speedometer::getTextColor() {
    return m_textColor;
}

void Speedometer::setTextColor(QColor color) {
    if (m_textColor == color)
        return;
    m_textColor = color;
    emit textColorChanged();
}

QColor Speedometer::getBackgroundColor() {
    return m_backgroundColor;
}

void Speedometer::setBackgroundColor(QColor color) {
    if (m_backgroundColor == color)
        return;
    m_backgroundColor = color;
    emit backgroundColorChanged();
}
