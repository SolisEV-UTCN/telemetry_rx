'''Testing Xbee transmission and insertion into InfluxDB. Receives frames of 12 bytes (see ref) with start and end-bytes.'''

import serial
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS
# https://github.com/influxdata/influxdb-client-python
# https://stackoverflow.com/questions/69352264/problems-setting-up-a-docker-based-influxdb-grafana-network
import time

# bucket-ul trebuie sa se numeasca la fel ca si bucket-ul creat de tine cand ai facut setup de influxdb
TOKEN = "BZIdcQpCDMuKx21_PNvKsJgI5LUbKmpblRcPnxH0Avva_0n7hQocc8mfi7H4KFVNZHkeSWyniSqmkeuBk6d3Qw=="
ORG = '5e2af96534acf5d7'
BUCKET = "kart_telemetry"
T_OFFSET = -40
CV_FACTOR = 0.001
PV_FACTOR = 0.1

# token-ul trebuie sa fie cel generat de API Keys de pe influxdb, iar org trebuie sa fie numele organizatiei alese
client = InfluxDBClient(url="http://localhost:8086", token=TOKEN, org=ORG)
write_api = client.write_api(write_options=ASYNCHRONOUS)

ser = serial.Serial()
ser.baudrate = 57600
ser.port = 'COM4'
ser.timeout = 1
print(ser)

ser.open()

start_byte_received = False
data = []
rx_frames = 0
incmplt_frame_error = 0
err = 0
CAN_ID = {
    0x18B4: "Temperatures",  # dec 6324
    0x18C8: "Cell_Voltage_1_4",  # dec 6344
    0x18C9: "Cell_Voltage_5_8",
    0x18CA: "Cell_Voltage_9_12",
    0x18CB: "Cell_Voltage_13_14",
    0x18FF: "Pack_State"  # dec 6399
}

while True:
    # Check if there is data available to read
    if ser.in_waiting > 0:
        # Read the next byte
        byte = ser.read()
        # Check if we have received the start byte
        if byte == b'\x01':
            if start_byte_received:
                # Two consecutive start bytes received means loss of end byte.
                print("Incomplete package error:", data)
            # Clear data buffer
            start_byte_received = True
            data = []
        # Check if we have received the end byte
        elif byte == b'\x00' and start_byte_received:
            # Print the data
            print("Received data:", data)
            # print("Id:", (data[0] << 8) | data[1])
            # Identify frame based on can ID
            if CAN_ID[(data[0] << 8) | data[1]] == "Temperatures":
                # Check number of bytes
                if (len(data) == 8):
                    # Create datapoint
                    point = (
                        Point("Battery")
                        .tag("Module", "BMS")
                        .field("T_MOS", data[2])
                        .field("T_BAL", data[3])
                        .field("Cell_Temp_1", data[4] + T_OFFSET)
                        .field("Cell_Temp_2", data[5] + T_OFFSET)
                        .field("Cell_Temp_3", data[6] + T_OFFSET)
                        .field("Cell_Temp_4", data[7] + T_OFFSET)
                    )
                else:
                    incmplt_frame_error += 1
                    err = 1
            elif CAN_ID[(data[0] << 8) | data[1]] == "Cell_Voltage_1_4":
                if (len(data) == 10):
                    # Create datapoint
                    point = (
                        Point("Battery")
                        .tag("Module", "BMS")
                        .field("Cell_Voltage_1", ((data[2] << 8) | data[3]) * CV_FACTOR)
                        .field("Cell_Voltage_2", ((data[4] << 8) | data[5]) * CV_FACTOR)
                        .field("Cell_Voltage_3", ((data[6] << 8) | data[7]) * CV_FACTOR)
                        .field("Cell_Voltage_4", ((data[8] << 8) | data[9]) * CV_FACTOR)
                    )
                else:
                    incmplt_frame_error += 1
                    err = 1
            elif CAN_ID[(data[0] << 8) | data[1]] == "Cell_Voltage_5_8":
                if (len(data) == 10):
                    # Create datapoint
                    point = (
                        Point("Battery")
                        .tag("Module", "BMS")
                        .field("Cell_Voltage_5", ((data[2] << 8) | data[3]) * CV_FACTOR)
                        .field("Cell_Voltage_6", ((data[4] << 8) | data[5]) * CV_FACTOR)
                        .field("Cell_Voltage_7", ((data[6] << 8) | data[7]) * CV_FACTOR)
                        .field("Cell_Voltage_8", ((data[8] << 8) | data[9]) * CV_FACTOR)
                    )
                else:
                    incmplt_frame_error += 1
                    err = 1
            elif CAN_ID[(data[0] << 8) | data[1]] == "Cell_Voltage_9_12":
                if (len(data) == 10):
                    # Create datapoint
                    point = (
                        Point("Battery")
                        .tag("Module", "BMS")
                        .field("Cell_Voltage_9", ((data[2] << 8) | data[3]) * CV_FACTOR)
                        .field("Cell_Voltage_10", ((data[4] << 8) | data[5]) * CV_FACTOR)
                        .field("Cell_Voltage_11", ((data[6] << 8) | data[7]) * CV_FACTOR)
                        .field("Cell_Voltage_12", ((data[8] << 8) | data[9]) * CV_FACTOR)
                    )
                else:
                    incmplt_frame_error += 1
                    err = 1
            elif CAN_ID[(data[0] << 8) | data[1]] == "Cell_Voltage_13_14":
                if (len(data) == 6):
                    # Create datapoint
                    point = (
                        Point("Battery")
                        .tag("Module", "BMS")
                        .field("Cell_Voltage_13", ((data[2] << 8) | data[3]) * CV_FACTOR)
                        .field("Cell_Voltage_14", ((data[4] << 8) | data[5]) * CV_FACTOR)
                    )
                else:
                    incmplt_frame_error += 1
                    err = 1
            elif CAN_ID[(data[0] << 8) | data[1]] == "Pack_State":
                if (len(data) == 3):
                    # Create datapoint
                    point = (
                        Point("Battery")
                        .tag("Module", "BMS")
                        .field("Pack_Voltage", data[2] * PV_FACTOR)
                    )
                else:
                    incmplt_frame_error += 1
                    err = 1
            if not err:
                # Write data point to influx
                write_api.write(bucket=BUCKET, record=point)
            else:
                # Reset error flag
                err = 0
            rx_frames += 1
            print(rx_frames, end=", ")
            print(incmplt_frame_error)
            # Reset the flag and data buffer
            start_byte_received = False
            data = b''
        elif start_byte_received:
            # Append the byte to the data buffer
            data.append(int.from_bytes(byte, "big", signed=False))

    # Wait for a short time to avoid busy-waiting
    # select.select([ser], [], [], 0.1)
    # time.sleep(0.1)
