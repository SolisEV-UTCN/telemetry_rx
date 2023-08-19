from pathlib import Path
import logging
import os
import sys

from influxdb_client import InfluxDBClient, WriteOptions, WritePrecision
from influxdb_client.client.util.multiprocessing_helper import MultiprocessingWriter

from classes.message import Message
from classes.parser import Parser
from helpers.patterns import Adapter, State
import adapters.dev_can
import adapters.dev_usb
import adapters.test_can
import adapters.test_usb


PWD = Path(__file__).parent.absolute()
CAN_MAPPING = Path(PWD, "config", "basic.json")
ENTRYPOINT = "http://database:8086"

def main_loop(reader: Adapter):
    # Connect asynchronously to InfluxDb
    with MultiprocessingWriter(url=ENTRYPOINT,
                               token=os.environ["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"],
                               org=os.environ["DOCKER_INFLUXDB_INIT_ORG"],
                               write_options=WriteOptions(batch_size=20)
                               ) as writer:
        state = State.INIT

        # Main application loop. State machine
        while True:
            if state is State.INIT:
                # Try to connect
                state = reader.init_device()

            elif state is State.COMM:
                # Read data
                message : Message
                for message in reader.read_data():
                    # Write data if read correctly
                    writer.write(bucket=message.bucket, record=message.to_point(), write_precision=WritePrecision.US)

            elif state is State.CLOSE:
                # Clear ports
                reader.deinit_device()
                logging.info("Closing application")
                break

            else:
                logging.error(f"Tried to enter unimplemented state {state}")
                state = State.CLOSE


if __name__ == "__main__":
    # Logger scaffolding
    formatter = logging.Formatter("[{levelname}]{filename}:{message}", style="{")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()

    # Enable debug info
    if os.environ["TUCN_RUN_MODE"] == "debug":
        handler.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
        root.setLevel(logging.INFO)
    root.addHandler(handler)

    # Container information
    root.debug("Environment variables:")
    try:
        root.debug(f"{os.environ['TUCN_INPUT_ADAPTER']}")
        root.debug(f"{os.environ['DOCKER_INFLUXDB_INIT_ADMIN_TOKEN']}")
        root.debug(f"{os.environ['DOCKER_INFLUXDB_INIT_ORG']}")
    except KeyError:
        root.warn(f"Missing an environment variable, using the default variables")
        os.environ.update({"TUCN_INPUT_ADAPTER": "usb"})
        os.environ.update({"DOCKER_INFLUXDB_INIT_ADMIN_TOKEN": "mJFrzAhQE_kk3gQGX3qcHe2c5I_CLGeyN2PseCEWs5IBQl4tB27zJOVWuQfIFwT8M5SDcrt9-Drv0mE5DvqBdw=="})
        os.environ.update({"DOCKER_INFLUXDB_INIT_ORG": "solis"})
    
    # Read JSON configuration file
    Parser().read_file(CAN_MAPPING)

    # Select adapter for data reader
    if os.environ["TUCN_INPUT_ADAPTER"] == "usb":
        logging.info("USB adapter selected")
        reader = adapters.dev_usb.UsbAdapter()
    elif os.environ["TUCN_INPUT_ADAPTER"] == "can":
        logging.info("CAN adapter selected")
        reader = adapters.dev_can.CanAdapter()
    elif os.environ["TUCN_INPUT_ADAPTER"] == "test_usb":
        logging.info("Test USB adapter selected")
        reader = adapters.test_usb.TestUsbAdapter()
    elif os.environ["TUCN_INPUT_ADAPTER"] == "test_can":
        logging.info("Test CAN adapter selected")
        reader = adapters.test_can.TestCanAdapter()
    else:
        reader = Adapter()

    # Bucket API is not exposed in async InfluxDB client
    with InfluxDBClient(url=ENTRYPOINT, token=os.environ["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"], org=os.environ["DOCKER_INFLUXDB_INIT_ORG"]) as influxdb_client:
        # Create buckets if they don't exist
        buckets_api = influxdb_client.buckets_api()
        for bucket in Parser().iter_buckets():
            if not buckets_api.find_bucket_by_name(bucket):
                logging.debug(f"Creating {bucket} bucket")
                buckets_api.create_bucket(bucket_name=bucket)

    # Threaded loop
    main_loop(reader)
