import enum
import logging
from typing import Iterator

from influxdb_client import Point

from classes.message import Message


class State(enum.Enum):
    INIT = 1
    COMM = 2
    CLOSE = 3
    SKIP_WRITE = 4
    
class Adapter(object):
    """Variation point for InfluxDB input"""
    def __init__(self):
        pass

    def init_device(self) -> State:
        logging.error("No valid adapter selected")
        return State.CLOSE
    
    def deinit_device(self) -> None:
        logging.error("No valid adapter selected")

    def read_data(self) -> Iterator[Message]:
        """Reads input medium"""
        logging.error("No valid adapter selected")
        yield Message("INVALID")
