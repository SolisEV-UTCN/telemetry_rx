from pathlib import Path
from typing import Dict, Iterable, List
import json
import logging

from classes.message import Message


CAN_ID = "can_id"
CAST_NAMES = "field_names"
CAST_TYPE = "field_struct"

__slots__ = "path", "buckets", "messages"
class Parser(object):
    buckets: List[str]
    messages: Dict[int, Message]

    @staticmethod
    def read_file(path: Path):
        logging.info(f"Loading config JSON from: {path}.")
        Parser.buckets = []
        Parser.messages = {}

        with open(path) as file:
            config_file = json.load(file, cls=json.JSONDecoder)
            for bucket, messages in config_file.items():
                Parser.buckets.append(bucket)
                for name, message in messages.items():
                    id = int(message[CAN_ID], 16)
                    fields = message[CAST_NAMES]
                    fmt = message[CAST_TYPE]
                    Parser.messages.update({id: Message(name, bucket, fields, fmt)})

        logging.info(f"Found {len(Parser.buckets)} buckets.")
        for index, bucket in enumerate(Parser.buckets):
            logging.debug(f"Bucket #{index + 1}: {bucket}")

        logging.info(f"Found {len(Parser.messages.keys())} CAN messages.")
        for can_id, message in Parser.messages.items():
            logging.debug(f"CAN 0x{can_id}: {message.name}")

    @staticmethod
    def iter_buckets() -> Iterable[str]:
        for bucket in Parser.buckets:
            yield bucket

    @staticmethod
    def iter_messages() -> Dict[int, Message]:
        return Parser.messages
