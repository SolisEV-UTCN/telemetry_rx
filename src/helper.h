#ifndef HELPER_H
#define HELPER_H

#include <QString>

enum Battery {
    FULL,
    PARTIAL_80,
    PARTIAL_60,
    PARTIAL_40,
    EMPTY
};

struct SerialBuffer {
    uint8_t HighTemp;
    uint8_t InternalTemp;
    uint16_t LowCellVoltage;
    uint16_t HighCellVoltage;
    uint8_t LowCellVoltageId;
    uint8_t HighCellVoltageId;
    uint8_t PackSOC;
    uint8_t RelayState;
    uint8_t PackAvgTemp;
    uint8_t LowCellTemp;
    uint8_t HighCellTemp;
    uint8_t LowCellTempId;
    uint8_t HighCellTempId;
    uint16_t PackCurrent;
    uint16_t PackVoltage;
    uint8_t FrameCount;
    uint8_t Speed;
};

QString rezolve_link(Battery);
#endif // HELPER_H
