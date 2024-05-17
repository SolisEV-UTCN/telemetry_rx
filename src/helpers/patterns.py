import enum
import logging
from typing import Tuple

from classes.message import Message


class State(enum.Enum):
    INIT = 1
    COMM = 2
    CLOSE = 3
    
class Adapter(object):
    """Variation point for InfluxDB input"""
    def __init__(self):
        pass

    def init_device(self) -> State:
        logging.error("No valid adapter selected")
        return State.CLOSE
    
    def deinit_device(self) -> None:
        logging.error("No valid adapter selected")

    def read_data(self) -> Tuple[State, Message | None]:
        """Reads input medium"""
        logging.error("No valid adapter selected")
        return State.CLOSE, None
