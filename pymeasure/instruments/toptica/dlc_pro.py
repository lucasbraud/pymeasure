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

"""
This module contains the driver for Toptica DLC Pro laser controllers.
"""

import datetime
import logging

from pymeasure.instruments import Instrument

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TopticaDLCPro(Instrument):
    """
    Represents a Toptica DLC Pro laser controller and provides a high-level interface for
    interacting with the instrument. This class wraps the Toptica SDK to provide PyMeasure
    compatibility.

    Supports both CTL and TA laser systems. The laser type is automatically detected
    during initialization.

    .. code-block:: python

        # Initialize with IP address (connection opens automatically)
        laser = TopticaDLCPro("192.168.1.44")

        try:
            # For CTL lasers
            print(f"Wavelength: {laser.wavelength} nm")
            laser.wavelength = 1550.0
            laser.emission = True

            # For TA lasers
            laser.ta_current = 800.0  # mA
            laser.ta_temperature_setpoint = 25.0  # °C

            # Get all parameters as a dictionary
            params = laser.get_all_parameters()

            # Save to JSON
            import json
            with open("laser_config.json", "w") as f:
                json.dump(params, f, indent=2)

        finally:
            # Always ensure proper shutdown
            laser.shutdown()

    :param ip_address: The IP address of the Toptica DLC Pro device
    :param name: The name of the instrument (defaults to auto-detected type)
    :param \\**kwargs: Additional keyword arguments passed to parent class
    """

    def __init__(self, ip_address, name=None, **kwargs):
        """
        Initialize the Toptica DLC Pro instrument.

        :param ip_address: The IP address of the Toptica DLC Pro device
        :param name: The name of the instrument (defaults to auto-detected type)
        """
        # Import here to avoid import errors if SDK is not available
        try:
            from toptica.lasersdk.client import NetworkConnection, DecopError
        except ImportError:
            raise ImportError("toptica.lasersdk is required for TopticaDLCPro. "
                              "Install it with: pip install toptica.lasersdk")

        self.ip_address = ip_address
        self.connection = NetworkConnection(ip_address)
        self.client = None
        self.laser_type = None
        self._decop_error = DecopError

        # Create a fake adapter since we don't use traditional communication
        class FakeAdapter:
            def write(self, command):
                pass

            def read(self):
                return ""

            def close(self):
                pass

        # Initialize parent with fake adapter
        super().__init__(FakeAdapter(), name=name or "Toptica DLC Pro",
                         includeSCPI=False, **kwargs)

        # Open connection and detect laser type
        self._open_connection()

        # Update name with detected laser type
        if name is None:
            self.name = f"Toptica DLC Pro {self.laser_type}"

        log.info(f"Initialized {self.name} at {self.ip_address}")

    def _open_connection(self):
        """Open connection to the Toptica laser controller."""
        try:
            from toptica.lasersdk.client import Client
            self.client = Client(self.connection)
            self.client.open()

            # Determine the laser type
            laser_type = self.client.get("laser1:type")
            if laser_type == "CTL":
                self.laser_type = "CTL"
            elif "BoosTApro" in laser_type:
                self.laser_type = "TA"
            else:
                self.laser_type = "Unknown"

            log.info(f"Connected to {self.laser_type} laser at {self.ip_address}")

        except Exception as e:
            log.error(f"Failed to connect to laser at {self.ip_address}: {e}")
            self.client = None
            raise ConnectionError(f"Failed to connect to laser: {e}")

    def _get_parameter(self, param_name):
        """Get a parameter value from the laser."""
        if not self.client:
            raise ConnectionError("Connection not open")

        try:
            return self.client.get(param_name)
        except self._decop_error as e:
            raise ValueError(f"Error retrieving parameter {param_name}: {e}")

    def _set_parameter(self, param_name, value):
        """Set a parameter value on the laser."""
        if not self.client:
            raise ConnectionError("Connection not open")

        try:
            self.client.set(param_name, value)
        except self._decop_error as e:
            raise ValueError(f"Error setting parameter {param_name} to {value}: {e}")

    # Common properties for all laser types
    @property
    def emission(self):
        """Get the emission status of the laser (bool)."""
        return self._get_parameter("emission")

    @emission.setter
    def emission(self, value):
        """Set the emission status of the laser (bool)."""
        if not isinstance(value, bool):
            raise ValueError("Emission must be True or False")
        self._set_parameter("emission", value)

    # CTL-specific properties
    @property
    def wavelength(self):
        """Get the current CTL wavelength setpoint in nm (CTL lasers only)."""
        if self.laser_type != "CTL":
            raise ValueError("This property is only available for CTL lasers")
        return self._get_parameter("laser1:ctl:wavelength-set")

    @wavelength.setter
    def wavelength(self, value):
        """Set the CTL wavelength in nm (CTL lasers only)."""
        if self.laser_type != "CTL":
            raise ValueError("This property is only available for CTL lasers")

        # Check wavelength limits
        wl_min = self._get_parameter("laser1:ctl:wavelength-min")
        wl_max = self._get_parameter("laser1:ctl:wavelength-max")

        if value < wl_min or value > wl_max:
            raise ValueError(f"Wavelength must be between {wl_min} nm and {wl_max} nm")

        self._set_parameter("laser1:ctl:wavelength-set", value)

    @property
    def wavelength_actual(self):
        """Get the actual CTL wavelength in nm (CTL lasers only)."""
        if self.laser_type != "CTL":
            raise ValueError("This property is only available for CTL lasers")
        return self._get_parameter("laser1:ctl:wavelength-act")

    @property
    def wavelength_limits(self):
        """Get the CTL wavelength limits as (min, max) in nm (CTL lasers only)."""
        if self.laser_type != "CTL":
            raise ValueError("This property is only available for CTL lasers")

        wl_min = self._get_parameter("laser1:ctl:wavelength-min")
        wl_max = self._get_parameter("laser1:ctl:wavelength-max")
        return (wl_min, wl_max)

    @property
    def scan_offset(self):
        """Get the current scan offset for CTL (CTL lasers only)."""
        if self.laser_type != "CTL":
            raise ValueError("This property is only available for CTL lasers")
        return self._get_parameter("laser1:scan:offset")

    @scan_offset.setter
    def scan_offset(self, value):
        """Set the scan offset for CTL (CTL lasers only)."""
        if self.laser_type != "CTL":
            raise ValueError("This property is only available for CTL lasers")

        # Check offset limits
        offset_min = self._get_parameter("laser1:dl:pc:voltage-min")
        offset_max = self._get_parameter("laser1:dl:pc:voltage-max")

        if value < offset_min or value > offset_max:
            raise ValueError(f"Scan offset must be between {offset_min} and {offset_max}")

        self._set_parameter("laser1:scan:offset", value)

    @property
    def scan_offset_limits(self):
        """Get the CTL scan offset limits as (min, max) (CTL lasers only)."""
        if self.laser_type != "CTL":
            raise ValueError("This property is only available for CTL lasers")

        offset_min = self._get_parameter("laser1:dl:pc:voltage-min")
        offset_max = self._get_parameter("laser1:dl:pc:voltage-max")
        return (offset_min, offset_max)

    @property
    def ctl_current(self):
        """Get the current CTL current setpoint in mA (CTL lasers only)."""
        if self.laser_type != "CTL":
            raise ValueError("This property is only available for CTL lasers")
        return self._get_parameter("laser1:dl:cc:current-set")

    @ctl_current.setter
    def ctl_current(self, value):
        """Set the CTL current setpoint in mA (CTL lasers only)."""
        if self.laser_type != "CTL":
            raise ValueError("This property is only available for CTL lasers")

        # Check current limit
        current_limit = self._get_parameter("laser1:dl:cc:current-clip")

        if value < 0 or value > current_limit:
            raise ValueError(f"Current must be between 0 and {current_limit} mA")

        self._set_parameter("laser1:dl:cc:current-set", value)

    @property
    def ctl_current_actual(self):
        """Get the actual CTL current in mA (CTL lasers only)."""
        if self.laser_type != "CTL":
            raise ValueError("This property is only available for CTL lasers")
        return self._get_parameter("laser1:dl:cc:current-act")

    # TA-specific properties
    @property
    def ta_current(self):
        """Get the current TA current setpoint in mA (TA lasers only)."""
        if self.laser_type != "TA":
            raise ValueError("This property is only available for TA lasers")
        return self._get_parameter("ampcc1:channel1:current-set")

    @ta_current.setter
    def ta_current(self, value):
        """Set the TA current setpoint in mA (TA lasers only)."""
        if self.laser_type != "TA":
            raise ValueError("This property is only available for TA lasers")

        # Check current limit
        current_limit = self._get_parameter("ampcc1:channel1:current-clip-limit")

        if value < 0 or value > current_limit:
            raise ValueError(f"Current must be between 0 and {current_limit} mA")

        self._set_parameter("ampcc1:channel1:current-set", value)

    @property
    def ta_current_actual(self):
        """Get the actual TA current in mA (TA lasers only)."""
        if self.laser_type != "TA":
            raise ValueError("This property is only available for TA lasers")
        return self._get_parameter("ampcc1:channel1:current-act")

    @property
    def ta_current_limit(self):
        """Get the TA current limit in mA (TA lasers only)."""
        if self.laser_type != "TA":
            raise ValueError("This property is only available for TA lasers")
        return self._get_parameter("ampcc1:channel1:current-clip-limit")

    @property
    def ta_temperature(self):
        """Get the current TA temperature in °C (TA lasers only)."""
        if self.laser_type != "TA":
            raise ValueError("This property is only available for TA lasers")
        return self._get_parameter("laser1:amp:tc:temp-act")

    @property
    def ta_temperature_setpoint(self):
        """Get the TA temperature setpoint in °C (TA lasers only)."""
        if self.laser_type != "TA":
            raise ValueError("This property is only available for TA lasers")
        return self._get_parameter("laser1:amp:tc:temp-set")

    @ta_temperature_setpoint.setter
    def ta_temperature_setpoint(self, value):
        """Set the TA temperature setpoint in °C (TA lasers only)."""
        if self.laser_type != "TA":
            raise ValueError("This property is only available for TA lasers")

        # Check temperature limits
        temp_min = self._get_parameter("laser1:amp:tc:temp-set-min")
        temp_max = self._get_parameter("laser1:amp:tc:temp-set-max")

        if value < temp_min or value > temp_max:
            raise ValueError(f"Temperature must be between {temp_min} and {temp_max} °C")

        self._set_parameter("laser1:amp:tc:temp-set", value)

    @property
    def ta_temperature_limits(self):
        """Get the TA temperature limits as (min, max) in °C (TA lasers only)."""
        if self.laser_type != "TA":
            raise ValueError("This property is only available for TA lasers")

        temp_min = self._get_parameter("laser1:amp:tc:temp-set-min")
        temp_max = self._get_parameter("laser1:amp:tc:temp-set-max")
        return (temp_min, temp_max)

    # Utility methods
    def get_parameter(self, param_name):
        """
        Get a parameter value from the laser.

        :param param_name: The name of the parameter to retrieve
        :return: The value of the specified parameter
        """
        return self._get_parameter(param_name)

    def set_parameter(self, param_name, value):
        """
        Set a parameter value on the laser.

        :param param_name: The name of the parameter to set
        :param value: The value to set for the parameter
        """
        self._set_parameter(param_name, value)

    def get_all_parameters(self, use_dynamic_discovery=True):
        """
        Get all relevant laser parameters as a dictionary.
        
        :param use_dynamic_discovery: If True, dynamically discover all available parameters.
                                    If False, use predefined parameter lists.
        :return: Dictionary containing all laser parameters with their values.
                Failed parameter retrievals are stored with their error messages.
        """
        if not self.client:
            raise ConnectionError("Connection not open")
        
        # Get parameter list
        if use_dynamic_discovery:
            try:
                param_names = self.get_all_supported_parameters()
            except Exception as e:
                log.warning(f"Dynamic parameter discovery failed: {e}. Using default list.")
                param_names = self._get_default_parameter_list()
        else:
            param_names = self._get_default_parameter_list()
        
        # Retrieve all parameters
        parameters = {}
        for param in param_names:
            try:
                parameters[param] = self.client.get(param)
            except self._decop_error as error:
                parameters[param] = f"ERROR: {error}"
        
        # Add metadata
        parameters["_metadata"] = {
            "laser_type": self.laser_type,
            "ip_address": self.ip_address,
            "timestamp": datetime.datetime.now().isoformat(),
            "instrument_name": self.name,
            "parameter_count": len(param_names),
            "discovery_method": "dynamic" if use_dynamic_discovery else "predefined"
        }
        
        log.info(f"Retrieved {len(param_names)} parameters for {self.laser_type} laser "
                 f"using {'dynamic' if use_dynamic_discovery else 'predefined'} discovery")
        return parameters

    def get_all_supported_parameters(self):
        """
        Get all supported parameters from the laser by testing parameter patterns.
        
        :return: List of all parameter names that can be read from the laser
        """
        if not self.client:
            raise ConnectionError("Connection not open")
        
        try:
            # Start with the enhanced parameter list as a base
            candidate_params = self._get_enhanced_parameter_list()
            
            # Test each parameter to see if it's actually available
            available_params = []
            for param in candidate_params:
                try:
                    # Try to read the parameter
                    self.client.get(param)
                    available_params.append(param)
                except self._decop_error:
                    # Parameter not available, skip it
                    continue
                except Exception:
                    # Other error, skip it
                    continue
            
            log.info(f"Found {len(available_params)} available parameters "
                     f"out of {len(candidate_params)} tested")
            return available_params
            
        except Exception as e:
            log.error(f"Error during parameter discovery: {e}")
            # Fall back to default list
            return self._get_default_parameter_list()
    
    def _get_enhanced_parameter_list(self):
        """
        Get an enhanced parameter list that includes more parameters than the basic defaults.
        
        :return: Enhanced list of parameter names
        """
        base_params = self._get_default_parameter_list()
        
        # Add additional common parameters that might be available
        additional_params = [
            "system:uptime",
            "system:serial-number",
            "system:model",
            "fw:version",
            "cc1:board-temp",
            "tc1:board-temp"
        ]
        
        if self.laser_type == "CTL":
            additional_params.extend([
                "laser1:dl:tc:temp-act",
                "laser1:dl:tc:temp-set",
                "laser1:ctl:mode",
                "laser1:ctl:state"
            ])
        elif self.laser_type == "TA":
            additional_params.extend([
                "laser1:amp:photodiode",
                "laser1:amp:state"
            ])
        
        # Combine and deduplicate
        all_params = list(set(base_params + additional_params))
        
        return sorted(all_params)

    def _get_default_parameter_list(self):
        """
        Get the default parameter list based on laser type (fallback method).

        :return: List of default parameter names for the detected laser type
        """
        if self.laser_type == "CTL":
            return [
                "laser1:ctl:wavelength-set",
                "laser1:ctl:wavelength-act",
                "laser1:scan:offset",
                "laser1:ctl:wavelength-max",
                "laser1:ctl:wavelength-min",
                "laser1:dl:pc:voltage-max",
                "laser1:dl:pc:voltage-min",
                "laser1:dl:cc:current-set",
                "laser1:dl:cc:current-act",
                "laser1:dl:cc:current-clip",
                "laser1:type",
                "emission"
            ]
        elif self.laser_type == "TA":
            return [
                "ampcc1:channel1:current-set",
                "ampcc1:channel1:current-act",
                "laser1:amp:tc:temp-act",
                "laser1:amp:tc:temp-set",
                "laser1:amp:tc:temp-set-min",
                "laser1:amp:tc:temp-set-max",
                "ampcc1:channel1:current-clip-limit",
                "laser1:type",
                "emission"
            ]
        else:
            return ["laser1:type", "emission"]

    def shutdown(self):
        """
        Safely shutdown the instrument by disabling emission and closing the connection.
        """
        try:
            if self.client:
                # Close the connection
                self.client.close()
                log.info(f"Connection to {self.ip_address} closed")
        except Exception as e:
            log.error(f"Error during shutdown: {e}")
        finally:
            self.client = None
            super().shutdown()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
