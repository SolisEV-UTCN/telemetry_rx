from classes.meta import Singleton

from pathlib import Path
import json
import logging

__slots__ = "path", "buckets", "messages"
class Config(metaclass=Singleton):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.buckets = []
        self.messages = []

    def read_path(self) -> None:
        try:
            with open(self.path) as file:
                json.loads(file, cls=json.JSONDecoder, )
        except json.JSONDecodeError as e:
            logging.error(f"Unable to parse config. For more information check, src/plug&play/classes/can.py\n{e}")
