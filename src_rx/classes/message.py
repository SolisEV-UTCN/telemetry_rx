import struct
from typing import List

from influxdb_client import Point


class Field(object):
    def __init__(self, name: str, value, offset, factor) -> None:
        self.name = name
        self.value = (value + offset) * factor

__slots__ = "name", "bucket", "recipe", "data"
class Message(object):
    def __init__(self, name: str, bucket="garbage", field_names=None, fmt="<8B") -> None:
        self.name = name
        self.bucket = bucket
        self.field_names = []
        self.fmt = fmt
        if field_names is None:
            self.field_names = [str(i) for i in range(struct.calcsize(fmt))]
        else:
            for name in field_names:
                self.field_names.append(name)
        self.data: List[Field] = []

    def to_point(self) -> Point:
        point = Point(self.name)
        for field in self.data:
            point.field(field.name, field.value)
        return point
    
    def append(self, name: str, value, offset, factor) -> None:
        self.data.append(Field(name, value, offset, factor))
