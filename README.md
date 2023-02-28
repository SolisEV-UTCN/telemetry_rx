# Telemetry system

**Telemetry system** is divided into two variants: _Plug&Play_ and _xBee_.

### Plug&Play

**Plug&Play** is designed using third-party components. Its main goal is to
quickly develop entire telemetry system. List of third-party components:

- [Kvaser Ethercan HS](https://www.kvaser.com/product/kvaser-ethercan-hs/#/!)
- [Loco5AC](https://dl.ui.com/qsg/Loco5AC/Loco5AC_EN.html)

Substantial drawback of this system is big power consumption (~7W). Once _xBee_
variant is complete this _Plug&Play_ could be used as a redundancy system.

### xBee

**xBee** is a student made telemetry variant. It is designed to use the least
possible amount of power, whilst satisfying regulations enforced by tournament
organizers. List of components:

- [STM32F103](https://www.st.com/en/microcontrollers-microprocessors/stm32f103.html)

This variant has a limited bandwidth, but it still satisfies current telemetry
system needs.
