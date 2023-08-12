import logging
from typing import List, Tuple

from influxdb_client import Point


__slots__ = "name", "bucket", "recipe", "data"
class Message(object):
    def __init__(self, name: str, bucket: str, recipe: List[str]) -> None:
        self.name = name
        self.bucket = bucket
        self.recipe = recipe
        self.data: List[Tuple[str, int | float]] = []

        self._validate_recipe()

    def to_point(self) -> Point:
        point = Point(self.name)
        for double in self.data:
            point.field(double[0], double[1])
        return point
    
    async def convert_bytes(self, byte_stream: bytearray):
        self.data.clear()

        factor = 1
        offset = 0
        for rule in self.recipe:
            options = rule.split(",")
            name = options[0]
            byte_order = options[1]
            data_type = options[2]
            bitpos = int(options[3])
            length = int(options[4])

            # Optional parameters
            if len(options) > 5:
                factor = float(options[5])
            if len(options) > 6:
                offset = int(options[6])

            # Byte order
            if byte_order == "intel":
                field = byte_stream[bitpos:bitpos + length]
            else:
                field = byte_stream[bitpos + length:bitpos:-1]

            # Data type
            if data_type == "uint" or data_type == "int":
                field = int(field)
            else:
                field = float(field)

            # Update dictionary
            self.data.append((name, (field + offset) * factor ))

    def _validate_recipe(self) -> None:
        for rule in self.recipe:
            options = rule.split(",")

            # Check number of arguments
            if len(options) < 5 and len(options) > 7:
                logging.warn(f"[Message {self.name}]A rule has an incorrect number of arguments")
                continue

            # Check byteorder
            if options[1] != "intel" and options[2] != "motorola":
                logging.warn(f"[Message {self.name}]Second rule argument should be intel or motorola")
                continue

            # Check data type
            if options[2] != "uint" and options[2] != "int" and options[2] != "float":
                logging.warn(f"[Message {self.name}]Third rule argument should be uint, int or float")
                continue

            # Check type of bitpos, length, factor, offset
            try:
                int(options[3])
                int(options[4])
                if len(options) > 5:
                    float(options[5])
                if len(options) > 6:
                    int(options[6])
            except ValueError:
                logging.warn(f"[Message {self.name}]Invalid type for arguments 4-7")
                continue

            # Check if data is out of bounds
            if (int(options[3]) + int(options[4])) > 64:
                logging.warn(f"[Message {self.name}]Bitpos + length is out of bounds")
                continue
