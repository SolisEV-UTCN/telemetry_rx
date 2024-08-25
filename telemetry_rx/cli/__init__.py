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


# Default values
INFLUX_BUCKET = datetime.now(UTC).strftime("record_%Y_%m_%d-%H:%M:%S")
INFLUX_ORG = "solis"
INFLUX_URL = "http://influx:8086"

# Common paths
PWD = Path(__file__).parent.absolute()
CAN_MAPPING = Path(PWD, "config", "Solis-EV4.dbc")
OFFLINE_DATA = Path(PWD, "config", "Session_2")

# Click types
TYPE_ADAPTER = click.Choice(["USB", "UDP"], case_sensitive=False)
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
@click.option("--influx-url", default=INFLUX_URL, envvar="INFLUX_URL", allow_from_autoenv=True, type=str, help=H_URL)
@click.option("--influx-org", default=INFLUX_ORG, envvar="INFLUX_ORG", allow_from_autoenv=True, type=str, help=H_ORG)
@click.option("--influx-token", envvar="INFLUX_TOKEN", allow_from_autoenv=True, type=str, help=H_TOKEN)
@click.option("--influx-token-file", envvar="INFLUX_TOKEN_FILE", allow_from_autoenv=True, type=TYPE_R_PATH, help=H_TOKEN_FILE)
@click.option("--influx-bucket", default=INFLUX_BUCKET, envvar="INFLUX_BUCKET", allow_from_autoenv=True, type=str, help=H_BUCKET)
@click.option("--dbc", default=CAN_MAPPING, type=TYPE_R_PATH, help=H_DBC)
@click.option("-v", "--verbose", count=True)
@click.pass_context
def common(ctx: click.Context, influx_url: str, influx_org: str, influx_token: str | None, influx_token_file: Path | None, influx_bucket: str, dbc: Path, verbose: int):
# fmt: on
    """ Script for running telemetry. """
    ctx.ensure_object(dict)

    _verbose(verbose)

    # Debug info
    logging.debug(f"INFLUX_BUCKET={influx_bucket}")
    logging.debug(f"INFLUX_ORG={influx_org}")
    logging.debug(f"INFLUX_TOKEN={influx_token}")
    logging.debug(f"INFLUX_TOKEN_FILE={influx_token_file}")
    logging.debug(f"INFLUX_URL={influx_url}")
    logging.debug(f"DBC_PATH={dbc}")

    influx_token = influx_token or "token"
    influx_token_file = influx_token_file or "token_file"

    # Initialize an InfluxDB client
    client = _influx_client(influx_org, influx_token, influx_token_file, influx_url)
    if not client.ping():
        logging.error("Couldn't establish connection to InfluxDB.")
        return -1

    # Create bucket if it doesn't exists
    buckets_api = client.buckets_api()
    if not buckets_api.find_bucket_by_name(influx_bucket):
        logging.info(f"Creating {influx_bucket} bucket.")
        buckets_api.create_bucket(bucket_name=influx_bucket)

    # Load DBC
    try:
        dbc = cantools.db.load_file(dbc, database_format="dbc", encoding="cp1252", cache_dir=tempfile.gettempdir())
    except cantools.db.UnsupportedDatabaseFormatError:
        logging.error("Failed to read DBC file.")
        return -1

    ctx.obj = {
        "DBC": dbc,
        "INFLUX_CLIENT": client,
        "INFLUX_BUCKET": influx_bucket
    }


@common.command("listen")
@click.option("--adapter", type=TYPE_ADAPTER, default="USB")
@click.option("--address", default="/dev/ttyUSB0", help="Connection port for USB adapter. Bind address for UDP adapter.")
@click.pass_context
def collect_data(ctx: click.Context, adapter: str, address: str):
    """ Collect live CAN data through an adapter. """
    ctx = ctx.find_object(dict)

    adapter = configure_adapter(adapter, ctx["DBC"], address)
    setup_main(ctx["INFLUX_CLIENT"], adapter, ctx["INFLUX_BUCKET"])

    _clean_up(ctx["INFLUX_CLIENT"])


@common.command("parse")
@click.option("--path", default=OFFLINE_DATA, type=TYPE_DIR)
@click.pass_context
def parse_file(ctx: click.Context, path: Path):
    """ Parse file with locally stored CAN data. """
    ctx = ctx.find_object(dict)

    parse(ctx["INFLUX_CLIENT"], ctx["DBC"], path, ctx["INFLUX_BUCKET"])

    _clean_up(ctx["INFLUX_CLIENT"])


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

    # Raise error otherwise
    else:
        logging.debug(f"INFLUX_TOKEN_FILE={influx_token_file}")
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
    if level >= 2:
        handler.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
    elif level == 1:
        handler.setLevel(logging.INFO)
        root.setLevel(logging.INFO)
    else:
        handler.setLevel(logging.WARN)
        root.setLevel(logging.WARN)

    root.addHandler(handler)
