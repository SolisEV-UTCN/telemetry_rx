import logging
from collections.abc import Iterator

from influxdb_client import Point

from telemetry_rx.adapters import Adapter
from telemetry_rx.classes import AppState


class TcpAdapter(Adapter):
    def __init__(self):
        super().__init__()

    def init_device(self) -> AppState:
        logging.error("TCP adapter is not implemented")
        return AppState.STOP

    def deinit_device(self) -> None:
        logging.error("TCP adapter is not implemented")

    def read_data(self) -> Iterator[Point]:
        """Reads input medium"""
        logging.error("TCP adapter is not implemented")
        raise NotImplementedError("TCP adapter is not implemented")
