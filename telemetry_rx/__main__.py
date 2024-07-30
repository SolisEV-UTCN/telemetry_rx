if __name__ == "__main__":
    from telemetry_rx.cli import common
    from telemetry_rx.utils import InfluxCreds

    common(InfluxCreds("", "", "", ""))
