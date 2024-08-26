import logging
import socket
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
    def process_data(dbc: Database, data: list[bytes]) -> Point | None:
        """Data is received over UDP in 14 bytes, network order.
        A message consists of 2 bytes of frame ID and 8 bytes of data.
        Ex.: | 66 CB 65 6F | 04 01 | 00 01 02 03 04 05 06 07 |
             |  Timestamp  |   ID  |           DATA          |
        """
        return Point()
