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
from pymeasure.instruments.validators import (
    strict_discrete_set, strict_range
)


class TraceChannel(Channel):
    """A trace channel of the instrument."""

    mode = Channel.control(
        ":TRACe{ch}:MODE?", ":TRACe{ch}:MODE %s",
        """Control the trace mode.
        WRITe: puts the trace in the normal mode, updating the data.
        MAXHold: displays the highest measured trace value for all the data that has been
        measured since the function was turned on.
        MINHold: displays the lowest measured trace value for all the data that has been measured
        since the function was turned on.
        VIEW: turns on the trace data so that it can be viewed on the display.
        BLANk: turns off the trace data so that it is not viewed on the display.
        AVERage: averages the trace for test period.
        Default Trace1:WRITe, Trace2|3|4: BLANk""",
        validator=strict_discrete_set,
        values=["WRITe", "MAXHold", "MINHold", "VIEW", "BLANk", "AVERage"],
    )

    data = Channel.measurement(
        ":TRACe:DATA? {ch}",
        """Get the current displayed trace data.
        Returns:
            list: List of amplitude values for the current trace.
        """,
        get_process=lambda v: [float(val) for val in v.split(',')]
    )
    
    math_input_x = Channel.control(
        ":TRACe:MATH:X?", ":TRACe:MATH:X {ch}",
        """Control the trace math input X.
        Sets which trace to use as the X input for trace math operations.
        Available via the Trace > Math > Input X menu on the instrument.""",
    )
    
    math_input_x = Channel.control(
        ":TRACe:MATH:X?", ":TRACe:MATH:X {ch}",
        """Control the trace math input X.
        Sets which trace to use as the X input for trace math operations.
        Available via the Trace > Math > Input X menu on the instrument.""",
    )
    
    math_input_y = Channel.control(
        ":TRACe:MATH:Y?", ":TRACe:MATH:Y {ch}",
        """Control the trace math input Y.
        Sets which trace to use as the Y input for trace math operations.
        Available via the Trace > Math > Input Y menu on the instrument.""",
    )
    
    math_input_z = Channel.control(
        ":TRACe:MATH:Z?", ":TRACe:MATH:Z {ch}",
        """Control the trace math input Z.
        Sets which trace to use as the Z input for trace math operations.
        Available via the Trace > Math > Input Z menu on the instrument.""",
    )
    
    detection_mode = Channel.control(
        ":DETector:TRACe{ch}?", ":DETector:TRACe{ch} %s",
        """Control the detection mode for the trace.
        NEGative: Negative peak detection displays the lowest sample in each interval.
        POSitive: Positive peak detection displays the highest sample in each interval.
        SAMPle: Sample detection displays a single sample taken during each interval.
        AVERage: Average detection displays the average value of all samples in each interval.
        NORMAL: Normal detection selects maximum and minimum video signal values alternately.
        QUASi: Quasipeak detection weights signal levels based on repetition frequency.
        Default: POSitive
        Available via the Detect menu on the instrument.""",
        validator=strict_discrete_set,
        values=["NEGative", "POSitive", "SAMPle", "AVERage", "NORMAL", "QUASi"],
    )
    
    count_average = Channel.control(
        ":AVERage:TRACe{ch}:COUNt?", ":AVERage:TRACe{ch}:COUNt %d",
        """Control the number of measurements that are combined for averaging.
        Valid range: 1 to 999. Default: 1.
        Available via the Trace > Average menu on the instrument.""",
        validator=strict_range,
        values=[1, 999],
        cast=int,
    )
    
    average_number = Channel.measurement(
        ":AVERage:TRACe{ch}?",
        """Get the current average number of traces.
        Returns the current count of measurements that have been averaged.""",
        cast=int
    )

    average_clear = Channel.setting(
        ":AVERage:TRACe{ch}:CLEar",
        """Restart the trace average.
        This command is only available when average is on.
        It resets the current average count and restarts the trace averaging process.
        Available via the Trace menu on the instrument.""",
    )


