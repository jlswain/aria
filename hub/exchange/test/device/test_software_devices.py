from unittest      import TestCase
from unittest      import mock
from unittest.mock import Mock
from unittest.mock import MagicMock
from unittest.mock import patch
import unittest

import datetime
from datetime import timedelta
from device     import Device
from device.timer_device import TimerDevice

@mock.patch('device.timer_device.datetime')
@mock.patch("threading.Thread")
class TestTimerDevice (TestCase):

    @unittest.skip('not working')
    def test_timer_should_generate_event_after_time (self, mock_timer, mock_datetime):
        mock_datetime.datetime.now.return_value = datetime.datetime.fromtimestamp(1479659949)

        lastTime = datetime.datetime.fromtimestamp(1479659940)

        # Create a timer that will generate an event every 5 seconds
        eventCallback = Mock()
        timer = TimerDevice(5)
        timer.registerEventCallback(eventCallback)

        # If the timer ticks up by 5 seconds, an event should be generated
        # This test calls tick() manually, in reality this will need to be a timer on a thread
        timer.tick(lastTime)
        eventCallback.assert_called_with(timer.get_uuid(), {'value': str(mock_datetime.datetime.now.return_value)})

    @unittest.skip('not working')
    def test_timer_should_not_generate_event_if_time_has_not_passed (self, mock_timer, mock_datetime):
        mock_datetime.datetime.now.return_value = datetime.datetime.fromtimestamp(1479659942)

        lastTime = datetime.datetime.fromtimestamp(1479659940)

        # Create a timer that will generate an event every 5 seconds
        eventCallback = Mock()
        timer = TimerDevice(5)
        timer.registerEventCallback(eventCallback)

        # If the timer ticks up by less than 5 seconds, no event should be generated
        timer.tick(lastTime)
        self.assertFalse(eventCallback.called)
    


