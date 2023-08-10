from pathlib import Path
import logging
import os
import sys

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import WriteApi, ASYNCHRONOUS

from classes.parser import Parser
from helpers.meta import Adapter
import adapters.can
import adapters.usb
import adapters.test_can
import adapters.test_usb


CAN_MAPPING = Path("config", "basic.json")

def loop(reader: Adapter, writer: WriteApi, config: Parser) -> None:
    """Main application loop. Reads telemetry data and writes it to InfluxDB"""
    while True:
        reader.read_data(config.messages())
        for message in reader.iter_data():
            # Write data
            writer.write(bucket=message.bucket(), record=message.point())

if __name__ == "__main__":
    # Logger scaffolding
    formatter = logging.Formatter("[{levelname}]{filename}:{message}", style="{")
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)

    # Container information
    root.debug("Environment variables:")
    root.debug(f"{os.environ['TUCN_INPUT_ADAPTER']}")
    root.debug(f"{os.environ['DOCKER_INFLUXDB_INIT_ADMIN_TOKEN']}")
    root.debug(f"{os.environ['DOCKER_INFLUXDB_INIT_ORG']}")

    # Read JSON configuration file
    config = Parser(CAN_MAPPING)

    # Connect to InfluxDb
    influxdb_client = InfluxDBClient(
        url="database:8086",
        token=os.environ["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"],
        org=os.environ["DOCKER_INFLUXDB_INIT_ORG"]
    )
    writer = influxdb_client.write_api(write_options=ASYNCHRONOUS)

    # Create buckets if don't exist
    buckets_api = influxdb_client.buckets_api()
    for bucket in config.buckets():
        if buckets_api.find_bucket_by_name(bucket):
            buckets_api.create_bucket(bucket_name=bucket)

    # Select adapter for data reader
    if os.environ['TUCN_INPUT_ADAPTER'] == "usb":
        reader = adapters.usb.UsbAdapter()
    elif os.environ['TUCN_INPUT_ADAPTER'] == "can":
        reader = adapters.can.CanAdapter()
    elif os.environ['TUCN_INPUT_ADAPTER'] == "test_usb":
        reader = adapters.test_usb.TestUsbAdapter()
    elif os.environ['TUCN_INPUT_ADAPTER'] == "test_can":
        reader = adapters.test_can.TestCanAdapter()
    else:
        reader = Adapter()
    
    loop(reader, writer, config)
