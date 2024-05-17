from pathlib import Path
import logging
import os
import sys

from influxdb_client import InfluxDBClient, WriteOptions, WritePrecision
from influxdb_client.client.util.multiprocessing_helper import MultiprocessingWriter

from classes.parser import Parser
from helpers.patterns import Adapter, State
import adapters.dev_can
import adapters.dev_usb
import adapters.test_can
import adapters.test_usb


PWD = Path(__file__).parent.absolute()
CAN_MAPPING = Path(PWD, "config", "basic.json")
ENTRYPOINT = "http://127.0.0.1:8086"

def main_loop(reader: Adapter, token: str, org: str):
    # Write points in batches to InfluxDb
    with MultiprocessingWriter(
        url=ENTRYPOINT,
        token=token,
        org=org,
        write_options=WriteOptions(batch_size=20)
    ) as writer:
        
        # State machine
        state = State.INIT
        while True:
            # Initialization state
            if state is State.INIT:
                state = reader.init_device()

            # Communication state
            elif state is State.COMM:
                state, message = reader.read_data()
                if message is not None:
                    writer.write(
                        bucket=message.bucket,
                        record=message.to_point(),
                        write_precision=WritePrecision.US
                    )

            # Deinitialization state
            elif state is State.CLOSE:
                reader.deinit_device()
                logging.info("Closing application.")
                break

            # Unknown state
            else:
                logging.error(f"Tried to enter an unimplemented state - {state}.")
                state = State.CLOSE


if __name__ == "__main__":
    # Logger scaffolding
    formatter = logging.Formatter("[{levelname}]{filename}:{message}", style="{")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()

    # Enable debug info
    debug_info = os.environ.get("TUCN_RUN_MODE", "debug")
    if debug_info == "debug":
        handler.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
        root.setLevel(logging.INFO)
    root.addHandler(handler)

    # Default environment variables
    adapter = os.environ.get("TUCN_INPUT_ADAPTER", "usb")
    logging.debug(f"TUCN_INPUT_ADAPTER={adapter}")

    token = os.environ.get("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN", "")
    logging.debug(f"DOCKER_INFLUXDB_INIT_ADMIN_TOKEN={token}")
    
    org = os.environ.get("DOCKER_INFLUXDB_INIT_ORG", "solis")
    logging.debug(f"DOCKER_INFLUXDB_INIT_ORG={org}")
    
    # Read JSON configuration file
    Parser.read_file(CAN_MAPPING)

    # Select adapter for data reader
    if adapter == "usb":
        logging.info("USB adapter selected.")
        reader = adapters.dev_usb.UsbAdapter()

    elif adapter == "can":
        logging.info("CAN adapter selected.")
        reader = adapters.dev_can.CanAdapter()

    elif adapter == "test_usb":
        logging.info("Test USB adapter selected.")
        reader = adapters.test_usb.TestUsbAdapter()

    elif adapter == "test_can":
        logging.info("Test CAN adapter selected.")
        reader = adapters.test_can.TestCanAdapter()
        
    else:
        reader = Adapter()

    # Bucket API is not exposed in async InfluxDB client
    with InfluxDBClient(url=ENTRYPOINT, token=token, org=org) as influxdb_client:
        # Create buckets if they don't exist
        buckets_api = influxdb_client.buckets_api()
        for bucket in Parser.iter_buckets():
            if not buckets_api.find_bucket_by_name(bucket):
                logging.debug(f"Creating {bucket} bucket.")
                buckets_api.create_bucket(bucket_name=bucket)

    # Threaded loop
    main_loop(reader, token, org)
