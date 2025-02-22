from dataclasses import dataclass

from cantools.database import Database
from influxdb_client import InfluxDBClient


@dataclass()
class AppContext(object):
    client: InfluxDBClient = None
    bucket_name: str = None
    dbc: Database = None

    def __iter__(self):
        return iter(self.__dict__)
