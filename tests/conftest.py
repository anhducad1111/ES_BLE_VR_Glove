"""
Test Configuration and Shared Fixtures
"""
import pytest
from unittest.mock import MagicMock

from src.model.ble_service import BLEService
from src.model.imu import IMUData, IMUEulerData
from src.model.sensor import Sensor
from src.view.main_view import MainView


@pytest.fixture
def mock_ble_service():
    """Fixture providing a mocked BLE service."""
    service = MagicMock(spec=BLEService)
    return service


@pytest.fixture
def mock_imu_data():
    """Fixture providing mocked IMU data."""
    imu_data = MagicMock(spec=IMUData)
    return imu_data

@pytest.fixture
def mock_imu_euler():
    """Fixture providing mocked IMU Euler data."""
    imu_euler = MagicMock(spec=IMUEulerData)
    return imu_euler


@pytest.fixture
def mock_sensor():
    """Fixture providing a mocked sensor."""
    sensor = MagicMock(spec=Sensor)
    return sensor


@pytest.fixture
def mock_main_view():
    """Fixture providing a mocked main view."""
    view = MagicMock(spec=MainView)
    return view