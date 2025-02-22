import logging
import socket
import struct
from collections.abc import Iterator

from cantools.database import Database
from influxdb_client import Point

from telemetry_rx.adapters import Adapter
from telemetry_rx.utils import AppState


class UdpAdapter(Adapter):
    def __init__(self, address: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        address = address.split(":")
        self.address, self.port = address[0], int(address[1])
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def init_device(self) -> AppState:
        try:
            self.server.bind((self.address, self.port))
        except OSError as e:
            logging.error(f"Couldn't bind server to {self.address}:{self.port}. Port is already in use!")
            logging.debug(f"Bind failed due to: {e}")
            return AppState.STOP
        else:
            logging.info(f"Server is listening on {self.address}:{self.port}")
            return AppState.COMM

    def deinit_device(self) -> None:
        self.server.close()

    def read_data(self) -> Iterator[Point]:
        """Reads input medium"""
        while self.running:
            # Receive and process data
            data, addr = self.server.recvfrom(14)
            logging.info(f"Connection from {addr[0]}:{addr[1]}")
            logging.debug(f"Data received: {data}")
            point = self.process_data(self.dbc, data)
            if point is not None:
                yield point

    @staticmethod
    def process_data(dbc: Database, data: bytes) -> Point | None:
        """Data is received over UDP in 14 bytes, network order.
        A message consists of 2 bytes of frame ID and 8 bytes of data.
        Ex.: | 66 CB 65 6F | 04 01 | 00 01 02 03 04 05 06 07 |
             |  Timestamp  |   ID  |           DATA          |
        """

        if len(data) != 14:
            logging.error(f"Data received is not 14 bytes long: {data}")
            return None

        timestamp_bytes = data[:4]
        frame_id_bytes = data[4:6]
        data_bytes = data[6:]

        timestamp = struct.unpack("!I", timestamp_bytes)[0]
        frame_id = struct.unpack("!H", frame_id_bytes)[0]
        logging.debug(f"Timestamp: {timestamp}")
        logging.debug(f"Frame ID: {frame_id}")

        try:
            message = dbc.get_message_by_frame_id(frame_id)
            logging.debug(f"Received message: {data_bytes}")
        except KeyError:
            logging.warn(f"Received unknown message with {frame_id:04X} ID.")
            return None

        fields = message.decode_simple(data)
        logging.debug(f"Parsed data: {fields}")

        return Point.from_dict(
            {
                "measurement": "solar_vehicle",
                "tags": {"ecu": message.senders[0]},
                "fields": fields,
                "time": timestamp,
            }
        )
