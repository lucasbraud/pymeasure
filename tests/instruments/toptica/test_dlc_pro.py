"""
Tests for the Toptica DLC Pro PyMeasure wrapper.

These tests use mocking to simulate the Toptica SDK since the actual hardware
may not be available during testing.
"""

import pytest
from unittest.mock import Mock, patch
from pymeasure.instruments.toptica import TopticaDLCPro


class TestTopticaDLCPro:
    """Test cases for the TopticaDLCPro instrument."""

    @patch('toptica.lasersdk.client.NetworkConnection')
    def test_ctl_laser_initialization(self, mock_network_connection):
        """Test initialization of CTL laser."""
        # Mock the Toptica SDK
        mock_client = Mock()
        mock_client.get.return_value = "CTL"
        
        with patch('toptica.lasersdk.client.Client') as mock_client_class:
            mock_client_class.return_value = mock_client
            
            # Initialize the instrument
            laser = TopticaDLCPro("192.168.1.44")
            
            # Verify initialization
            assert laser.ip_address == "192.168.1.44"
            assert laser.laser_type == "CTL"
            assert laser.name == "Toptica DLC Pro CTL"
            
            # Verify SDK calls
            mock_client.open.assert_called_once()
            mock_client.get.assert_called_with("laser1:type")

    @patch('toptica.lasersdk.client.NetworkConnection')
    def test_ta_laser_initialization(self, mock_network_connection):
        """Test initialization of TA laser."""
        # Mock the Toptica SDK
        mock_client = Mock()
        mock_client.get.return_value = "BoosTApro"
        
        with patch('toptica.lasersdk.client.Client') as mock_client_class:
            mock_client_class.return_value = mock_client
            
            # Initialize the instrument
            laser = TopticaDLCPro("192.168.1.104")
            
            # Verify initialization
            assert laser.ip_address == "192.168.1.104"
            assert laser.laser_type == "TA"
            assert laser.name == "Toptica DLC Pro TA"

    @patch('toptica.lasersdk.client.NetworkConnection')
    def test_emission_property(self, mock_network_connection):
        """Test emission property getter and setter."""
        mock_client = Mock()
        mock_client.get.side_effect = lambda param: {
            "laser1:type": "CTL",
            "emission": True
        }[param]
        
        with patch('toptica.lasersdk.client.Client') as mock_client_class:
            mock_client_class.return_value = mock_client
            
            laser = TopticaDLCPro("192.168.1.44")
            
            # Test getter
            assert laser.emission is True
            mock_client.get.assert_called_with("emission")
            
            # Test setter
            laser.emission = False
            mock_client.set.assert_called_with("emission", False)

    @patch('toptica.lasersdk.client.NetworkConnection')
    def test_ctl_wavelength_property(self, mock_network_connection):
        """Test CTL wavelength property."""
        mock_client = Mock()
        mock_client.get.side_effect = lambda param: {
            "laser1:type": "CTL",
            "laser1:ctl:wavelength-set": 1550.0,
            "laser1:ctl:wavelength-act": 1549.98,
            "laser1:ctl:wavelength-min": 1500.0,
            "laser1:ctl:wavelength-max": 1600.0
        }[param]
        
        with patch('toptica.lasersdk.client.Client') as mock_client_class:
            mock_client_class.return_value = mock_client
            
            laser = TopticaDLCPro("192.168.1.44")
            
            # Test getter
            assert laser.wavelength == 1550.0
            mock_client.get.assert_called_with("laser1:ctl:wavelength-set")
            
            # Test actual wavelength
            assert laser.wavelength_actual == 1549.98
            
            # Test wavelength limits
            limits = laser.wavelength_limits
            assert limits == (1500.0, 1600.0)
            
            # Test setter within limits
            laser.wavelength = 1555.0
            mock_client.set.assert_called_with("laser1:ctl:wavelength-set", 1555.0)

    @patch('toptica.lasersdk.client.NetworkConnection')
    def test_ctl_wavelength_out_of_range(self, mock_network_connection):
        """Test CTL wavelength property with out-of-range value."""
        mock_client = Mock()
        mock_client.get.side_effect = lambda param: {
            "laser1:type": "CTL",
            "laser1:ctl:wavelength-min": 1500.0,
            "laser1:ctl:wavelength-max": 1600.0
        }[param]
        
        with patch('toptica.lasersdk.client.Client') as mock_client_class:
            mock_client_class.return_value = mock_client
            
            laser = TopticaDLCPro("192.168.1.44")
            
            # Test setting wavelength out of range
            with pytest.raises(ValueError, match="Wavelength must be between"):
                laser.wavelength = 1700.0

    @patch('toptica.lasersdk.client.NetworkConnection')
    def test_ta_current_property(self, mock_network_connection):
        """Test TA current property."""
        mock_client = Mock()
        mock_client.get.side_effect = lambda param: {
            "laser1:type": "BoosTApro",
            "ampcc1:channel1:current-set": 800.0,
            "ampcc1:channel1:current-act": 799.5,
            "ampcc1:channel1:current-clip-limit": 1000.0
        }[param]
        
        with patch('toptica.lasersdk.client.Client') as mock_client_class:
            mock_client_class.return_value = mock_client
            
            laser = TopticaDLCPro("192.168.1.104")
            
            # Test getter
            assert laser.ta_current == 800.0
            mock_client.get.assert_called_with("ampcc1:channel1:current-set")
            
            # Test actual current
            assert laser.ta_current_actual == 799.5
            
            # Test current limit
            assert laser.ta_current_limit == 1000.0
            
            # Test setter within limits
            laser.ta_current = 850.0
            mock_client.set.assert_called_with("ampcc1:channel1:current-set", 850.0)

    @patch('toptica.lasersdk.client.NetworkConnection')
    def test_wrong_laser_type_access(self, mock_network_connection):
        """Test accessing TA properties on CTL laser raises error."""
        mock_client = Mock()
        mock_client.get.return_value = "CTL"
        
        with patch('toptica.lasersdk.client.Client') as mock_client_class:
            mock_client_class.return_value = mock_client
            
            laser = TopticaDLCPro("192.168.1.44")
            
            # Test accessing TA property on CTL laser
            with pytest.raises(ValueError, match="only available for TA lasers"):
                _ = laser.ta_current

    @patch('toptica.lasersdk.client.NetworkConnection')
    def test_generic_parameter_access(self, mock_network_connection):
        """Test generic parameter access methods."""
        mock_client = Mock()
        mock_client.get.side_effect = lambda param: {
            "laser1:type": "CTL",
            "custom:parameter": "test_value"
        }[param]
        
        with patch('toptica.lasersdk.client.Client') as mock_client_class:
            mock_client_class.return_value = mock_client
            
            laser = TopticaDLCPro("192.168.1.44")
            
            # Test get_parameter
            value = laser.get_parameter("custom:parameter")
            assert value == "test_value"
            
            # Test set_parameter
            laser.set_parameter("custom:parameter", "new_value")
            mock_client.set.assert_called_with("custom:parameter", "new_value")

    @patch('toptica.lasersdk.client.NetworkConnection')
    def test_get_all_parameters(self, mock_network_connection):
        """Test parameter retrieval functionality."""
        mock_client = Mock()
        mock_client.get.side_effect = lambda param: {
            "laser1:type": "CTL",
            "laser1:ctl:wavelength-set": 1550.0,
            "emission": False
        }.get(param, f"value_for_{param}")
        
        with patch('toptica.lasersdk.client.Client') as mock_client_class:
            mock_client_class.return_value = mock_client
            
            laser = TopticaDLCPro("192.168.1.44")
            
            # Test get all parameters
            params = laser.get_all_parameters()
            
            # Check that we got a dictionary
            assert isinstance(params, dict)
            
            # Check metadata is included
            assert "_metadata" in params
            assert params["_metadata"]["laser_type"] == "CTL"
            assert params["_metadata"]["ip_address"] == "192.168.1.44"
            
            # Check some parameters are included
            assert "laser1:ctl:wavelength-set" in params
            assert "emission" in params

    @patch('toptica.lasersdk.client.NetworkConnection')
    def test_context_manager(self, mock_network_connection):
        """Test context manager functionality."""
        mock_client = Mock()
        mock_client.get.return_value = "CTL"
        
        with patch('toptica.lasersdk.client.Client') as mock_client_class:
            mock_client_class.return_value = mock_client
            
            # Test context manager
            with TopticaDLCPro("192.168.1.44") as laser:
                assert laser.laser_type == "CTL"
            
            # Verify shutdown was called
            mock_client.set.assert_called_with("emission", False)
            mock_client.close.assert_called_once()

    def test_sdk_import_error(self):
        """Test proper error handling when SDK is not available."""
        with patch('pymeasure.instruments.toptica.dlc_pro.ImportError', ImportError):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'toptica'")):
                with pytest.raises(ImportError, match="toptica.lasersdk is required"):
                    TopticaDLCPro("192.168.1.44")


if __name__ == "__main__":
    pytest.main([__file__])
