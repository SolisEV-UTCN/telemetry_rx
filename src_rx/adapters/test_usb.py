import logging
from pathlib import Path
from typing import Generator

from classes.message import Message
from adapters.usb import UsbAdapter


class TestUsbAdapter(UsbAdapter):
    """This adapters is used for testing.
    
    Keyword arguments:
    file_path -- Path to csv file with dummy data, if None generate random messages
    """
    def get_point_list(self) -> Generator[Message, None, None]:
        """Returns list of points"""
        logging.info("Test USB adapter selected")
        output = Message("AAA", 999)

        # Generate random data
        # output = [Point("test_data").field("value").timestamp(i) for i in range(1_000_000)]

        yield output
