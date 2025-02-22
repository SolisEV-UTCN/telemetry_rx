import logging
import os
import sys
import tempfile
from datetime import datetime, UTC
from pathlib import Path

import cantools
import click
from influxdb_client import InfluxDBClient

from telemetry_rx.cli.listen import configure_adapter, setup_main
from telemetry_rx.cli.parse import parse
from telemetry_rx.utils import AppContext


# Default values
INFLUX_BUCKET = datetime.now(UTC).strftime("record_%Y_%m_%d-%H:%M:%S")
INFLUX_ORG = "solis"
INFLUX_URL = "http://influx:8086"

# Common paths
CAN_MAPPING = Path(__file__).parents[1].absolute() / "config" / "Solis-EV4.dbc"
OFFLINE_DATA = Path(__file__).parents[2].absolute() / "tests" / "serial_input"

# Click types
TYPE_ADAPTER = click.Choice(["TCP", "USB", "UDP"], case_sensitive=False)
TYPE_R_PATH = click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path)
TYPE_DIR = click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path)

# Help text
H_URL = "Entrypoint to InfluxDB server."
H_ORG = "Organization in InfluxDB."
H_TOKEN = "InfluxDB API token. Token must have write permissions."
H_TOKEN_FILE = "Path to a file with an InfluxDB API token. Token must have write permissions."
H_BUCKET = "Bucket name for writting extracted CAN data."
H_DBC = "Path to CAN bus database."


# fmt: off
@click.group()
@click.pass_context
@click.option("--influx-url", default=INFLUX_URL, envvar="INFLUX_URL", allow_from_autoenv=True, type=str, help=H_URL)
@click.option("--influx-org", default=INFLUX_ORG, envvar="INFLUX_ORG", allow_from_autoenv=True, type=str, help=H_ORG)
@click.option("--influx-token", envvar="INFLUX_TOKEN", allow_from_autoenv=True, type=str, help=H_TOKEN)
@click.option("--influx-token-file", envvar="INFLUX_TOKEN_FILE", allow_from_autoenv=True, type=TYPE_R_PATH, help=H_TOKEN_FILE)
@click.option("--influx-bucket", default=INFLUX_BUCKET, envvar="INFLUX_BUCKET", allow_from_autoenv=True, type=str, help=H_BUCKET)
@click.option("--dbc", default=CAN_MAPPING, type=TYPE_R_PATH, help=H_DBC)
@click.option("-v", "--verbose", count=True)
def common(ctx: click.Context, influx_url: str, influx_org: str, influx_token: str | None, influx_token_file: Path | None, influx_bucket: str, dbc: Path, verbose: int):
# fmt: on
    """ Script for running telemetry. """
    _verbose(verbose)

    # Debug info
    logging.debug(f"INFLUX_BUCKET={influx_bucket}")
    logging.debug(f"INFLUX_ORG={influx_org}")
    logging.debug(f"INFLUX_TOKEN={influx_token}")
    logging.debug(f"INFLUX_TOKEN_FILE={influx_token_file}")
    logging.debug(f"INFLUX_URL={influx_url}")
    logging.debug(f"DBC_PATH={dbc}")

    # Initialize an InfluxDB client
    client = _influx_client(influx_org, influx_token, influx_token_file, influx_url)
    if not client.ping():
        logging.error("Couldn't establish connection to InfluxDB.")
    else:
        # Create bucket if it doesn't exist
        buckets_api = client.buckets_api()
        if not buckets_api.find_bucket_by_name(influx_bucket):
            logging.info(f"Creating {influx_bucket} bucket.")
            bucket = buckets_api.create_bucket(bucket_name=influx_bucket)
            # Make `tests` bucket with retention policy of 3 days
            if influx_bucket == "tests":
                bucket.retention_rules = "3d"
                buckets_api.update_bucket(bucket)

    # Load DBC
    try:
        dbc = cantools.db.load_file(dbc, database_format="dbc", encoding="cp1252", cache_dir=tempfile.gettempdir())
    except cantools.db.UnsupportedDatabaseFormatError:
        logging.error("Failed to read DBC file.")

    ctx.ensure_object(AppContext)
    ctx.obj = AppContext(dbc=dbc, client=client, bucket_name=influx_bucket)


@common.command("listen")
@click.pass_obj
@click.option("--adapter", type=TYPE_ADAPTER, default="USB", envvar="SOLIS_ADAPTER")
@click.option("--address", default="/dev/ttyUSB0", envvar="SOLIS_ADDRESS", help="Connection port for USB adapter. Bind address for TCP adapter.")
def collect_data(ctx: AppContext, adapter: str, address: str):
    """ Collect live CAN data through an adapter. """
    logging.debug(f"Adapter: {adapter}")
    logging.debug(f"Address: {address}")

    adapter = configure_adapter(adapter, ctx.dbc, address)
    setup_main(ctx.client, adapter, ctx.bucket_name)

    _clean_up(ctx.client)


@common.command("parse")
@click.pass_obj
@click.option("--path", default=OFFLINE_DATA, type=TYPE_DIR)
def parse_file(ctx: AppContext, path: Path):
    """ Parse file with locally stored CAN data. """
    parse(ctx.client, ctx.dbc, path, ctx.bucket_name)

    _clean_up(ctx.client)


def _clean_up(client: InfluxDBClient):
    client.close()


def _influx_client(influx_org: str, influx_token: str | None, influx_token_file: Path | None, influx_url: str) -> InfluxDBClient:
    """ Get InfluxDB API credentials. """
    # Get token from string
    if influx_token is not None:
        token = influx_token

    # Check if token is contained within a file path
    elif influx_token_file is not None and os.path.exists(influx_token_file):
        file = open(Path(influx_token_file), "rt")
        token = file.readline().strip()
        file.close()
        logging.debug(f"INFLUX_TOKEN_FILE contains '{token}'")

    # Raise error otherwise
    else:
        raise ValueError(
            "Provide INFLUX_TOKEN or INFLUX_TOKEN_FILE. Run command with -h flag for more info."
        )

    return InfluxDBClient(influx_url, token, org=influx_org)


def _verbose(level: int) -> None:
    """ Format logger to be pretty. """
    # Logger scaffolding
    formatter = logging.Formatter("[{levelname}]{filename}:{message}", style="{")
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()

    # Set level of debug info
    if level >= 1:
        handler.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
        root.setLevel(logging.INFO)

    root.addHandler(handler)
