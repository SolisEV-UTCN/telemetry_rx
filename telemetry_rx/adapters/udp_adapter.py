import logging
import socket
from collections.abc import Iterator

from cantools.database import Database
from influxdb_client import Point

from telemetry_rx.adapters import Adapter
from telemetry_rx.utils import AppState


class UdpAdapter(Adapter):
    def __init__(self, address: str, port: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        self.address = address
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connections: list[socket.socket] = []

    def init_device(self) -> AppState:
        try:
            self.server.bind((self.address, self.port))
        except OSError:
            logging.error(f"Couldn't bind server to {self.address}:{self.port}. Port is already in use!")
            return AppState.STOP
        else:
            self.server.listen()
            logging.info(f"Server is listening on {self.address}:{self.port}")
            return AppState.COMM

    def deinit_device(self) -> None:
        for conn in self.connections:
            conn.close()
        self.server.close()

    def read_data(self) -> Iterator[Point]:
        """Reads input medium"""
        while self.running:
            # Accept connection
            conn, addr = self.server.accept()
            self.connections.append(conn)
            logging.info(f"Connection from {addr[0]}:{addr[1]}")

            # Receive and process data
            data = conn.recv(14)
            point = self.process_data(self.dbc, data)
            if point is not None:
                logging.debug("Data received: {point}")
                yield point

    def process_data(dbc: Database, data: list[bytes]) -> Point | None:
        """Data is received over UDP in 14 bytes, network order.
        A message consists of 2 bytes of frame ID and 8 bytes of data.
        Ex.: | 66 CB 65 6F | 04 01 | 00 01 02 03 04 05 06 07 |
            |  Timestamp  |   ID  |           DATA          |
        """
        return Point()
