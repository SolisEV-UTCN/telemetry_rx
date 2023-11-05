from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision
from typing import Dict, List, Tuple
import datetime
import dateutil
import itertools


DOWNLOAD_URL = "127.0.0.1:8086"
DOWNLOAD_TOKEN = "AdpIvvaMk9ojGazqWzYZ8oaEBCx4bLpWfWm0wkPiMp_XzG-BvgPKqEbvt1LGs08DP93h2IFkvBwtry_FnCy_6A=="
DOWNLOAD_ORG = "solis"
UPLOAD_URL = ""
UPLOAD_TOKEN = ""
UPLOAD_ORG = "BWSC"

def download_data():
    START_TIME = datetime.datetime(2023, 9, 10, 8, 0, 0, tzinfo=dateutil.tz.gettz("Australia/Darwin"))
    time = int(START_TIME.timestamp())
    with InfluxDBClient(url=DOWNLOAD_URL, token=DOWNLOAD_TOKEN, org=DOWNLOAD_ORG) as local:
        query_api = local.query_api()

        # Get distance, sum it if reset
        distances = query_api.query(f'from(bucket: "INVERTOR") |> range(start: {time}) |> filter(fn: (r) => r._field == "odometer") |> aggregateWindow(every: 1m, fn: max, createEmpty: false)').to_values(columns=["_time", "_value"])

        odometer = []
        is_off = False
        offset = 0
        prev = distances[0][1]
        for distance in distances[1:]:
            if distance[1] < prev - offset:
                offset = prev
                is_off = True
            if is_off:
                distance[1] += offset
            prev = distance[1]
            odometer.append([distance[0], distance[1]])

        # Trim data if needed
        limit = len(odometer)
                
        # Get solar energy
        mppt_1_vol = query_api.query(f'from(bucket: "MPPT") |> range(start: {time}) |> filter(fn: (r) => r._field == "input_front_voltage") |> aggregateWindow(every: 1m, fn: mean, createEmpty: false) |> limit(n: {limit})').to_values(columns=["_time", "_value"])
        mppt_2_vol = query_api.query(f'from(bucket: "MPPT") |> range(start: {time}) |> filter(fn: (r) => r._field == "input_back_voltage") |> aggregateWindow(every: 1m, fn: mean, createEmpty: false) |> limit(n: {limit})').to_values(columns=["_time", "_value"])
        mppt_1_cur = query_api.query(f'from(bucket: "MPPT") |> range(start: {time}) |> filter(fn: (r) => r._field == "input_front_current") |> aggregateWindow(every: 1m, fn: mean, createEmpty: false) |> limit(n: {limit})').to_values(columns=["_time", "_value"])
        mppt_2_cur = query_api.query(f'from(bucket: "MPPT") |> range(start: {time}) |> filter(fn: (r) => r._field == "input_back_current") |> aggregateWindow(every: 1m, fn: mean, createEmpty: false) |> limit(n: {limit})').to_values(columns=["_time", "_value"])
        mppts = []
        for v1, v2, c1, c2 in zip(mppt_1_vol, mppt_2_vol, mppt_1_cur, mppt_2_cur):
            mppts.append(v1[1] * c1[1] + v2[1] * c2[1])
        mppts = itertools.accumulate(mppts)

        # Get battery energy
        bus_voltages = query_api.query(f'from(bucket: "INVERTOR") |> range(start: {time}) |> filter(fn: (r) => r._field == "bus_voltage") |> aggregateWindow(every: 1m, fn: mean, createEmpty: false) |> limit(n: {limit})').to_values(columns=["_time", "_value"])
        bus_currents = query_api.query(f'from(bucket: "INVERTOR") |> range(start: {time}) |> filter(fn: (r) => r._field == "bus_current") |> aggregateWindow(every: 1m, fn: mean, createEmpty: false) |> limit(n: {limit})').to_values(columns=["_time", "_value"])
        battery = []
        for vol, cur in zip(bus_voltages, bus_currents):
            battery.append(vol[1] * cur[1])
        battery = itertools.accumulate(battery)

        # Combine all
        for distance, solarEnergy, batteryEnergy in zip(odometer, mppts, battery):
            yield {"distance": (distance[1], distance[0]), "solarEnergy": (solarEnergy, 0), "batteryEnergy": (batteryEnergy, 0)}


def upload_data(data: List[Dict[str, Tuple[float, float]]]):
    EVENT = "BWSC2023"
    CLASS = "Challenger"
    TEAM  = "TUCN Solar Racing Team"
    CAR   = "SOLIS"
    SHORT = "TUCN Solar"

    with InfluxDBClient(url=UPLOAD_URL, token=UPLOAD_TOKEN, org=UPLOAD_ORG) as remote:
        write_api = remote.write_api(write_options=SYNCHRONOUS)
        for datum in data:
            point = Point("telemetry")

            # Required tags
            point.tag("event", EVENT)
            point.tag("class", CLASS)
            point.tag("team", TEAM)
            point.tag("car", CAR)
            point.tag("shortname", SHORT)

            # Required fields
            point.field("distance", datum["distance"][0])
            point.field("solarEnergy", datum["solarEnergy"][0])
            point.field("batteryEnergy", datum["batteryEnergy"][0])

            # Timestamp
            point.time(datum["distance"][1], write_precision=WritePrecision.S)

            write_api.write(bucket="SOLIS", write_precision=WritePrecision.S, record=point)


if __name__ == "__main__":
    data = list(download_data())
    upload_data(data)
