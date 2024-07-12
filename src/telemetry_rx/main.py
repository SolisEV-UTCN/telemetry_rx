from pathlib import Path
import logging
import os
import sys

from influxdb_client import InfluxDBClient, WriteOptions, WritePrecision
from influxdb_client.client.util.multiprocessing_helper import MultiprocessingWriter

from adapters import Adapter, TcpAdapter, UsbAdapter
from classes import AppState


PWD = Path(__file__).parent.absolute()
CAN_MAPPING = Path(PWD, "config", "basic.json")
ENTRYPOINT = "http://127.0.0.1:8086"


def _init_logger(debug=False) -> None:
    """Format logger to be pretty."""
    # Logger scaffolding
    formatter = logging.Formatter("[{levelname}]{filename}:{message}", style="{")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()

    # Enable debug info
    if debug:
        handler.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
        root.setLevel(logging.INFO)
    root.addHandler(handler)


def _configure_adapter() -> Adapter:
    """Select adapter to medium where the data will arrive."""
    # Default environment variables
    adapter = os.environ.get("INPUT_ADAPTER", "USB").upper()
    logging.debug(f"INPUT_ADAPTER={adapter}")

    # Select adapter for data reader
    if adapter == "USB":
        logging.info("USB adapter selected.")
        reader = UsbAdapter()

    elif adapter == "TCP":
        logging.info("TCP adapter selected.")
        reader = TcpAdapter()

    else:
        logging.error("No adapter selected.")
        raise ValueError("Incorrect adapter selected: {adapter}")

    return reader


def _init_influx(reader: Adapter) -> None:
    # Get API token
    token = os.environ.get("INFLUX_TOKEN_FILE", "/run/secrets/influx_token").lower()
    logging.debug(f"INFLUX_TOKEN_FILE={token}")
    token = open(Path(token), "rt").readline().strip()
    logging.debug(f"INFLUX_TOKEN={token}")

    # Get ORG info
    org = os.environ.get("INFLUX_ORG", "solis").lower()
    logging.debug(f"INFLUX_ORG={org}")

    # Get Bucket info
    bucket = os.environ.get("INFLUX_BUCKET", "test_bucket").lower()
    logging.debug(f"INFLUX_BUCKET={bucket}")

    # Create bucket if it doesn't exists
    with InfluxDBClient(url=ENTRYPOINT, token=token, org=org) as influxdb_client:
        # Create buckets if they don't exist
        buckets_api = influxdb_client.buckets_api()
        if not buckets_api.find_bucket_by_name(bucket):
            logging.info(f"Creating {bucket} bucket.")
            buckets_api.create_bucket(bucket_name=bucket)

    # Write points in batches to InfluxDb
    with MultiprocessingWriter(url=ENTRYPOINT, token=token, org=org, write_options=WriteOptions(batch_size=5000)) as writer:
        _main_loop(reader, writer, bucket)


def _main_loop(reader: Adapter, writer: MultiprocessingWriter, bucket: str):
    # State machine
    state = AppState.INIT
    while True:
        # Initialization state
        if state is AppState.INIT:
            state = reader.init_device()

        # Deinitialization state
        elif state is AppState.STOP:
            reader.deinit_device()
            logging.info("Closing application.")
            break

        try:
            # Continious reading
            for data in reader.read_data():
                writer.write(bucket=bucket, record=data, write_precision=WritePrecision.US)

        except KeyboardInterrupt:
            state = AppState.STOP
        except Exception as e:
            logging.error(f"Unhandeled exception: {e}")
            state = AppState.STOP


def start():
    """Main script."""
    debug = os.environ.get("RUN_MODE", "release").lower()
    if debug == "release":
        debug = False
    else:
        debug = True
    _init_logger(debug)

    adapter = _configure_adapter()

    _init_influx(adapter)


if __name__ == "__main__":
    start()
