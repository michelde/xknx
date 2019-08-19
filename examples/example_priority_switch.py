"""Example for Switch device."""
import asyncio

from xknx import XKNX
from xknx.devices import PrioritySwitch


async def main():
    """Connect to KNX/IP device, switch on outlet, wait 2 seconds and switch of off again."""
    xknx = XKNX()
    await xknx.start()
    priority_switch = PrioritySwitch(xknx,
                                     name='TestPriority',
                                     group_address='2/0/99')
    # set priority = true; value = on
    await priority_switch.set(3)
    await asyncio.sleep(2)
    # set priority = false; value = off
    await priority_switch.set(0)
    await asyncio.sleep(2)
    await xknx.stop()


# pylint: disable=invalid-name
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
