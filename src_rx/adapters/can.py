import logging
from typing import Generator

from classes.message import Message
from helpers.meta import Adapter


class CanAdapter(Adapter):
    def get_point_list(self) -> Generator[Message, None, None]:
        """Returns list of points"""
        logging.info("Test USB adapter selected")
        yield Message("garbage", 999)
