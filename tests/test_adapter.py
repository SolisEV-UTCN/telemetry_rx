from pathlib import Path


from telemetry_rx.adapters import UsbAdapter


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
