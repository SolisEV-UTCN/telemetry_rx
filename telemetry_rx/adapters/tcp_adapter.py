import logging
import socket
import struct
from time import time_ns
from collections.abc import Iterator

from cantools.database import Database
from influxdb_client import Point

from telemetry_rx.adapters import Adapter
from telemetry_rx.utils import AppState


class TcpAdapter(Adapter):
    def __init__(self, address: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        address = address.split(":")
        self.address, self.port = address[0], int(address[1])
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def init_device(self) -> AppState:
        try:
            self.server.bind((self.address, self.port))
            self.server.listen()
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
            conn, addr = self.server.accept()
            conn.settimeout(20)
            logging.info(f"Connection from {addr}")
            try:
                while conn:
                    # Receive and process data
                    data = conn.recv(10)
                    if len(data) == 0:
                        conn.close()
                        break
                    logging.debug(f"Data received: {data}")
                    point = self.process_data(self.dbc, data)
                    if point is not None:
                        yield point
            except socket.timeout:
                conn.close()

    @staticmethod
    def process_data(dbc: Database, data: bytes) -> Point | None:
        """Data is received over TCP in 10 bytes, network order.
        A message consists of 2 bytes of frame ID and 8 bytes of data.
        Ex.: | 04 01 | 00 01 02 03 04 05 06 07 |
             |   ID  |           DATA          |
        """

        if len(data) != 10:
            logging.error(f"Data received is not 10 bytes long: {data}")
            return None

        frame_id, data = struct.unpack("<H8s", data)
        logging.debug(f"Frame ID: {frame_id}")

        try:
            message = dbc.get_message_by_frame_id(frame_id)
            logging.debug(f"Received message: {data}")
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
                "time": time_ns(),
            }
        )
