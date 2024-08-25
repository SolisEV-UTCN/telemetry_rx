import logging
import socket

from cantools.database import Database
from influxdb_client import InfluxDBClient, Point


def start_udp_socket(client: InfluxDBClient, dbc: Database, bucket: str, address: str, port: int):
    # Init Write API bucket
    writer = client.write_api()

    # Init UDP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((address, port))
    server.listen()
    logging.info("Server is listening on {address}:{port}")

    while True:
        # Open socket
        conn, _addr = server.accept()
        try:
            logging.info("Connection from {_addr}")
            data = conn.recv(10)
            point = process_data(dbc, data)
            if point is not None:
                logging.debug("Data received: {point}")
                writer.write(bucket, point)
        except KeyboardInterrupt:
            break
        finally:
            conn.close()
            writer.close()
            server.close()


def process_data(dbc: Database, data: list[bytes]) -> Point | None:
    """Data is received over UDP in 10 bytes, intel order.
    A message consists of 2 bytes of frame ID and 8 bytes of data.
    Ex.:| 04 01 | 00 01 02 03 04 05 06 07 |
        |   ID  |           DATA          |
    """
    return Point()
