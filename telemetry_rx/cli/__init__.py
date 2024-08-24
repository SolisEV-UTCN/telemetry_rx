from datetime import datetime, UTC
from pathlib import Path
import logging
import os
import sys

import click

from telemetry_rx.cli.run import configure_adapter, setup_main
from telemetry_rx.cli.parse import parse
from telemetry_rx.utils import InfluxCreds

import flask


# Default values
INFLUX_BUCKET = datetime.now(UTC).strftime("record_%Y_%m_%d-%H:%M:%S")
INFLUX_ORG = "solis"
INFLUX_URL = "http://influx:8086"

# Common paths
PWD = Path(__file__).parent.absolute()
CAN_MAPPING = Path(PWD, "config", "Solis-EV4.dbc")
OFFLINE_DATA = Path(PWD, "config", "Session_2")

# Click types
TYPE_ADAPTER = click.Choice(["USB", "TCP"], case_sensitive=False)
TYPE_R_PATH = click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path)
TYPE_DIR = click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path)


# !Flask Server info!
app = flask.Flask(__name__)

@app.route('/')
def base():
    return flask.jsonify({"message":"flask server running.."}), 200

@app.route('/data', methods=['POST'])
def get_data():
    data = flask.request.json
    return flask.jsonify({"data": data}), 201


# fmt: off
@click.group()
@click.option("--influx-bucket", default=INFLUX_BUCKET, envvar="INFLUX_BUCKET", show_envvar=True, allow_from_autoenv=True, type=str, help="Name of bucket for writting extracted CAN data.")
@click.option("--influx-org", default=INFLUX_ORG, envvar="INFLUX_ORG", show_envvar=True, allow_from_autoenv=True, type=str, help="Name of organization in InfluxDB.")
@click.option("-t", "--influx-token", envvar="INFLUX_TOKEN", show_envvar=True, allow_from_autoenv=True, type=str, help="String for an InfluxDB API token.\nGenerated token must contain write permissions.")
@click.option("--influx-token-file", envvar="INFLUX_TOKEN_FILE", show_envvar=True, allow_from_autoenv=True, type=TYPE_R_PATH, help="File path with a InfluxDB API token.\nGenerated token must contain write permissions.")
@click.option("--influx-url", default=INFLUX_URL, envvar="INFLUX_URL", show_envvar=True, allow_from_autoenv=True, type=str, help="InfluxDB entrypoint.")
@click.option("-v", "--verbose", count=True)
@click.pass_context
def common(ctx: click.Context, influx_bucket: str, influx_org: str, influx_token: str | None, influx_token_file: Path | None, influx_url: str, verbose: int):
# fmt: on
    """ Script for running telemetry. """
    ctx.ensure_object(InfluxCreds)

    _verbose(verbose)

    influx_token = influx_token or "token"
    influx_token_file = influx_token_file or "token_file"

    ctx.obj = _credentials(influx_bucket, influx_org, influx_token, influx_token_file, influx_url)



@common.command("run")
@click.option("--adapter", type=TYPE_ADAPTER, default="USB")
@click.option("--dbc", default=CAN_MAPPING, type=TYPE_R_PATH)
@click.pass_context
def collect_data(ctx: click.Context, adapter: str, dbc: Path):
    """ Collect live CAN data through an adapter. """
    creds = ctx.find_object(InfluxCreds)

    adapter = configure_adapter(adapter, dbc)
    setup_main(adapter, creds)


@common.command("parse")
@click.option("--path", default=OFFLINE_DATA, type=TYPE_DIR)
@click.pass_context
def parse_file(ctx: click.Context, path: Path):
    """ Parse file with locally stored CAN data. """
    creds = ctx.find_object(InfluxCreds)

    parse(creds, path)

@common.command("flask_server")
@click.pass_context
def start_flask_server(ctx: click.Context) -> None:
    """Start Flask server"""
    app.run(host="0.0.0.0", port=5000, debug=True)

def _credentials(influx_bucket: str, influx_org: str, influx_token: str | None, influx_token_file: Path | None, influx_url: str,) -> InfluxCreds:
    """Get InfluxDB API credentials."""
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

    return InfluxCreds(influx_bucket, influx_org, token, influx_url)


def _verbose(level: int) -> None:
    """Format logger to be pretty."""
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
