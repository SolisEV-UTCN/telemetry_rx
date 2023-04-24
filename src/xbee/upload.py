from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS
# https://github.com/influxdata/influxdb-client-python
# https://stackoverflow.com/questions/69352264/problems-setting-up-a-docker-based-influxdb-grafana-network
import time

bucket = "solis_telemetry"

client = InfluxDBClient(url="http://localhost:8086",
                        token="rMS0Sj5nyh3Yh7VeZqAG9WI-1pgoakv0QDX-tkPrkQidJyajczyZtg8BEs_Aqzrv9DvHCRE3KyeJh9IV-OmMhw==", org="642dbcccb861ec05")

write_api = client.write_api(write_options=ASYNCHRONOUS)

for x in range(50):
    p = Point("my_measurement").tag("location", "Solis").field("test", x)
    write_api.write(bucket=bucket, record=p)
    time.sleep(3)