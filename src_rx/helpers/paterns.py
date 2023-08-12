import logging
from typing import Tuple

from classes.message import Message

    
class Adapter(object):
    """Variation point for InfluxDB input"""
    def __init__(self):
        pass

    async def init_device(self) -> bool:
        logging.error("No valid adapter selected")
        return False
    
    async def read_data(self) -> Tuple[bool, Message]:
        """Reads input medium"""
        logging.error("No valid adapter selected")
        return (False, Message("INVALID", "garbage", ["INVALID,intel,uint,0,1"]))
