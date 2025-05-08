import logging
import struct
from collections.abc import Iterator
from datetime import datetime

import serial
from influxdb_client import Point

from telemetry_rx.adapters import Adapter
from telemetry_rx.utils import AppState

# 2025-05-08 14:00:00


class UsbAdapter(Adapter):
    MESSAGE_LEN = 21  # Updated to include 5 bytes for timestamp

    def __init__(self, address: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        self.address = address
        self.baudrate = 115200
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_EVEN
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = None

    def init_device(self) -> AppState:
        try:
            self.device = serial.Serial(
                port=self.address,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout,
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
            logging.critical("Could not establish serial communication. To see more info, enable debug flag.")
            logging.debug(e)
            return AppState.ERROR

    def deinit_device(self) -> None:
        self.device.close()

    def read_data(self) -> Iterator[Point]:
        """Reads serial input and converts bytestream to a Point."""
        while self.running:
            # Read UART bytestream
            logging.debug(f"{self.device.in_waiting} bytes are in input buffer.")
            payload = self.device.read(1)
            if payload[0] != 0xFE:
                continue

            payload += self.device.read(UsbAdapter.MESSAGE_LEN - 1)
            logging.debug(f"Full payload length: {len(payload)}")
            logging.debug(f"Full payload: {payload.hex()}")
            logging.debug(f"Expected length: {UsbAdapter.MESSAGE_LEN}")
            logging.debug(f"First byte: {payload[0]:02x}, Last byte: {payload[-1]:02x}")

            try:
                frame_id, data_h, data_l, timestamp, crc = self.process_bytes(payload)
                logging.debug(f"Processed bytes - frame_id: {frame_id}, timestamp: {timestamp.hex()}")
            except ValueError as e:
                logging.debug(f"Failed to process bytes: {e}")
                logging.debug(f"Received: {payload}")
                continue

            # Validate CRC-32 MPEG-2
            # STM32 algorithm reverses byte order for uint32_t before calculating CRC
            if not self.validate_crc(crc, data_h[::-1] + data_l[::-1]):
                continue

            # Decode data
            point = self.parse_data(frame_id, data_h + data_l)
            if point is not None:
                # Add timestamp to the point
                dt = datetime(
                    year=datetime.now().year,  # Current year
                    month=timestamp[4],        # Month
                    day=timestamp[3],          # Day
                    hour=timestamp[2],         # Hour
                    minute=timestamp[1],       # Minute
                    second=timestamp[0]        # Second
                )
                logging.debug(f"Created datetime: {dt}")
                point.time(dt)
                yield point

    def process_bytes(self, data: bytes) -> tuple[int, bytes, bytes, bytes, int]:
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
        Byte[11] \ //second
        Byte[12] | //minute
        Byte[13] | //hour
        Byte[14] | //day
        Byte[15] / //month
        Byte[16] \
        Byte[17] | Computed CRC-32 (order intel)
        Byte[18] |
        Byte[19] /
        Byte[20] = Padding byte (0x7F)
        """
        if data[0] != 0xFE or data[20] != 0x7F:
            raise ValueError("Serial frame is corrupted")
        return struct.unpack("<xH4s4s5sIx", data)
