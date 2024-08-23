import logging
import os
import struct
from pathlib import Path

from influxdb_client import InfluxDBClient, Point, WriteOptions

from telemetry_rx.utils import InfluxCreds


# Read and parse .txt file
def read_and_parse_file(file_path):
    data_points = []
    with open(file_path, "rb") as file:

        byteLine = file.read(20)
        while len(byteLine) == 20:

            byteArray: bytes

            # <4xL8s intel -> >4x8s8s motorolla + timestamp modification
            timestamp, byteArray = struct.unpack(">4x8s8s", byteLine)

            data_points.append((timestamp, byteArray))

            byteLine = file.read(20)

    return data_points


def write_to_influxdb(write_api: InfluxDBClient, credentials: InfluxCreds, data_points, measurement: str):

    for timestamp, value in data_points:
        point = Point(measurement).field("value", int.from_bytes(value, byteorder="big")).time(timestamp)
        write_api.write(bucket = credentials.as_dict()['bucket'],
                        org    = credentials.as_dict()['org'],
                        record = point)

def parse(credentials: InfluxCreds, data_path: Path):

    client = InfluxDBClient(url   = credentials.as_dict()['url'],
                            token = credentials.as_dict()['token'],
                            org   = credentials.as_dict()['org'])
    write_api = client.write_api(write_options=WriteOptions())

    for file_path in os.listdir(data_path):
            file = os.path.join(data_path, file_path)
            if os.path.isfile(file):
                file_name = str.split(str.split(file_path, "\\")[0], ".")[0]

                measurement = str.split(file_name, "_")[0] + "_" + str.split(file_name, "_")[1]

                data_points = read_and_parse_file(file)


                write_to_influxdb(write_api, credentials, data_points, measurement)

    client.close()
