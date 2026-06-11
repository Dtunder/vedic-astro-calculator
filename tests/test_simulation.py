import unittest
from unittest.mock import patch, MagicMock

from simulation import (
    RemoteConfigurationService,
    NetworkError,
    TimeoutError,
    BadConfigurationError,
)


class TestSimulation(unittest.TestCase):
    def setUp(self) -> None:
        # Create service with 100% failure rate
        self.service = RemoteConfigurationService(failure_rate=1.0)

    @patch("simulation.random.random", return_value=1.0)
    def test_fetch_config_success(self, mock_random: MagicMock) -> None:
        service = RemoteConfigurationService(failure_rate=0.5)
        result = service.fetch_config()
        self.assertEqual(result["status"], "success")
        self.assertEqual(service.call_count, 1)

    @patch("simulation.random.choice", return_value=NetworkError)
    def test_fetch_config_network_error_triggers_fallback(
        self, mock_choice: MagicMock
    ) -> None:
        # Always fail with NetworkError. Should retry 3 times, then fallback.
        result = self.service.fetch_config()
        self.assertEqual(result["status"], "fallback")
        # 1 initial try + 3 retries = 4 total calls
        self.assertEqual(self.service.call_count, 4)

    @patch("simulation.random.choice", return_value=TimeoutError)
    def test_fetch_config_timeout_error_triggers_fallback(
        self, mock_choice: MagicMock
    ) -> None:
        # Always fail with TimeoutError. Should retry 3 times, then fallback.
        result = self.service.fetch_config()
        self.assertEqual(result["status"], "fallback")
        self.assertEqual(self.service.call_count, 4)

    @patch("simulation.random.choice", return_value=BadConfigurationError)
    def test_fetch_config_bad_configuration_triggers_fallback(
        self, mock_choice: MagicMock
    ) -> None:
        # Always fail with BadConfigurationError.
        # Should retry 3 times, then fallback.
        result = self.service.fetch_config()
        self.assertEqual(result["status"], "fallback")
        self.assertEqual(self.service.call_count, 4)


if __name__ == "__main__":
    unittest.main()
