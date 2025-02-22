import logging
import os
import struct
from pathlib import Path
from typing import Iterator

from cantools.database import Database
from influxdb_client import InfluxDBClient, Point

from telemetry_rx.utils import MAX_DEPTH


def parse(client: InfluxDBClient, dbc: Database, data_path: Path, bucket: str):
    write_api = client.write_api()

    # Find file paths with binary data
    for file in locate_data_files(data_path):
        # Write points into InfluxDB
        for point in parse_file(file, dbc):
            write_api.write(bucket, point)

    # Clean-up
    write_api.close()


def locate_data_files(root: Path, depth=0, max_depth=MAX_DEPTH) -> Iterator[Path]:
    """Recursively search for .bin files."""
    if depth > max_depth:
        return

    # os.scandir is a better and faster directory iterator
    # https://peps.python.org/pep-0471/
    with os.scandir(root) as it:
        for entry in it:
            if entry.is_dir():
                yield from locate_data_files(entry.name, depth + 1)
            elif entry.is_file() and entry.name.endswith(".bin"):
                yield Path(entry.path)


def parse_file(file_path: Path, dbc: Database) -> Iterator[Point]:
    """Read and parse .bin file."""
    frame_id = file_path.stem

    try:
        message = dbc.get_message_by_frame_id(frame_id)
        logging.debug(f"Receive message {message}")
    except KeyError:
        logging.warn(f"Received unknown message with {frame_id:04X} ID.")
        return None

    with open(file_path, "rb") as file:
        while (line := file.read(16)) == 16:
            timestamp: int
            byte_array: list[bytes]

            # Message is serialized into 16 bytes, motorolla order
            # First 8 bytes are UNIX timestamps, ULL type
            # Following 8 bytes are encoded CAN data
            timestamp, byte_array = struct.unpack(">Q8s", line)
            fields = message.decode_simple(byte_array)
            logging.debug(f"Parsed data: {fields}")

            # Construct a point
            yield Point.from_dict(
                {
                    "measurement": "solar_vehicle",
                    "tags": {"ecu": message.senders[0]},
                    "fields": fields,
                    "time": timestamp,
                }
            )
