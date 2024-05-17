import logging
from typing import Tuple

from classes.message import Message
from adapters.dev_usb import UsbAdapter


class TestUsbAdapter(UsbAdapter):
    def __init__(self):
        pass

    async def init_device(self) -> bool:
        logging.error("Test USB adapter is not implemented")
        return False
    
    async def read_data(self) -> Tuple[bool, Message]:
        """Reads input medium"""
        logging.error("Test USB adapter is not implemented")
        return (False, Message("INVALID", "garbage", ["INVALID,intel,uint,0,1"]))
