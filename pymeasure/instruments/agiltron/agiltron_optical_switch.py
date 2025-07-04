#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging

from pymeasure.instruments import Instrument

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AgiltronOpticalSwitch(Instrument):
    """ Represents the Agiltron optical switch and provides a high-level
    interface for interacting with the instrument.

    The optical switch supports both 1x2 and 1x8 configurations with different
    communication protocols.

    .. code-block:: python

        # For 1x8 switch (text-based commands)
        switch = AgiltronOpticalSwitch("ASRL7::INSTR", switch_type="1x8")
        switch.channel = 3
        print(switch.channel)

        # For 1x2 switch (binary commands)
        switch = AgiltronOpticalSwitch("ASRL7::INSTR", switch_type="1x2")
        switch.channel = 1

    """

    SWITCH_TYPES = ['1x2', '1x8']

    def __init__(self, adapter, name="Agiltron Optical Switch", switch_type='1x2', **kwargs):
        """Initialize the Agiltron optical switch.

        :param adapter: VISA address of the instrument
        :param name: Name of the instrument
        :param switch_type: Type of switch ('1x2' or '1x8')
        :param kwargs: Additional keyword arguments passed to the VISA adapter
        """
        # Set up serial communication parameters
        serial_kwargs = {
            'baud_rate': 9600,
            'data_bits': 8,
            'stop_bits': 1,
            'parity': 'none',
            'read_termination': '\r\n',
            'write_termination': '\r\n',
            'timeout': 2000,
        }
        serial_kwargs.update(kwargs)

        super().__init__(adapter, name, includeSCPI=False, **serial_kwargs)

        # Validate switch type
        if switch_type not in self.SWITCH_TYPES:
            raise ValueError(f"Invalid switch type: {switch_type}. "
                             f"Must be one of {self.SWITCH_TYPES}")

        self.switch_type = switch_type

        # Set up channel validation based on switch type
        if self.switch_type == '1x8':
            self._channel_range = range(1, 9)  # 1 to 8
        else:  # '1x2'
            self._channel_range = range(1, 3)  # 1 to 2

        # Initialize device connection and get ID if supported
        if self.switch_type == '1x8':
            self._get_id()

    def _get_id(self):
        """Get the ID information for 1x8 switches."""
        try:
            self._product_name = self.ask('*PN')
            self._serial_number = self.ask('*SN')
            log.info(f"Connected to {self._product_name}, S/N: {self._serial_number}")
        except Exception as e:
            log.warning(f"Could not retrieve device ID: {e}")
            self._product_name = "Unknown"
            self._serial_number = "Unknown"

    @property
    def id(self):
        """Get the device identification information.

        :return: Dictionary containing product name and serial number
        """
        if self.switch_type == '1x8':
            return {
                'product': getattr(self, '_product_name', 'Unknown'),
                'serial': getattr(self, '_serial_number', 'Unknown')
            }
        else:
            return {
                'product': 'Agiltron 1x2 Switch',
                'serial': 'Unknown'
            }

    @property
    def channel(self):
        """Get the currently selected channel (1x8 switches only).

        For 1x2 switches, this property is not directly readable from the device.
        """
        if self.switch_type == '1x8':
            # The switch doesn't have a direct query command, so we track internally
            return getattr(self, '_current_channel', 1)
        else:
            # 1x2 switches don't support channel readback
            return getattr(self, '_current_channel', 1)

    @channel.setter
    def channel(self, value):
        """Set the active channel.

        :param value: Channel number (1-2 for 1x2 switch, 1-8 for 1x8 switch)
        """
        # Validate channel number
        if value not in self._channel_range:
            raise ValueError(f"Channel {value} is not valid for {self.switch_type} switch. "
                             f"Valid channels: {list(self._channel_range)}")

        if self.switch_type == '1x8':
            # Send text command for 1x8 switches
            self.write(f'*SW00{value}')
            self._current_channel = value
            log.info(f"Switched to channel {value}")

        elif self.switch_type == '1x2':
            # Send binary command for 1x2 switches
            if value == 1:
                msg = bytes([0x01, 0x12, 0x00, 0x01])
            elif value == 2:
                msg = bytes([0x01, 0x12, 0x00, 0x02])

            self.adapter.write_raw(msg)
            self._current_channel = value
            log.info(f"Switched to channel {value}")

    def switch_to_channel(self, channel):
        """Switch to the specified channel.

        :param channel: Channel number to switch to
        :return: The selected channel number
        """
        self.channel = channel
        return self.channel

    def get_available_channels(self):
        """Get the list of available channels for this switch type.

        :return: List of available channel numbers
        """
        return list(self._channel_range)

    def __repr__(self):
        """Return a string representation of the instrument."""
        id_info = self.id
        return (f"{self.__class__.__name__}:\n"
                f"  Type: {self.switch_type}\n"
                f"  Product: {id_info['product']}\n"
                f"  Serial: {id_info['serial']}\n"
                f"  Current Channel: {getattr(self, '_current_channel', 'Unknown')}")