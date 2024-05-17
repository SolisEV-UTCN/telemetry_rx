from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision
from typing import Dict, List, Tuple
from datetime import datetime, timedelta, timezone

DATE_CONVERSION: List[
    Tuple[str, str, str]
]  # datetime_start: str, datetime_end: str, datetime_convert: str
DATE_CONVERSION = [
    (
        "2023-10-21T00:47:52Z",
        "2023-10-21T06:54:47Z",
        "2023-10-22T08:40:01ACST",
    ),  # Day 1
    (
        "2023-10-21T07:50:15Z",
        "2023-10-21T09:05:48Z",
        "2023-10-23T10:25:00ACST",
    ),  # Day 2
    ("2023-10-21T09:05:49Z", "2023-10-21T10:41:28Z", "2023-10-23T15:02:00ACST"),
    (
        "2023-10-21T10:48:54Z",
        "2023-10-21T15:47:35Z",
        "2023-10-24T10:15:00ACST",
    ),  # Day 3
    (
        "2023-10-21T15:51:56Z",
        "2023-10-21T16:05:29Z",
        "2023-10-25T10:10:00ACST",
    ),  # Day 4
    ("2023-10-21T16:16:11Z", "2023-10-21T17:05:05Z", "2023-10-25T10:40:00ACST"),
    ("2023-10-21T17:48:20Z", "2023-10-21T21:10:27Z", "2023-10-25T11:30:00ACST"),
    (
        "2023-10-21T21:49:12Z",
        "2023-10-21T23:03:53Z",
        "2023-10-26T11:56:50ACDT",
    ),  # Day 5
    (
        "2023-10-21T23:04:09Z",
        "2023-10-22T05:29:00Z",
        "2023-10-27T10:47:30ACDT",
    ),  # Day 6
]


def acst_to_utc(str: str, daylight=0) -> str:
    # Define timezones
    acst_offset = timedelta(
        hours=9.5 + daylight
    )  # Australian Central Standard Time (ACST) offset from UTC
    acst_timezone = timezone(acst_offset)
    utc_timezone = timezone.utc

    # Convert input string to datetime object in ACST
    acst_datetime = datetime.strptime(str, "%Y-%m-%dT%H:%M:%S")
    acst_datetime = acst_datetime.replace(tzinfo=acst_timezone)

    # Convert ACST datetime to UTC
    utc_datetime = acst_datetime.astimezone(utc_timezone)

    # Format UTC datetime as string
    utc_datetime_str = utc_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    return utc_datetime_str


def utc_to_acst(str: str, daylight=0) -> str:
    # Define timezones
    acst_offset = timedelta(
        hours=9.5 + daylight
    )  # Australian Central Standard Time (ACST) offset from UTC
    acst_timezone = timezone(acst_offset)
    utc_timezone = timezone.utc

    # Convert input string to datetime object in UTC
    utc_datetime = datetime.strptime(str, "%Y-%m-%dT%H:%M:%S")
    utc_datetime = utc_datetime.replace(tzinfo=utc_timezone)

    # Convert UTC datetime to ACST
    acst_datetime = utc_datetime.astimezone(acst_timezone)

    # Format ACST datetime as string
    acst_datetime_str = acst_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    return acst_datetime_str


if __name__ == "__main__":
    URL_CLIENT = "127.0.0.1:8080"
    URL_SERVER = "https://us-east-1-1.aws.cloud2.influxdata.com"
    TOKEN_CLIENT = "AdpIvvaMk9ojGazqWzYZ8oaEBCx4bLpWfWm0wkPiMp_XzG-BvgPKqEbvt1LGs08DP93h2IFkvBwtry_FnCy_6A=="
    TOKEN_SERVER = "xAxQVd38rOvkCQTQOawG-SllOqrbwVoxSg0FiPKfZs1O8upoPh2miS4eBgYOXCLKyDfbJom9qdkxgKyisewJYQ=="
    ORG_CLIENT = "solis"
    ORG_SERVER = "Telemetry Team"

    buckets = ["BMU", "Dashboard", "INVERTOR", "MPPT"]

    with InfluxDBClient(
        URL_CLIENT, TOKEN_CLIENT, org=ORG_CLIENT
    ) as client, InfluxDBClient(URL_SERVER, TOKEN_SERVER, org=ORG_SERVER) as server:
        reader = client.query_api()
        for bucket in buckets:
            points = []
            for datetime_start, datetime_end, datetime_convert in DATE_CONVERSION:
                q = f'from(bucket:"{bucket}") |> range(start:{datetime_start}, stop:{datetime_end})'
                tabels = reader.query(q)
                values = tabels.to_values(columns=["_time", "_field", "_value"])
                points.extend(values)
            print(f"{bucket}:{len(points)}")