class SVA1000X(SCPIMixin, Instrument):
    """
    Represents the Siglent SVA 1000X spectrum analyzer and provides a high-level
    interface for controlling frequency, span, amplitude, and measurement settings.
    
    Connection example:
    
    .. code-block:: python
    
        from pymeasure.instruments.siglenttechnologies import SVA1000X
        
        # Connect via USB or Ethernet
        sa = SVA1000X("USB0::0xF4ED::0xEE3A::SVA1032X5R0123::INSTR")
        # or via Ethernet
        # sa = SVA1000X("TCPIP::192.168.1.100::INSTR")
        
        # Basic frequency setup
        sa.center_frequency = 1e9  # 1 GHz
        sa.frequency_span = 100e6  # 100 MHz span
        
        # Take a measurement
        frequencies = sa.frequencies
        trace_data = sa.trace_data
    """

    def __init__(self, adapter, name="Siglent SVA 1000X Spectrum Analyzer", **kwargs):
        super().__init__(adapter, name, **kwargs)

    # Frequency Control
    center_frequency = Instrument.control(
        ":FREQuency:CENTer?", ":FREQuency:CENTer %g",
        """Control the center frequency in Hz.
        Valid range: 50 Hz to 3.2 GHz.""",
        validator=strict_range,
        values=[50, 3.2e9],
    )

    start_frequency = Instrument.control(
        ":FREQuency:STARt?", ":FREQuency:STARt %g",
        """Control the start frequency in Hz.
        Valid range: 0 Hz to 3.2 GHz.""",
        validator=strict_range,
        values=[0, 3.2e9],
    )

    stop_frequency = Instrument.control(
        ":FREQuency:STOP?", ":FREQuency:STOP %g",
        """Control the stop frequency in Hz.""",
        validator=strict_range,
        values=[0, 3.2e9],
    )

    center_frequency_step = Instrument.control(
        ":FREQuency:CENTer:STEP?", ":FREQuency:CENTer:STEP %g",
        """Control the step size for center frequency adjustments in Hz.
        Valid range: 1 Hz to 3.2 GHz.
        Default: 320 MHz.""",
        validator=strict_range,
        values=[1, 3.2e9],
    )
    
    frequency_step_auto = Instrument.control(
        ":FREQuency:CENTer:STEP:AUTO?", ":FREQuency:CENTer:STEP:AUTO %s",
        """Control whether the step size is set automatically based on the span.
        ON (1) sets step size automatically, OFF (0) for manual control.""",
        validator=strict_discrete_set,
        values=["ON", "OFF", "1", "0"],
        map_values=True,
    )

    set_step_to_center_frequency = Instrument.setting(
        ":FREQuency:CENTer:SET:STEP",
        """Set the step value equal to center frequency.
        This command sets the step size equal to the current center frequency value.""",
    )

    frequency_offset = Instrument.control(
        ":SENSe:FREQuency:OFFSet?", ":SENSe:FREQuency:OFFSet %g",
        """Control the frequency offset in Hz.
        Valid range: -100 GHz to 100 GHz. Default: 0 Hz.""",
        validator=strict_range,
        values=[-100e9, 100e9],
    )

    frequency_span = Instrument.control(
        ":FREQuency:SPAN?", ":FREQuency:SPAN %g",
        """Control the frequency span in Hz.
        Valid values: 0 Hz (zero span/time domain mode) or 100 Hz to 3.2 GHz.
        Default: 1.5 GHz.""",
        validator=strict_range,
        values=[0, 3.2e9],
    )

    set_frequency_span_full = Instrument.setting(
        ":FREQuency:SPAN:FULL",
        """Set the frequency span to full scale.
        This command sets the span to the maximum value supported by the instrument.""",
    )

    set_frequency_span_zero = Instrument.setting(
        ":FREQuency:SPAN:ZERO",
        """Set the frequency span to zero (time domain mode).
        This command sets the analyzer to zero span mode for time domain analysis.""",
    )

    set_frequency_span_previous = Instrument.setting(
        ":FREQuency:SPAN:PREVious",
        """Set the frequency span to the previous value.
        This command restores the last used frequency span value.""",
    )

    set_frequency_span_half = Instrument.setting(
        ":FREQuency:SPAN:HALF",
        """Set the frequency span to half of the current value.
        This command reduces the current span by a factor of two.""",
    )

    set_frequency_span_double = Instrument.setting(
        ":FREQuency:SPAN:DOUBle",
        """Set the frequency span to double the current value.
        This command increases the current span by a factor of two.""",
    )
    
    auto_tune = Instrument.setting(
        ":FREQuency:TUNE:IMMediate",
        """Auto tune the spectrum analyzer to display the main signal.
        This command automatically adjusts the analyzer parameters to best display
        the dominant signal in the current frequency range.
        Available via the Auto Tune menu on the instrument.""",
    )

    # Amplitude Control
    reference_level = Instrument.control(
        ":DISPlay:WINDow:TRACe:Y:SCALe:RLEVel?", ":DISPlay:WINDow:TRACe:Y:SCALe:RLEVel %g DBM",
        """Control the reference level for the Y-axis.
        Valid range: -100 dBm to 30 dBm. Default: 0 dBm.
        Note: Other units are supported by the instrument (dBmV, dBuV, dBuA, V, W)
        but this implementation uses dBm.""",
        validator=strict_range,
        values=[-100, 30],
    )

    attenuation = Instrument.control(
        ":SENSe:POWer:RF:ATTenuation?", ":SENSe:POWer:RF:ATTenuation %g",
        """Control the RF attenuation in dB.
        Valid range: 0 to 51 dB. Default: 20 dB.""",
        validator=strict_range,
        values=[0, 51],
    )

    attenuation_auto = Instrument.control(
        ":SENSe:POWer:RF:ATTenuation:AUTO?", ":SENSe:POWer:RF:ATTenuation:AUTO %s",
        """Control automatic RF attenuation.
        ON (1) enables auto attenuation, OFF (0) disables it.
        Default: ON""",
        validator=strict_discrete_set,
        values=["ON", "OFF", "1", "0"],
        map_values=True,
    )
    
    preamp = Instrument.control(
        ":SENSe:POWer:RF:GAIN:STATe?", ":SENSe:POWer:RF:GAIN:STATe %s",
        """Control the internal preamplifier.
        ON (1) turns on the preamplifier, OFF (0) turns it off.
        Available via the Amplitude > Preamp menu on the instrument.
        Default: OFF""",
        validator=strict_discrete_set,
        values=["ON", "OFF", "1", "0"],
        map_values=True,
    )
    
    reference_offset = Instrument.control(
        ":DISPlay:WINDow:TRACe:Y:SCALe:RLEVel:OFFSet?",
        ":DISPlay:WINDow:TRACe:Y:SCALe:RLEVel:OFFSet %g",
        """Control the reference level offset in dB.
        Valid range: -100 dB to 100 dB. Default: 0 dB.
        Available via the Amplitude > Ref OffSets menu on the instrument.""",
        validator=strict_range,
        values=[-100, 100],
    )
    
    amplitude_units = Instrument.control(
        ":UNIT:POWer?", ":UNIT:POWer %s",
        """Control the amplitude units for the input, output and display.
        Valid values: DBM (dBm), DBMV (dBmV), DBUV (dBuV), DBUA (dBuA), V (volts), W (watts).
        Default: DBM
        Available via the Amplitude > Units menu on the instrument.""",
        validator=strict_discrete_set,
        values=["DBM", "DBMV", "DBUV", "DBUA", "V", "W"],
    )
    
    scale_type = Instrument.control(
        ":DISPlay:WINDow:TRACe:Y:SCALe:SPACing?", 
        ":DISPlay:WINDow:TRACe:Y:SCALe:SPACing %s",
        """Control the vertical graticule divisions between logarithmic and linear units.
        LINear sets the vertical divisions to linear units (V),
        LOGarithmic sets the vertical divisions to logarithmic units (dBm).
        Available via the Amplitude > Scale Type menu on the instrument.
        Default: LOGarithmic""",
        validator=strict_discrete_set,
        values=["LINear", "LOGarithmic"],
    )

    scale_division = Instrument.control(
        ":DISPlay:WINDow:TRACe:Y:SCALe:PDIVision?", 
        ":DISPlay:WINDow:TRACe:Y:SCALe:PDIVision %g",
        """Control the per-division display scaling for the y-axis when in logarithmic scale.
        Valid range: 1 dB to 10 dB. Default: 10 dB.
        Available via the Amplitude > Scale/Div menu on the instrument.""",
        validator=strict_range,
        values=[1, 10],
    )

    set_correction_off = Instrument.setting(
        ":CORRection:OFF",
        """Disable all amplitude correction functions.
        This command turns off all amplitude correction sets.
        Available via the Amplitude > Corrections menu on the instrument.""",
    )
    
    # TODO: Implement additional amplitude correction functions from the manual

    # Sweep Control
    sweep_mode = Instrument.control(
        ":SWEep:MODE?", ":SWEep:MODE %s",
        """Control the sweep mode.
        AUTO automatically selects between sweep and FFT mode.
        FFT forces FFT analysis mode.
        SWEep forces stepped sweep mode.
        Default: SWEep""",
        validator=strict_discrete_set,
        values=["AUTO", "FFT", "SWEep"],
    )

    sweep_time = Instrument.control(
        ":SWEep:TIME?", ":SWEep:TIME %g",
        """Control the sweep time in seconds.
        Valid range: 450 µs to 1500 s.
        In zero span mode (span=0 Hz), the X-axis represents time rather than frequency.
        Default value depends on current settings, typically around 312.416 ms.""",
        validator=strict_range,
        values=[450e-6, 1500],
    )

    sweep_time_auto_enabled = Instrument.control(
        ":SWEep:TIME:AUTO?", ":SWEep:TIME:AUTO %s",
        """Control automatic sweep time.
        ON (1) enables auto sweep time, OFF (0) disables it.
        Default: ON
        Available via the Sweep > Sweep Time menu on the instrument.""",
        validator=strict_discrete_set,
        values=["ON", "OFF", "1", "0"],
        map_values=True,
    )
    
    sweep_speed = Instrument.control(
        ":SWEep:SPEed?", ":SWEep:SPEed %s",
        """Control the sweep speed mode.
        NORMal for faster sweeps with less accuracy.
        ACCUracy for more accurate measurements with slower sweep times.
        Default: NORMal
        Available via the Sweep > Sweep Rule menu on the instrument.""",
        validator=strict_discrete_set,
        values=["NORMal", "ACCUracy"],
    )
    
    sweep_count = Instrument.control(
        ":SWEep:COUNt?", ":SWEep:COUNt %d",
        """Control the number of sweeps to perform when in single sweep mode.
        Valid range: 1 to 99999. Default: 1.
        Available via the Sweep > Numbers menu on the instrument.""",
        validator=strict_range,
        values=[1, 99999],
        cast=int,
    )
    
    qpd_time = Instrument.control(
        ":QPD:DWELl:TIME?", ":QPD:DWELl:TIME %g",
        """Control the QPD (Quasi-Peak Detector) dwell time in seconds.
        Valid range: 0 us to 10 s (quasi-peak: 900 us to 30 ks).
        Default: 50 ms.
        Available via the Sweep > QPD Time menu on the instrument.""",
        validator=strict_range,
        values=[0, 10],
    )
    
    restart_sweep = Instrument.setting(
        ":INITiate:RESTart",
        """Restart the current sweep.
        This command initiates or restarts the current sweep operation.""",
    )
    
    continuous_sweep_enabled = Instrument.control(
        ":INITiate:CONTinuous?", ":INITiate:CONTinuous %s",
        """Control continuous sweep mode.
        ON (1) enables continuous sweep, OFF (0) disables it and sets to single sweep mode.
        Default: ON
        Available via the Sweep > Sweep menu on the instrument.""",
        validator=strict_discrete_set,
        values=["ON", "OFF", "1", "0"],
        map_values=True,
    )
    
    initiate_pause = Instrument.setting(
        ":INITiate:Pause",
        """Pause the current sweep.
        This command pauses the sweep at the end of the current sweep cycle.""",
    )
    
    initiate_resume = Instrument.setting(
        ":INITiate:RESume",
        """Resume a paused sweep.
        This command resumes a previously paused sweep operation.""",
    )
    
    abort = Instrument.setting(
        ":ABORt",
        """Abort the current sweep operation.
        This command immediately stops the current measurement cycle.""",
    )

    # Trigger Control
    trigger_source = Instrument.control(
        ":TRIGger:SOURce?", ":TRIGger:SOURce %s",
        """Control the trigger source.
        IMMediate: free-run triggering.
        VIDeo: triggers on the video signal level.
        EXTernal: allows you to connect an external trigger source.
        Default: IMMediate""",
        validator=strict_discrete_set,
        values=["IMMediate", "VIDeo", "EXTernal"],
    )
    
    trigger_video_level = Instrument.control(
        ":TRIGger:VIDeo:LEVel?", ":TRIGger:VIDeo:LEVel %g DBM",
        """Control the level at which a video trigger will occur in dBm.
        Valid range: -300 dBm to 50 dBm. Default: 0 dBm.
        Note: This setting is only effective when trigger_source is set to VIDeo.
        Available via the Trigger > Video Level menu on the instrument.""",
        validator=strict_range,
        values=[-300, 50],
    )
    
    trigger_edge = Instrument.control(
        ":TRIGger:RFBurst:SLOPe?", ":TRIGger:RFBurst:SLOPe %s",
        """Control the edge/slope for external trigger signals.
        POSitive: Triggers on the positive edge of the external trigger signal.
        NEGative: Triggers on the negative edge of the external trigger signal.
        Default: POSitive
        Note: External trigger signal must be a 0V to +5V TTL signal.
        Available via the Trigger > External Trigger menu on the instrument.""",
        validator=strict_discrete_set,
        values=["POSitive", "NEGative"],
    )

    # Bandwidth Control
    resolution_bandwidth = Instrument.control(
        ":BWIDth:RESolution?", ":BWIDth:RESolution %g",
        """Control the resolution bandwidth (RBW) in Hz.
        Valid values: 1Hz, 3Hz, 10Hz, 30Hz, 100Hz, 300Hz, 1kHz, 3kHz, 10kHz, 
        30kHz, 100kHz, 300kHz, 1MHz.
        Default: 1MHz.""",
        validator=strict_discrete_set,
        values=[1, 3, 10, 30, 100, 300, 1e3, 3e3, 10e3, 30e3, 100e3, 300e3, 1e6],
    )

    resolution_bandwidth_auto = Instrument.control(
        ":SENSe:BANDwidth:RESolution:AUTO?", ":SENSe:BANDwidth:RESolution:AUTO %s",
        """Control automatic resolution bandwidth (RBW).
        ON (1) enables auto RBW, OFF (0) disables it.
        Default: ON
        Available via the BW > RBW menu on the instrument.""",
        validator=strict_discrete_set,
        values=["ON", "OFF", "1", "0"],
        map_values=True,
    )
    video_bandwidth = Instrument.control(
        ":BWIDth:VIDeo?", ":BWIDth:VIDeo %g",
        """Control the video bandwidth (VBW) in Hz.
        Valid values: 1Hz, 3Hz, 10Hz, 30Hz, 100Hz, 300Hz, 1kHz, 3kHz, 10kHz, 
        30kHz, 100kHz, 300kHz, 1MHz.
        Default: 1MHz.
        Available via the BW > VBW menu on the instrument.""",
        validator=strict_discrete_set,
        values=[1, 3, 10, 30, 100, 300, 1e3, 3e3, 10e3, 30e3, 100e3, 300e3, 1e6],
    )

    video_bandwidth_auto = Instrument.control(
        ":SENSe:BANDwidth:VIDeo:AUTO?", ":SENSe:BANDwidth:VIDeo:AUTO %s",
        """Control automatic video bandwidth (VBW).
        ON (1) enables auto VBW, OFF (0) disables it.
        Default: ON
        Available via the BW > VBW Auto menu on the instrument.""",
        validator=strict_discrete_set,
        values=["ON", "OFF", "1", "0"],
        map_values=True,
    )

    video_bandwidth_ratio = Instrument.control(
        ":BWIDth:VIDeo:RATio?", ":BWIDth:VIDeo:RATio %g",
        """Control the ratio of the video bandwidth to the resolution bandwidth.
        Valid values: 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0
        Default: 1.0
        Available via the BW > VBW/RBW menu on the instrument.""",
        validator=strict_discrete_set,
        values=[0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0],
    )
    
    video_bandwidth_ratio_auto = Instrument.measurement(
        ":BWIDth:VIDeo:RATio:CONfig?",
        """Query whether automatic video to resolution bandwidth ratio is enabled.
        Returns 0 (OFF) or 1 (ON).
        Default: 1 (ON)""",
        map_values=True
    )
    
    filter_type = Instrument.control(
        ":SENSe:FILTer:TYPE?", ":SENSe:FILTer:TYPE %s",
        """Control the filter type used for measurements.
        EMI: Selects EMI filter type for EMI measurements.
        GAUSS: Selects Gaussian filter type for general spectrum analysis.
        Default: GAUSS""",
        validator=strict_discrete_set,
        values=["EMI", "GAUSS"],
    )

    # Trace Control
    trace_data_type = Instrument.control(
        ":FORMat:TRACe:DATA?", ":FORMat:TRACe:DATA %s",
        """Control the trace data type format.
        ASCii: Returns trace data as comma-separated ASCII values.
        REAL,32 or REAL32: Binary 32-bit real values in the current Y Axis Unit.
        REAL,64 or REAL: Binary 64-bit real values in the current Y Axis Unit.
        Default: ASCii""",
        validator=strict_discrete_set,
        values=["ASCii", "REAL,32", "REAL,64", "REAL32", "REAL"],
    )
    
    trace_math_function = Instrument.control(
        ":CALCulate[:SELected]:MATH:FUNCtion?", ":CALCulate[:SELected]:MATH:FUNCtion %s",
        """Control the trace math function.
        OFF: Turns off trace math operations.
        PDIF: Power Difference - subtracts the power level of the source trace from the power 
        level of the target trace.
        PSUM: Power Sum - adds the power level of the source trace to the power level of the target 
        trace.
        LOFF: Log Offset - adds an offset value to the source trace.
        LDIF: Log Difference - subtracts the logged data of the source trace from the logged data of 
        the target trace.
        Default: OFF""",
        validator=strict_discrete_set,
        values=["OFF", "PDIF", "PSUM", "LOFF", "LDIF"],
    )
    
    trace_math_offset = Instrument.control(
        ":TRACe:MATH:OFFSet?", ":TRACe:MATH:OFFSet %g",
        """Control the trace math offset in dB.""",
        validator=strict_range,
        values=[-100, 100],
    )
    
    average_type = Instrument.control(
        ":AVERage:TYPE?", ":AVERage:TYPE %s",
        """Control the average type for measurements.
        LOGPower: Logarithmic power averaging.
        POWer: Power averaging (RMS).
        VOLTage: Voltage averaging.
        Default: LOGPower
        Available via the BW > Avg Type menu on the instrument.""",
        validator=strict_discrete_set,
        values=["LOGPower", "POWer", "VOLTage"],
    )

    trace1 = Instrument.ChannelCreator(TraceChannel, 1)
    trace2 = Instrument.ChannelCreator(TraceChannel, 2)
    trace3 = Instrument.ChannelCreator(TraceChannel, 3)
    trace4 = Instrument.ChannelCreator(TraceChannel, 4)
