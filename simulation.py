import logging
import random
from typing import Dict, Any

from resilience import retry_with_fallback

logger = logging.getLogger(__name__)


class NetworkError(Exception):
    """Exception raised for simulated network errors."""

    pass


class TimeoutError(Exception):
    """Exception raised for simulated timeout errors."""

    pass


class BadConfigurationError(Exception):
    """Exception raised for simulated bad configuration errors."""

    pass


def local_fallback_config(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Fallback function that returns a default local configuration.
    """
    logger.info("Using local fallback configuration.")
    return {
        "status": "fallback",
        "api_url": "http://localhost:8080/api",
        "timeout_ms": 5000,
        "features": {"advanced_calc": False},
    }


class RemoteConfigurationService:
    """
    Simulates a remote service that provides configuration data
    but is prone to failures.
    """

    def __init__(self, failure_rate: float = 0.5) -> None:
        """
        Args:
            failure_rate (float): Probability (0.0 to 1.0) of a call failing.
        """
        self.failure_rate = failure_rate
        self.call_count = 0

    @retry_with_fallback(
        retries=3,
        delay=0.1,  # Short delay for testing/simulation
        backoff=2.0,
        exceptions=(NetworkError, TimeoutError, BadConfigurationError),
        fallback=local_fallback_config,
    )
    def fetch_config(self) -> Dict[str, Any]:
        """
        Simulates fetching configuration from a remote server.
        May randomly fail with NetworkError or TimeoutError.
        """
        self.call_count += 1
        logger.info(
            "Fetching configuration from remote server... (attempt %d)",
            self.call_count,
        )

        if random.random() < self.failure_rate:
            error_type = random.choice(
                [NetworkError, TimeoutError, BadConfigurationError]
            )

            if error_type == NetworkError:
                raise NetworkError("Connection refused by remote host.")
            elif error_type == TimeoutError:
                raise TimeoutError("Request to remote host timed out.")
            else:
                raise BadConfigurationError(
                    "Remote host returned invalid configuration data."
                )

        logger.info("Successfully fetched remote configuration.")
        return {
            "status": "success",
            "api_url": "https://api.vedic-astro.remote/v1",
            "timeout_ms": 2000,
            "features": {"advanced_calc": True},
        }
