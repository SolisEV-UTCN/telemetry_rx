from pathlib import Path
import asyncio
import enum
import logging
import os
import sys

from influxdb_client import InfluxDBClient
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from classes.parser import Parser
from helpers.paterns import Adapter
import adapters.dev_can
import adapters.dev_usb
import adapters.test_can
import adapters.test_usb


PWD = Path(__file__).parent.absolute()
CAN_MAPPING = Path(PWD, "config", "basic.json")

class State(enum.Enum):
    INIT = 1
    COMM = 2
    CLOSE = 3

async def main_async(reader: Adapter):
    # Connect asynchronously to InfluxDb
    async with InfluxDBClientAsync(url="http://database:8086", token=os.environ["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"], org=os.environ["DOCKER_INFLUXDB_INIT_ORG"]) as influxdb_client:
        state = State.INIT
        writer = influxdb_client.write_api()

        # Main application loop. State machine
        while state is not State.CLOSE:
            if state is State.INIT:
                # Try to connect
                succ = await reader.init_device()
                if succ is True:
                    state = State.COMM

            elif state is State.COMM:
                # Read data
                succ, message = await reader.read_data()
                if succ is False:
                    logging.warn("Connection to read medium is lost")
                    state = State.INIT
                    continue
                # Write data
                await writer.write(bucket=message.bucket, record=message.to_point())
            
            else:
                logging.error(f"Unknown state. Closing application")
                state = State.CLOSE


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
    Parser().read_file(CAN_MAPPING)

    # Select adapter for data reader
    if os.environ['TUCN_INPUT_ADAPTER'] == "usb":
        logging.info("USB adapter selected")
        reader = adapters.dev_usb.UsbAdapter()
    elif os.environ['TUCN_INPUT_ADAPTER'] == "can":
        logging.info("CAN adapter selected")
        reader = adapters.dev_can.CanAdapter()
    elif os.environ['TUCN_INPUT_ADAPTER'] == "test_usb":
        logging.info("Test USB adapter selected")
        reader = adapters.test_usb.TestUsbAdapter()
    elif os.environ['TUCN_INPUT_ADAPTER'] == "test_can":
        logging.info("Test CAN adapter selected")
        reader = adapters.test_can.TestCanAdapter()
    else:
        reader = Adapter()

    # Bucket API is not exposed in async InfluxDB client
    with InfluxDBClient(url="http://database:8086", token=os.environ["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"], org=os.environ["DOCKER_INFLUXDB_INIT_ORG"]) as influxdb_client:
        # Create buckets if they don't exist
        buckets_api = influxdb_client.buckets_api()
        for bucket in Parser().iter_buckets():
            if not buckets_api.find_bucket_by_name(bucket):
                logging.debug(f"Creating {bucket} bucket")
                buckets_api.create_bucket(bucket_name=bucket)

    # Asynchronous loop
    asyncio.run(main_async(reader))
