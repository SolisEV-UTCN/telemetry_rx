import logging

from cantools.database import Database
from influxdb_client import InfluxDBClient, WriteOptions, WritePrecision
from influxdb_client.client.util.multiprocessing_helper import MultiprocessingWriter

from telemetry_rx.adapters import Adapter, UdpAdapter, UsbAdapter
from telemetry_rx.utils import AppState


def configure_adapter(adapter: str, dbc: Database, address: str) -> Adapter:
    """Select adapter to medium where the data will arrive."""
    adapter = adapter.upper()

    if adapter == "USB":
        logging.info("USB adapter selected.")
        reader = UsbAdapter(address, dbc)

    elif adapter == "UDP":
        logging.info("UDP adapter selected.")
        reader = UdpAdapter(address, dbc)

    else:
        logging.debug(f"INPUT_ADAPTER={adapter}")
        logging.error("No adapter selected.")
        raise ValueError("Incorrect adapter selected.")

    return reader


def setup_main(client: InfluxDBClient, reader: Adapter, bucket: str) -> None:
    """Init bucket for recording, than monitor CAN traffic."""
    # Write points in batches to InfluxDB
    with MultiprocessingWriter(
        url=client.url,
        token=client.token,
        org=client.org,
        write_options=WriteOptions(batch_size=5000),
    ) as writer:
        main_loop(reader, writer, bucket)


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
