from pathlib import Path

import pytest

from telemetry_rx.adapters import UsbAdapter


PWD = Path(__file__).parents[1].absolute()
CAN_MAPPING = Path(PWD, "telemetry_rx", "config", "Solis-EV4.dbc")


def test_process_bytes():
    adapter = UsbAdapter(CAN_MAPPING)

    # Test valid input
    seq = bytes(
        [
            0xFE,  # Padding
            0x10,  # CAN header
            0x06,
            0x00,  # CAN data
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x44,  # CAN CRC
            0x81,
            0x1A,
            0x62,
            0x7F,  # Padding
        ]
    )
    out = adapter.process_bytes(seq)
    assert out[0] == 0x610
    assert out[1] == bytes([0, 0, 0, 0])
    assert out[2] == bytes([0, 0, 0, 0])
    assert out[3] == 0x621A8144

    # Test invalid input
    with pytest.raises(ValueError):
        seq = bytes([0xFE] + [0x00] * 14 + [0xAA])
        out = adapter.process_bytes(seq)


def test_init_device(): ...


def test_read_data(): ...


def _mock_usb(): ...
