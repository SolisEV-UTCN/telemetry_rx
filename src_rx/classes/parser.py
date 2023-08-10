from pathlib import Path
from typing import List, Dict
import json
import logging

from classes.message import Message
from helpers.meta import Singleton


__slots__ = "path", "buckets", "messages"
class Parser(Singleton):
    def __init__(self, path: Path) -> None:
        self.path = path

    def buckets(self) -> List[str]:
        with open(self.path) as file:
            json.load(file, cls=json.JSONDecoder)
        return ["AAA"]

    def messages(self) -> Dict[int, Message]:
        with open(self.path) as file:
            json.load(file, cls=json.JSONDecoder)
        return {999: Message("AAA", 999)}
