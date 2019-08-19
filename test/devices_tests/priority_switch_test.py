"""Unit test for PrioritySwitch objects."""
import asyncio
import unittest
from unittest.mock import Mock

from xknx import XKNX
from xknx.devices import PrioritySwitch
from xknx.knx import DPTBinary, GroupAddress, Telegram, TelegramType


class TestPrioritySwitch(unittest.TestCase):
    """Test class for PrioritySwitch object."""

    def setUp(self):
        """Set up test class."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Tear down test class."""
        self.loop.close()

    #
    # SYNC
    #
    def test_sync(self):
        """Test sync function / sending group reads to KNX bus."""
        xknx = XKNX(loop=self.loop)
        priority_switch = PrioritySwitch(xknx, "TestOutlet", group_address_state='1/2/3')
        self.loop.run_until_complete(asyncio.Task(priority_switch.sync(False)))

        self.assertEqual(xknx.telegrams.qsize(), 1)

        telegram = xknx.telegrams.get_nowait()
        self.assertEqual(telegram,
                         Telegram(GroupAddress('1/2/3'), TelegramType.GROUP_READ))

    def test_sync_state_address(self):
        """Test sync function / sending group reads to KNX bus. Test with Switch with explicit state address."""
        xknx = XKNX(loop=self.loop)
        priority_switch = PrioritySwitch(xknx, "TestOutlet",
                                         group_address='1/2/3',
                                         group_address_state='1/2/4')
        self.loop.run_until_complete(asyncio.Task(priority_switch.sync(False)))

        self.assertEqual(xknx.telegrams.qsize(), 1)

        telegram = xknx.telegrams.get_nowait()
        self.assertEqual(telegram,
                         Telegram(GroupAddress('1/2/4'), TelegramType.GROUP_READ))

    #
    # TEST PROCESS
    #
    def test_process(self):
        """Test process / reading telegrams from telegram queue. Test if device was updated."""
        xknx = XKNX(loop=self.loop)
        priority_switch = PrioritySwitch(xknx, 'TestOutlet', group_address='1/2/3')

        # self.assertEqual(priority_switch.state, None)

        telegram_on = Telegram()
        telegram_on.group_address = GroupAddress('1/2/3')
        telegram_on.payload = DPTBinary(1)
        self.loop.run_until_complete(asyncio.Task(priority_switch.process(telegram_on)))
        #  Priority off, Switch on
        self.assertEqual(priority_switch.resolve_state(), True)
        self.assertEqual(priority_switch.resolve_priority(), False)

        telegram_off = Telegram()
        telegram_off.group_address = GroupAddress('1/2/3')
        telegram_off.payload = DPTBinary(0)
        self.loop.run_until_complete(asyncio.Task(priority_switch.process(telegram_off)))
        #  Priority off, Switch off
        self.assertEqual(priority_switch.resolve_state(), False)
        self.assertEqual(priority_switch.resolve_priority(), False)

    def test_process_callback(self):
        """Test process / reading telegrams from telegram queue. Test if callback was called."""
        # pylint: disable=no-self-use

        xknx = XKNX(loop=self.loop)
        priority_switch = PrioritySwitch(xknx, 'TestOutlet', group_address='1/2/3')

        after_update_callback = Mock()

        async def async_after_update_callback(device):
            """Async callback."""
            after_update_callback(device)
        priority_switch.register_device_updated_cb(async_after_update_callback)

        telegram = Telegram()
        telegram.group_address = GroupAddress('1/2/3')
        telegram.payload = DPTBinary(1)
        self.loop.run_until_complete(asyncio.Task(priority_switch.process(telegram)))

        after_update_callback.assert_called_with(priority_switch)

    #
    # TEST SET PRIORITY FALSE, SWITCH OFF
    #
    def test_set_on(self):
        """Test switching on switch."""
        xknx = XKNX(loop=self.loop)
        priority_switch = PrioritySwitch(xknx, 'TestOutlet', group_address='1/2/3')
        self.loop.run_until_complete(asyncio.Task(priority_switch.set(0)))
        self.assertEqual(xknx.telegrams.qsize(), 1)
        telegram = xknx.telegrams.get_nowait()
        self.assertEqual(telegram,
                         Telegram(GroupAddress('1/2/3'), payload=DPTBinary(0)))

    #
    # TEST SET PRIORITY FALSE, SWITCH ON
    #
    def test_set_off(self):
        """Test switching off switch."""
        xknx = XKNX(loop=self.loop)
        priority_switch = PrioritySwitch(xknx, 'TestOutlet', group_address='1/2/3')
        self.loop.run_until_complete(asyncio.Task(priority_switch.set(1)))
        self.assertEqual(xknx.telegrams.qsize(), 1)
        telegram = xknx.telegrams.get_nowait()
        self.assertEqual(telegram,
                         Telegram(GroupAddress('1/2/3'), payload=DPTBinary(1)))

    #
    # TEST has_group_address
    #
    def test_has_group_address(self):
        """Test has_group_address."""
        xknx = XKNX(loop=self.loop)
        priority_switch = PrioritySwitch(xknx, 'TestOutlet', group_address='1/2/3')
        self.assertTrue(priority_switch.has_group_address(GroupAddress('1/2/3')))
        self.assertFalse(priority_switch.has_group_address(GroupAddress('2/2/2')))
