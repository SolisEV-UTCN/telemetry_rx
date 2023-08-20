import logging
import struct
from typing import Tuple

import serial

from classes.message import Message
from classes.parser import Parser
from helpers.patterns import Adapter, State


COM_PORT = "/dev/ttyUSB0"

__slots__ = "device"
class UsbAdapter(Adapter):
    def init_device(self) -> State:
        try:
            self.device = serial.Serial(
                port=COM_PORT,
                baudrate=57600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )
            logging.info(f"Established connection on {self.device.port}.")
            logging.debug(f"Device information:\n\t- baudrate: {self.device.baudrate}\n\t- parity: {self.device.parity}\n\t- stopbits: {self.device.stopbits}\n\t- bytesize: {self.device.bytesize}")
            return State.COMM
        except serial.PortNotOpenError:
            logging.error("Port {COM_PORT} is already in use.")
            return State.CLOSE
        except serial.SerialException as e:
            logging.error("Could not establish serial communication. To see more info, enable debug flag.")
            logging.debug(e)
            return State.CLOSE
    
    def deinit_device(self):
        self.device.close()

    def read_data(self) -> Tuple[State, Message | None]:
        """Returns list of points"""
        # Check if input buffer is empty
        if self.device.in_waiting is 0:
            return State.COMM, None
        
        # Check if start byte is padded correctly
        start_byte = self.device.read()
        if start_byte != b"\xfe":
            return State.COMM, None

        payload = self.device.read(10)

        # Check if stop byte is padded correctly
        stop_byte = self.device.read()
        if stop_byte != b"\x7f":
            return State.COMM, None

        logging.debug(f"Read {payload.hex(' ').upper()}, {self.device.in_waiting} bytes remain in input buffer.")
        
        # Cast STD CAN ID from first 2 bytes
        can_id = (payload[0] << 8) + payload[1]
        message = self.parse_data(can_id, payload[2:])

        return State.COMM, message
    
    def parse_data(self, id: int, byte_stream: bytes) -> Message:
        # Get message formatter
        if id in Parser.messages:
            message = Parser.messages[id]
        else:
            logging.warn(f"Received unknown message with {hex(id)} ID.")
            return Message(f"{hex(id)}")

        message.data.clear()
        values = struct.unpack(message.fmt, byte_stream)

        # Iterate over unpacked bytes and set message fields
        for field_name, data in zip(message.field_names, values):
            cast = field_name.split(",")
            name = cast[0]
            factor = 1
            offset = 0
            # If JSON contains offset or factor, apply them
            if len(cast) > 1:
                factor = float(cast[1])
            if len(cast) > 2:
                offset = int(cast[2])
            message.append(name, data, offset, factor)
        
        return message
