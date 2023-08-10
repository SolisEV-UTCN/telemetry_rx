from influxdb_client import Point


__slots__ = "bucket", "id", "data"
class Message(object):
    def __init__(self, bucket, id) -> None:
        self.bucket = bucket
        self.id = id
        self.data = None

    def bucket(self) -> str:
        return "AAA"
    
    def point(self) -> Point:
        return Point("garbage")
