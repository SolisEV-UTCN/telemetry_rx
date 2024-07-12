import random
import sched
import serial


def slow_frame(ser: serial.Serial):
    value = random.randint(17, 99)
    msg = bytearray(b"\xfe")
    msg.append(value)  # high temp
    msg.append(value)  # internal temp
    msg.append(value)  # LSB low voltage
    msg.append(value)  # MSB low voltage
    msg.append(value)  # LSB high voltage
    msg.append(value)  # MSB high voltage
    msg.append(value)  # low voltage id
    msg.append(value)  # high voltage id
    msg.append(value)  # pack SoC
    msg.append(value)  # relay state
    msg.append(value)  # pack avg temp
    msg.append(value)  # low temp
    msg.append(value)  # high temp
    msg.append(value)  # low temp id
    msg.append(value)  # high temp id
    msg.append(255)  # padding + suffix
    ser.write(msg)


def fast_frame(ser: serial.Serial):
    value = random.randint(17, 99)
    msg = bytearray()
    msg.append(255)
    msg.append(255)
    msg.append(value)  # high temp
    msg.append(value)  # internal temp
    msg.append(value)  # LSB low voltage
    msg.append(value)  # MSB low voltage
    msg.append(value)  # LSB high voltage
    msg.append(value)  # MSB high voltage
    msg.append(value)  # low voltage id
    msg.append(value)  # high voltage id
    msg.append(value)  # pack SoC
    msg.append(value)  # relay state
    msg.append(value)  # pack avg temp
    msg.append(value)  # low temp
    msg.append(value)  # high temp
    msg.append(value)  # low temp id
    msg.append(value)  # high temp id
    msg.append(value)  # LSB pack curr
    msg.append(value)  # MSB pack curr
    msg.append(value)  # LSB pack volt
    msg.append(value)  # MSB pack volt
    msg.append(value)  # frame count
    msg.append(value)  # speed
    ser.write(msg)
    print(value)


if __name__ == "__main__":
    ser = serial.Serial("COM1", baudrate=9600, timeout=0, parity=serial.PARITY_EVEN, rtscts=1)
    sch = sched.scheduler()
    sch.enter(5, 1, fast_frame, argument=(ser,))
    sch.enter(10, 1, fast_frame, argument=(ser,))
    sch.enter(15, 1, fast_frame, argument=(ser,))
    sch.enter(20, 1, fast_frame, argument=(ser,))
    sch.enter(25, 1, fast_frame, argument=(ser,))
    sch.enter(30, 1, fast_frame, argument=(ser,))
    sch.enter(35, 1, fast_frame, argument=(ser,))
    sch.enter(40, 1, fast_frame, argument=(ser,))
    sch.run()
