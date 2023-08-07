from json import JSONDecodeError
from typing import Dict, Self, Optional


__slots__ = "channel", "id", "dlc", "data"
class CanMessage(object):
    def __init__(self, channel, id, dlc, data) -> None:
        self.channel = channel
        self.id = id
        self.dlc = dlc
        self.data = data

    @classmethod
    def parse_json(cls, input: Dict[int, str, Optional[str]]) -> Self:
        """This function expects following json structure:
            "<can_message_name>": {
                "can_id": <can_id>,
                "cast_type": "<cast_type>",
                ["custom_type": <custom_type>]
            }
        
        Keyword arguments: input
        input -- This classmethod is called as an object_pairs_hook JSON parameter.
                 "can_messages_name" - DBC message name
                 "can_id"            - CAN message id
                 "cast_type"         - CAN data will be casted to one of the following types:
                                       uint_8, int_8, uint_16, int_16, uint_32, int_32, uint_64, int_64,
                                       float_32, double_64,
                                       str,
                                       custom
                 "custom_type"       - custom type is a list which maps every data bit to a python type
                                       ex. ["uint_8", "uint_8", "uint_16", "float_32"] must have DLC set to 8
                                       if DLC and custom array length in bytes mismatch this function will raise an error
                                       
        Return: Self
        """
        return cls()
    