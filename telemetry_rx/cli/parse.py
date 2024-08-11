import logging
import os
import re
from pathlib import Path

from influxdb_client import InfluxDBClient, Point, WriteOptions

from telemetry_rx.utils import InfluxCreds


# Read and parse .txt file
def read_and_parse_file(file_path):
    data_points = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            match = re.match(r"(\d+)\s*:\s*([\dA-Fa-f]+)\s*([\dA-Fa-f]+)", line)
            if match:
                timestamp = int(match.group(1))
                value1 = match.group(2)
                value2 = match.group(3)
                byte_array1 = bytes.fromhex(value1)
                byte_array2 = bytes.fromhex(value2)
                concatenated_bytes = byte_array1 + byte_array2

                data_points.append((timestamp, concatenated_bytes))
    return data_points


def write_to_influxdb(write_api: InfluxDBClient, credentials: InfluxCreds, data_points, measurement: str):

    for timestamp, value in data_points:
        point = Point(measurement).field("value", int.from_bytes(value, byteorder="little")).time(timestamp)
        write_api.write(bucket = credentials.as_dict()['bucket'],
                        org    = credentials.as_dict()['org'],
                        record = point)

def parse(credentials: InfluxCreds, data_path: Path):

    client = InfluxDBClient(url   = credentials.as_dict()['url'],
                            token = credentials.as_dict()['token'],
                            org   = credentials.as_dict()['org'])
    write_api = client.write_api(write_options=WriteOptions())

    for file_directory in os.scandir(data_path):
        for file_path in os.listdir(file_directory.path):
            file = os.path.join(file_directory, file_path)
            if os.path.isfile(file):
                file_name = str.split(str.split(file_path, "\\")[0], ".")[0]

                measurement = str.split(file_name, "_")[0] + "_" + str.split(file_name, "_")[1]

                data_points = read_and_parse_file(file)

                write_to_influxdb(write_api, credentials, data_points, measurement)

    client.close()
