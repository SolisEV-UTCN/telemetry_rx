import logging
from typing import Tuple

import usb.core

from classes.message import Message
from classes.parser import Parser
from helpers.paterns import Adapter


DEVICE_VENDOR  = 0x0403
DEVICE_PRODUCT = 0x6001

class UsbAdapter(Adapter):
    def __init__(self):
        self.device: usb.core.Device

    async def init_device(self) -> bool:
        dev = usb.core.find(idVendor=DEVICE_VENDOR, idProduct=DEVICE_PRODUCT)
        
        if isinstance(dev, usb.core.Device):
            self.device = dev
            self.device.set_configuration()
            logging.info(f"Device {DEVICE_VENDOR}:{DEVICE_PRODUCT} found")
            return True

        return False

    async def read_data(self) -> Tuple[bool, Message]:
        """Returns list of points"""
        if self.device is None:
            return (False, Message("INVALID", "garbage", ["INVALID,intel,uint,0,1"]))
        
        # Read serial stream
        byte_stream = self.device.read(0, 12, 10)
        can_id = int(bytearray(byte_stream[:4]), base=16)
        can_data = bytearray(byte_stream[4:])

        # Map input to JSON
        if can_id in Parser().messages:
            message = Parser().messages[can_id]
        else:
            logging.warn(f"Received unknown message with id {can_id}")
            message = Message(f"UNKNOWN_{can_id}", "garbage", ["UNKNOWN_1,intel,uint,0,32","UNKNOWN_2,intel,uint,32,32"])

        # Serialize data
        await message.convert_bytes(can_data)

        return (True, message)
