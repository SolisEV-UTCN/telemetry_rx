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

QString rezolve_link(Battery);
#endif // HELPER_H
