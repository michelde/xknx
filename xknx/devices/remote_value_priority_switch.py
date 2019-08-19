"""
Module for managing an DPT Priority Switch remote value.

DPT 2.001.
"""
from xknx.exceptions import ConversionError, CouldNotParseTelegram
from xknx.knx import DPTBinary

from .remote_value import RemoteValue


class RemoteValuePrioritySwitch(RemoteValue):
    """Abstraction for remote value of KNX DPT 2.001 / DPT_Switch."""

    def __init__(self,
                 xknx,
                 group_address=None,
                 group_address_state=None,
                 sync_state=True,
                 device_name=None,
                 after_update_cb=None):
        """Initialize remote value of KNX DPT 2.001."""
        # pylint: disable=too-many-arguments
        super().__init__(xknx,
                         group_address,
                         group_address_state,
                         device_name=device_name,
                         sync_state=sync_state,
                         after_update_cb=after_update_cb)

    def payload_valid(self, payload):
        """Test if telegram payload may be parsed."""
        return (isinstance(payload, DPTBinary)
                and 0 <= payload.value <= 3)

    def to_knx(self, value):
        """Convert value to payload."""
        if isinstance(value, int) and 0 <= value <= 3:
            return DPTBinary(value)
        raise ConversionError("value invalid", value=value, device_name=self.device_name)

    def from_knx(self, payload):
        """Check if 0 <= payload <= 3."""
        if 0 <= payload.value <= 3:
            return payload.value
        raise CouldNotParseTelegram("payload invalid", payload=payload, device_name=self.device_name)
