import logging

from cantools.database import Database
from influxdb_client import InfluxDBClient, WriteOptions, WritePrecision
from influxdb_client.client.util.multiprocessing_helper import MultiprocessingWriter

from telemetry_rx.adapters import Adapter, TcpAdapter, UdpAdapter, UsbAdapter
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

    elif adapter == "TCP":
        logging.info("TCP adapter selected.")
        reader = TcpAdapter(address, dbc)

    else:
        logging.debug(f"INPUT_ADAPTER={adapter}")
        logging.error("No adapter selected.")
        raise ValueError("Incorrect adapter selected.")

    return reader


def setup_main(client: InfluxDBClient, reader: Adapter, bucket: str) -> None:
    """Init bucket for recording, then monitor CAN traffic."""
    # Write points in batches to InfluxDB
    logging.info(f"Setting up InfluxDB writer with URL: {client.url}, org: {client.org}, bucket: {bucket}")
    with MultiprocessingWriter(
        url=client.url,
        token=client.token,
        org=client.org,
        write_options=WriteOptions(batch_size=5000),
    ) as writer:
        logging.info("InfluxDB writer initialized successfully")
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
                try:
                    logging.debug(f"Raw Point object: {data}")
                    logging.debug(f"Point object type: {type(data)}")
                    logging.debug(f"Point object dir: {dir(data)}")
                    logging.debug(f"Point object dict: {data.__dict__}")
                    logging.debug(f"Writing to {bucket}: {data}")
                    logging.debug(f"Point details - measurement: {data._name}, tags: {data._tags}, fields: {data._fields}, time: {data._time}")
                    
                    # Try to write the point
                    try:
                        writer.write(bucket=bucket, record=data, write_precision=WritePrecision.NS)
                        logging.debug("Successfully wrote point to InfluxDB")
                    except Exception as write_error:
                        logging.error(f"Failed to write point to InfluxDB: {str(write_error)}")
                        logging.error(f"Point that failed to write: {data}")
                        raise
                except Exception as e:
                    logging.error(f"Failed to process point: {str(e)}")
                    logging.error(f"Point object state: {data}")
                    raise

        except KeyboardInterrupt:
            state = AppState.STOP
        except Exception as e:
            logging.critical(f"Unhandeled exception: {e}")
            state = AppState.STOP
