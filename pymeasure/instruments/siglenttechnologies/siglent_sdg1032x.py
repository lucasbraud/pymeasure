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

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SDG1032XChannel(Channel):
    """
    Represents a channel on the Siglent SDG1032X dual-channel function generator.
    """

    # Output control
    output_enabled = Channel.control(
        ":C{ch}:OUTP?", ":C{ch}:OUTP %s",
        """Control the output state of the channel (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process_list=lambda v: v[0].split()[-1] == "ON" if len(v) > 0 else False,
    )

    output_polarity = Channel.control(
        ":C{ch}:OUTP?", ":C{ch}:OUTP PLRT,%s",
        """Control the output polarity (NOR or INVT).""",
        validator=strict_discrete_set,
        values=["NOR", "INVT"],
        get_process_list=lambda v: v[6] if len(v) > 6 else "NOR",
    )

    output_load = Channel.control(
        ":C{ch}:OUTP?", ":C{ch}:OUTP LOAD,%s",
        """Control the output load impedance.
        HZ for high impedance or numeric value in ohms (50-10000).""",
        # We use a custom validator to allow both "HZ" and numeric values 50-10000
        validator=lambda x: x if x == "HZ" or (
            isinstance(x, (int, float)) and 50 <= x <= 10000
        ) else ValueError("Load must be 'HZ' or 50-10000 ohms"),
        get_process_list=lambda v: v[2] if len(v) > 2 else "HZ",
    )

    # Noise addition control
    noise_addition_enabled = Channel.control(
        ":C{ch}:NOISE_ADD?", ":C{ch}:NOISE_ADD STATE,%s",
        """Control whether noise is added to the output signal (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process_list=lambda v: v[1] == "ON" if len(v) > 1 else False,
    )

    def get_waveform_settings(self):
        """Get all waveform settings for this channel as a dictionary.

        Returns
        -------
        dict
            Dictionary containing all waveform settings
        """
        # Query all waveform settings
        response = self.ask(":BSWV{ch}?")

        # Remove the command echo and split by comma
        settings_str = response[8:].split(',')

        # Convert to dictionary
        settings = {}
        for i, key in enumerate(settings_str):
            if (i % 2) == 0:
                settings[key] = settings_str[i + 1]

        return settings


class SDG1032X(SCPIMixin, Instrument):
    """
    Represents the Siglent SDG1032X dual-channel function generator.
    
    This instrument provides two independent channels for generating various waveforms
    including sine, square, ramp, pulse, noise, arbitrary, DC, and PRBS signals.
    Each channel supports burst mode operation with configurable trigger sources.
    """

    def __init__(self, adapter, name="Siglent SDG1032X Function Generator", **kwargs):
        super().__init__(adapter, name, **kwargs)
        
    # Channel definitions
    channel_1 = Instrument.ChannelCreator(SDG1032XChannel, "1")
    channel_2 = Instrument.ChannelCreator(SDG1032XChannel, "2")
