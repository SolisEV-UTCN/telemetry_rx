#include "helper.h"


QString rezolve_link(Battery state) {
    switch(state) {
        case FULL:
            return QString(":/resource/battery_100.svg");
        case PARTIAL_80:
            return QString(":/resource/battery_080.svg");
        case PARTIAL_60:
            return QString(":/resource/battery_060.svg");
        case PARTIAL_40:
            return QString(":/resource/battery_040.svg");
        case EMPTY:
        default:
            return QString(":/resource/battery_020.svg");
    }
}
