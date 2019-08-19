"""Unit test for RemoteValuePrioritySwitch objects."""
import asyncio
import unittest

from xknx import XKNX
from xknx.devices import RemoteValuePrioritySwitch
from xknx.exceptions import ConversionError, CouldNotParseTelegram
from xknx.knx import DPTBinary, GroupAddress, Telegram


class TestRemoteValuePrioritySwitch(unittest.TestCase):
    """Test class for TestRemoteValuePrioritySwitch objects."""

    def setUp(self):
        """Set up test class."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Tear down test class."""
        self.loop.close()

    def test_to_knx(self):
        """Test to_knx function with normal operation."""
        xknx = XKNX(loop=self.loop)
        remote_value = RemoteValuePrioritySwitch(xknx, device_name='Prio Switch', group_address='1/6/4')
        self.assertEqual(remote_value.to_knx(3), DPTBinary(3))

    def test_from_knx(self):
        """Test from_knx function with normal operation."""
        xknx = XKNX(loop=self.loop)
        remote_value = RemoteValuePrioritySwitch(xknx, device_name='Prio Switch', group_address='1/6/4')
        self.assertEqual(remote_value.from_knx(DPTBinary(2)), 2)

    def test_to_knx_error(self):
        """Test to_knx function with wrong parametern."""
        xknx = XKNX(loop=self.loop)
        remote_value = RemoteValuePrioritySwitch(xknx, device_name='Prio Switch', group_address='1/6/4')
        with self.assertRaises(ConversionError):
            remote_value.to_knx(4)
        with self.assertRaises(ConversionError):
            remote_value.to_knx("4")

    def test_set(self):
        """Test setting value."""
        xknx = XKNX(loop=self.loop)
        remote_value = RemoteValuePrioritySwitch(
            xknx,
            device_name='Priority Switch',
            group_address=GroupAddress("1/2/3"))
        self.loop.run_until_complete(asyncio.Task(remote_value.set(2)))
        self.assertEqual(xknx.telegrams.qsize(), 1)
        telegram = xknx.telegrams.get_nowait()
        self.assertEqual(
            telegram,
            Telegram(
                GroupAddress('1/2/3'),
                payload=DPTBinary(2)))
        self.loop.run_until_complete(asyncio.Task(remote_value.set(3)))
        self.assertEqual(xknx.telegrams.qsize(), 1)
        telegram = xknx.telegrams.get_nowait()
        self.assertEqual(
            telegram,
            Telegram(
                GroupAddress('1/2/3'),
                payload=DPTBinary(3)))

    def test_process(self):
        """Test process telegram."""
        xknx = XKNX(loop=self.loop)
        remote_value = RemoteValuePrioritySwitch(
            xknx,
            device_name='Prio Switch',
            group_address=GroupAddress("1/2/3"))
        telegram = Telegram(
            group_address=GroupAddress("1/2/3"),
            payload=DPTBinary(0))
        self.loop.run_until_complete(asyncio.Task(remote_value.process(telegram)))
        self.assertEqual(remote_value.value, 0)

    def test_to_process_error(self):
        """Test process errornous telegram."""
        xknx = XKNX(loop=self.loop)
        remote_value = RemoteValuePrioritySwitch(
            xknx,
            device_name='Prio Switch',
            group_address=GroupAddress("1/2/3"))
        with self.assertRaises(CouldNotParseTelegram):
            telegram = Telegram(
                group_address=GroupAddress("1/2/3"),
                payload=DPTBinary(-1))
            self.loop.run_until_complete(asyncio.Task(remote_value.process(telegram)))
        with self.assertRaises(CouldNotParseTelegram):
            telegram = Telegram(
                group_address=GroupAddress("1/2/3"),
                payload=DPTBinary(7))
            self.loop.run_until_complete(asyncio.Task(remote_value.process(telegram)))
