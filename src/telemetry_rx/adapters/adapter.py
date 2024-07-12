import logging
import tempfile
import time
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path

import cantools
from crc import Calculator, Crc32
from influxdb_client import Point

from classes import AppState

PWD = Path(__file__).parent.absolute()
PATH_DBC = Path(PWD, "config", "solis_ev4.dbc")


class Adapter(ABC):
    """Variation point for InfluxDB input"""
    def __init__(self):
        self.device = None
        self.tmp_dir = tempfile.gettempdir()
        self.dbc = cantools.db.load_file(
            PATH_DBC, database_format="dbc", encoding="cp1252", cache_dir=self.tmp_dir
        )

    @abstractmethod
    def init_device(self) -> AppState:
        pass

    @abstractmethod
    def deinit_device(self) -> None:
        pass

    @abstractmethod
    def read_data(self) -> Iterator[Point]:
        pass

    def validate_crc(self, expected_crc: int, data: bytes) -> bool:
        calc = Calculator(Crc32.BZIP2, optimized=True)
        crc = calc.checksum(data)
        logging.debug(f"Calculated/Expected CRCs: {crc}/{expected_crc}")
        return expected_crc == crc

    def parse_data(self, frame_id: int, data: bytes) -> Point | None:
        # Get message formatter
        try:
            message = self.dbc.get_message_by_frame_id(frame_id)
        except KeyError:
            logging.warn(f"Received unknown message with {frame_id:04X} ID.")
            return None

        signals = message.decode_simple(data)
        signals.update({
            "measurement": message.senders[0],
            "time": time.time(),
        })
        return Point.from_dict(signals)
