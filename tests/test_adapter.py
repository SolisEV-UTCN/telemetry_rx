import struct
import tempfile
from pathlib import Path

import cantools

from telemetry_rx.adapters import UsbAdapter, UdpAdapter

PWD = Path(__file__).parents[1].absolute()
CAN_MAPPING = Path(PWD, "telemetry_rx", "config", "Solis-EV4.dbc")


def test_validate_crc():
    adapter = UsbAdapter(CAN_MAPPING)

    # Test valid input
    data = bytes([0xDE, 0xAD, 0xBE, 0xEF])
    expected_crc = 0x81DA1A18
    assert adapter.validate_crc(expected_crc, data)

    # Test invalid input
    expected_crc = 0x0
    assert not adapter.validate_crc(expected_crc, data)


def test_parse_data():
    adapter = UsbAdapter(CAN_MAPPING)
    # Order intel: Float 1 = 5, Float 2 = 120
    message = bytes([0x00, 0x00, 0xA0, 0x40, 0x00, 0x00, 0xF0, 0x42])

    # Test valid input
    point = adapter.parse_data(0x402, message)
    assert point is not None
    assert point.__dict__["_name"] == "solar_vehicle"
    assert point.__dict__["_tags"]["ecu"] == "MotorController"
    assert point.__dict__["_fields"]["MC_BusCurrent"] == 120.0
    assert point.__dict__["_fields"]["MC_BusVoltage"] == 5.0

    # Test invalid input
    point = adapter.parse_data(0x999, message)
    assert point is None


def test_listen_data():
    dbc = cantools.db.load_file(CAN_MAPPING, database_format="dbc", encoding="cp1252", cache_dir=tempfile.gettempdir())
    adapter = UdpAdapter(address='0.0.0.0:8081', dbc=dbc)

    data = bytes([0x66, 0xCB, 0x65, 0x6F, 0x04, 0x01, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07])
    point = adapter.process_data(dbc, data)

    assert point is not None

    assert point.__dict__["_name"] == "CAN_DATA"
    assert point.__dict__["_tags"]["frame_id"] == 0x0401
    # checking signal values (actual values are derived from bytes array and conv. to integers)
    assert point.__dict__["_fields"]["MC_ActiveMotor"] == 1284
    assert point.__dict__["_fields"]["MC_ErrorFlags"] == 770
    assert point.__dict__["_fields"]["MC_LimitFlags"] == 256
    assert point.__dict__["_fields"]["MC_ReceiveErrorCount"] == 7
    assert point.__dict__["_fields"]["MC_TransmitErrorCount"] == 6

    # checking timestamp value
    assert point.__dict__["_time"] == struct.unpack('!I', bytes([0x66, 0xCB, 0x65, 0x6F]))[0]
