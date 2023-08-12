from pathlib import Path
from typing import Dict, Iterable, List
import json
import logging

from classes.message import Message


CAN_ID = "can_id"
CAST_TYPE = "fields"

__slots__ = "path", "buckets", "messages"
class Parser(object):
    buckets: List[str]
    messages: Dict[int, Message]

    def read_file(self, path: Path):
        logging.info(f"Loading config JSON from: {path}")
        self.buckets = []
        self.messages = {}

        with open(path) as file:
            config_file = json.load(file, cls=json.JSONDecoder)
            for bucket, messages in config_file.items():
                self.buckets.append(bucket)
                for name, message in messages.items():
                    id = message[CAN_ID]
                    recipe = message[CAST_TYPE]
                    self.messages.update({id: Message(name, bucket, recipe)})

        logging.info(f"Found {len(self.buckets)} buckets")
        for index, bucket in enumerate(self.buckets):
            logging.debug(f"Bucket #{index + 1}: {bucket}")

        logging.info(f"Found {len(self.messages.keys())} CAN messages")
        for can_id, message in self.messages.items():
            logging.debug(f"CAN 0x{can_id}: {message.name}")

    def iter_buckets(self) -> Iterable[str]:
        for bucket in self.buckets:
            yield bucket

    def iter_messages(self) -> Dict[int, Message]:
        return self.messages
    
    # Private methods
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Parser, cls).__new__(cls)
        return cls._instance
