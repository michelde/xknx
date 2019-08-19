"""
Module for managing a switch via KNX.

It provides functionality for

* push local state changes to KNX bus
* KNX devices may read local values via GROUP READ.
"""
from .device import Device
from .remote_value_priority_switch import RemoteValuePrioritySwitch


class PrioritySwitch(Device):
    """Class for managing a priority switch."""

    def __init__(self,
                 xknx,
                 name,
                 group_address=None,
                 group_address_state=None,
                 device_updated_cb=None):
        """Initialize Priority Switch class."""
        # pylint: disable=too-many-arguments
        super().__init__(xknx, name, device_updated_cb)

        self.priority_switch = RemoteValuePrioritySwitch(
            xknx,
            group_address,
            group_address_state,
            device_name=self.name,
            after_update_cb=self.after_update)

    @classmethod
    def from_config(cls, xknx, name, config):
        """Initialize object from configuration structure."""
        group_address = \
            config.get('group_address')
        group_address_state = \
            config.get('group_address_state')

        return cls(xknx,
                   name,
                   group_address=group_address,
                   group_address_state=group_address_state)

    def has_group_address(self, group_address):
        """Test if device has given group address."""
        return self.priority_switch.has_group_address(group_address)

    def state_addresses(self):
        """Return group addresses which should be requested to sync state."""
        return self.priority_switch.state_addresses()

    @property
    def priority(self):
        """Return the current switch state of the device."""
        # None will return False
        return self.resolve_priority()

    @property
    def state(self):
        """Return the current switch state of the device."""
        # None will return False
        return self.resolve_state()

    async def process_group_read(self, telegram):
        """Process incoming GROUP READ telegram."""
        await self.priority_switch.send(response=True)

    async def process_group_write(self, telegram):
        """Process incoming GROUP WRITE telegram."""
        await self.priority_switch.process(telegram)

    async def set(self, value):
        """Set new value."""
        await self.priority_switch.set(value)

    def resolve_state_str(self):
        """Return the current state of the sensor as a human readable string."""
        values = {
            0: 'Priority off, Switch off',
            1: 'Priority off, Switch on',
            2: 'Priority on, Switch off',
            3: 'Priority on, Switch on'
        }
        return values.get(self.priority_switch.value, 'Value not possible')

    def resolve_state(self):
        """Return the current state of the sensor."""
        values = {
            0: False,  # Priority off, Switch off
            1: True,  # Priority off, Switch on
            2: False,  # Priority on, Switch off
            3: True  # Priority on, Switch on
        }

        return values.get(self.priority_switch.value, 'Value not possible')

    def resolve_priority(self):
        """Return the current state of the sensor."""
        values = {
            0: False,  # Priority off, Switch off
            1: False,  # Priority off, Switch on
            2: True,  # Priority on, Switch off
            3: True  # Priority on, Switch on
        }
        return values.get(self.priority_switch.value, 'Value not possible')

    def __str__(self):
        """Return object as readable string."""
        return '<Priority Switch name="{0}" ' \
               'sensor="{1}" value="{2}"/>' \
            .format(self.name,
                    self.priority_switch.group_addr_str(),
                    self.resolve_state())

    def __eq__(self, other):
        """Equal operator."""
        return self.__dict__ == other.__dict__
