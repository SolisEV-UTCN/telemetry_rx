import logging
import struct
from collections.abc import Iterator

import serial
from influxdb_client import Point

from telemetry_rx.adapters import Adapter
from telemetry_rx.classes import AppState


MESSAGE_LEN = 16
MESSAGE_CNT = 20
COM_PORT = "/dev/ttyUSB0"

__slots__ = "device"


class UsbAdapter(Adapter):
    def __init__(self):
        super().__init__()

    def init_device(self) -> AppState:
        try:
            self.device = serial.Serial(
                port=COM_PORT,
                baudrate=230400,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_ONE,
                timeout=None,
            )
            logging.info(f"Established connection on {self.device.port}.")
            logging.debug(
                "Device information:\n"
                f"\t- baudrate: {self.device.baudrate}\n"
                f"\t- parity: {self.device.parity}\n"
                f"\t- stopbits: {self.device.stopbits}\n"
                f"\t- bytesize: {self.device.bytesize}"
            )
            return AppState.COMM
        except serial.PortNotOpenError:
            logging.error("Port {COM_PORT} is already in use.")
            return AppState.STOP
        except serial.SerialException as e:
            logging.error("Could not establish serial communication. To see more info, enable debug flag.")
            logging.debug(e)
            return AppState.STOP

    def deinit_device(self) -> None:
        self.device.close()

    def read_data(self) -> Iterator[Point]:
        """Reads serial input and converts bytestream to a Point."""
        byte_size = MESSAGE_LEN * MESSAGE_CNT
        while True:
            # Read UART bytestream
            logging.debug(f"{self.device.in_waiting} bytes are in input buffer.")
            if self.device.in_waiting < byte_size:
                logging.debug("Input buffer was reset.")
                self.device.reset_input_buffer()

            payload = self.device.read(MESSAGE_LEN * MESSAGE_CNT)

            # Validate payload length
            if len(payload) != MESSAGE_LEN * MESSAGE_CNT:
                logging.warn("Received partial message!")
                continue

            for i in range(MESSAGE_CNT):
                frame_id, data_h, data_l, crc = self.process_bytes(payload, i * MESSAGE_LEN)

                # Validate CRC-32 MPEG-2
                # STM32 algorithm reverses byte order for uint32_t before calculating CRC
                if not self.validate_crc(crc, data_h[::-1] + data_l[::-1]):
                    continue

                # Decode data
                point = self.parse_data(frame_id, data_h + data_l)
                if point is not None:
                    yield point

    def process_bytes(self, data: bytes, offset: int) -> tuple[int, bytes, bytes, int]:
        r"""Incoming serial data is expected to be of following structure:
        Byte[00] = Padding byte (0xFE)
        Byte[01] = CAN frame ID - 1st byte (order intel)
        Byte[02] = CAN frame ID - 2nd byte
        Byte[03] \
        Byte[04] |
        Byte[05] |
        Byte[06] | CAN data
        Byte[07] |
        Byte[08] |
        Byte[09] |
        Byte[10] /
        Byte[11] \
        Byte[12] | Computed CRC-32 (order intel)
        Byte[13] |
        Byte[14] /
        Byte[15] = Padding byte (0x7F)
        """
        if data[0] != 0xFE and data[15] != 0x7F:
            raise ValueError("Serial frame is corrupted")
        return struct.unpack_from("<xH4s4sIx", data, offset)
