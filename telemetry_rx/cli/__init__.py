import os

from telemetry_rx.cli.run import init_influx, init_logger, configure_adapter


def main():
    """Main script."""
    debug = os.environ.get("RUN_MODE", "release").lower()
    if debug == "release":
        debug = False
    else:
        debug = True
    init_logger(debug)

    adapter = configure_adapter()

    init_influx(adapter)
