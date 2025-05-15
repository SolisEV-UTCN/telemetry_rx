import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Iterator

from cantools.database import Database
from crc import Calculator, Configuration
from influxdb_client import Point

from telemetry_rx.utils import AppState


class Adapter(ABC):
    """Variation point for InfluxDB input"""

    CRC_CONF = Configuration(
        width=32,
        polynomial=0x04C11DB7,
        init_value=0xFFFFFFFF,
        final_xor_value=0x0,
    )

    def __init__(self, dbc: Database):
        self.device = None
        self.dbc = dbc
        self.calc = Calculator(Adapter.CRC_CONF, optimized=True)

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
        crc = self.calc.checksum(data)
        if expected_crc != crc:
            logging.debug(f"Calculated/Expected CRCs: {crc}/{expected_crc}")
        return expected_crc == crc

    def parse_data(self, frame_id: int, data: bytes) -> Point | None:
        # Get message formatter
        try:
            message = self.dbc.get_message_by_frame_id(frame_id)
            logging.debug(f"Found message in DBC: {message.name}")
        except KeyError:
            logging.warn(f"Received unknown message with {frame_id:04X} ID.")
            return None

        try:
            fields = message.decode_simple(data)
            logging.debug(f"Decoded fields for {message.name}: {fields}")
        except Exception as e:
            logging.error(f"Failed to decode message {message.name}: {e}")
            return None

        try:
            point = Point.from_dict(
                {
                    "measurement": "solar_vehicle",
                    "tags": {"ecu": message.senders[0]},
                    "fields": fields,
                    "time": time.time_ns(),
                }
            )
            logging.debug(f"Created point for {message.name} from {message.senders[0]}")
            return point
        except Exception as e:
            logging.error(f"Failed to create point for {message.name}: {e}")
            return None
