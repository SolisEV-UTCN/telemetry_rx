from pathlib import Path
import logging

from influxdb_client import InfluxDBClient, WriteOptions, WritePrecision
from influxdb_client.client.util.multiprocessing_helper import MultiprocessingWriter

from telemetry_rx.adapters import Adapter, TcpAdapter, UsbAdapter
from telemetry_rx.utils import AppState, InfluxCreds


def configure_adapter(adapter: str, dbc_path: Path) -> Adapter:
    """Select adapter to medium where the data will arrive."""
    adapter = adapter.upper()

    if adapter == "USB":
        logging.info("USB adapter selected.")
        reader = UsbAdapter(dbc_path)

    elif adapter == "TCP":
        logging.info("TCP adapter selected.")
        reader = TcpAdapter(dbc_path)

    else:
        logging.debug(f"INPUT_ADAPTER={adapter}")
        logging.error("No adapter selected.")
        raise ValueError("Incorrect adapter selected.")

    return reader


def setup_main(reader: Adapter, credentials: InfluxCreds) -> None:
    """Init bucket for recording, than monitor CAN traffic."""
    # Debug info
    logging.debug(f"INFLUX_BUCKET={credentials.bucket}")
    logging.debug(f"INFLUX_ORG={credentials.org}")
    logging.debug(f"INFLUX_URL={credentials.url}")

    # Create bucket if it doesn't exists
    with InfluxDBClient(url=credentials.url, token=credentials.token, org=credentials.org) as influxdb_client:
        buckets_api = influxdb_client.buckets_api()
        if not buckets_api.find_bucket_by_name(credentials.bucket):
            logging.info(f"Creating {credentials.bucket} bucket.")
            buckets_api.create_bucket(bucket_name=credentials.bucket)

    # Write points in batches to InfluxDB
    with MultiprocessingWriter(
        url=credentials.url,
        token=credentials.token,
        org=credentials.org,
        write_options=WriteOptions(batch_size=5000),
    ) as writer:
        main_loop(reader, writer, credentials.bucket)


def main_loop(reader: Adapter, writer: MultiprocessingWriter, bucket: str):
    # State machine
    state = AppState.INIT
    while state != AppState.ERROR:
        # Initialization state
        if state is AppState.INIT:
            state = reader.init_device()
            continue

        # Deinitialization state
        elif state is AppState.STOP:
            reader.deinit_device()
            logging.info("Closing application.")
            break

        try:
            # Continious reading
            for data in reader.read_data():
                logging.debug(f"Writting to {bucket}: {data}")
                writer.write(bucket=bucket, record=data, write_precision=WritePrecision.NS)

        except KeyboardInterrupt:
            state = AppState.STOP
        except Exception as e:
            logging.critical(f"Unhandeled exception: {e}")
            state = AppState.STOP
