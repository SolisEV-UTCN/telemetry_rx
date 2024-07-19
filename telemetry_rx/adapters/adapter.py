import logging
import tempfile
import time
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path

import cantools
from crc import Calculator, Configuration
from influxdb_client import Point

from telemetry_rx.classes import AppState

PWD = Path(__file__).parent.parent.absolute()
PATH_DBC = Path(PWD, "config", "Solis-EV4.dbc")


class Adapter(ABC):
    """Variation point for InfluxDB input"""

    CRC_CONF = Configuration(
        width=32,
        polynomial=0x04C11DB7,
        init_value=0xFFFFFFFF,
        final_xor_value=0x0,
    )

    def __init__(self):
        self.device = None
        self.tmp_dir = tempfile.gettempdir()
        self.dbc = cantools.db.load_file(PATH_DBC, database_format="dbc", encoding="cp1252", cache_dir=self.tmp_dir)

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
        calc = Calculator(Adapter.CRC_CONF, optimized=True)
        crc = calc.checksum(data)
        if expected_crc != crc:
            logging.debug(f"Calculated/Expected CRCs: {crc}/{expected_crc}")
        return expected_crc == crc

    def parse_data(self, frame_id: int, data: bytes) -> Point | None:
        # Get message formatter
        try:
            message = self.dbc.get_message_by_frame_id(frame_id)
            logging.debug(f"Receive message {message}")
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
                "time": time.time_ns(),
            }
        )
