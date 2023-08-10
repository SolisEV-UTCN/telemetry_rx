import logging
from typing import Dict, Generator

from classes.message import Message


class Singleton(object):
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(*args, **kwargs)
        return cls._instances[cls]
    
class Adapter():
    """Variation point for InfluxDB input"""
    def read_data(self, filter: Dict[int, Message]) -> None:
        """Reads input medium"""
        pass

    def iter_data(self) -> Generator[Message, None, None]:
        """Returns iterator to the list of points"""
        logging.error("No valid adapter selected. Modify environment file.")
        yield Message("garbage", 999)
