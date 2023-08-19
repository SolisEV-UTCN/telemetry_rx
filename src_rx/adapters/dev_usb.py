import logging
import struct
from typing import Iterable

import serial

from classes.message import Message
from classes.parser import Parser
from helpers.patterns import Adapter, State



class UsbAdapter(Adapter):
    def __init__(self):
        self.device = serial.Serial()

    def init_device(self) -> State:
        try:
            self.device = serial.Serial(
                port="/dev/ttyUSB0",
                baudrate=57600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )
        except serial.PortNotOpenError:
            logging.error("Port is in use!")
            return State.CLOSE
        except serial.SerialException:
            logging.warn("Something went wrong, reconnecting...")
            return State.INIT
        logging.debug(f"Device data:\n{self.device}")
        return State.COMM
    
    def deinit_device(self):
        self.device.close()

    def read_data(self) -> Iterable[Message]:
        """Returns list of points"""
        # Read serial stream
        while self.device.in_waiting != 0:
            payload = self.device.read()

            if payload != b"\xfe":
                continue

            payload = self.device.read(10)
            termination = self.device.read()

            if termination != b"\x7f":
                continue

            logging.debug(f"Input buffer remaining bytes {self.device.in_waiting}")
            
            # Cast CAN Id as 16bit value
            can_id = (payload[0] << 8) + payload[1]

            message = self.parse_data(can_id, payload[2:])

            yield message
    
    def parse_data(self, id: int, byte_stream: bytes) -> Message:
        # Map input to JSON
        if id in Parser().messages:
            message = Parser().messages[id]
        else:
            logging.warn(f"Received unknown message with {hex(id)} ID")
            return Message(f"UNKNOWN_{hex(id)}")

        message.data.clear()
        values = struct.unpack(message.fmt, byte_stream)

        for field_name, data in zip(message.field_names, values):
            cast = field_name.split(",")
            name = cast[0]
            factor = 1
            offset = 0
            if len(cast) > 1:
                factor = float(cast[1])
            if len(cast) > 2:
                offset = int(cast[2])
            message.append(name, data, offset, factor)
        
        return message
