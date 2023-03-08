from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
# https://github.com/influxdata/influxdb-client-python
# https://stackoverflow.com/questions/69352264/problems-setting-up-a-docker-based-influxdb-grafana-network
import time

bucket = "solis_telemetry"

client = InfluxDBClient(url="http://localhost:8086",
                        token="rMS0Sj5nyh3Yh7VeZqAG9WI-1pgoakv0QDX-tkPrkQidJyajczyZtg8BEs_Aqzrv9DvHCRE3KyeJh9IV-OmMhw==", org="642dbcccb861ec05")

write_api = client.write_api(write_options=SYNCHRONOUS)

for x in range(50):
    p = Point("my_measurement").tag("location", "Solis").field("test", x)
    write_api.write(bucket=bucket, record=p)
    time.sleep(3)


# query
# from(bucket: "solis_telemetry")
# | > range(start: v.timeRangeStart, stop: v.timeRangeStop)
# | > filter(fn: (r)=>
#            r._measurement == "my_measurement" and
#            r._field == "test"
#            )

# query for filter by value
# // v.bucket, v.timeRangeStart, and v.timeRange stop are all variables supported by the flux plugin and influxdb
# from(bucket: v.bucket)
#   |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
#   |> filter(fn: (r) => r["_value"] >= 10 and r["_value"] <= 20)


# query for group by

# // v.windowPeriod is a variable referring to the current optimized window period (currently: $interval)
# from(bucket: v.bucket)
#   |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
#   |> filter(fn: (r) => r["_measurement"] == "measurement1" or r["_measurement"] =~ /^.*?regex.*$/)
#   |> filter(fn: (r) => r["_field"] == "field2" or r["_field"] =~ /^.*?regex.*$/)
#   |> aggregateWindow(every: v.windowPeriod, fn: mean|median|max|count|derivative|sum)
#   |> yield(name: "some-name")
