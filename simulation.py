import logging
import random
from typing import Dict, Any

from resilience import retry_with_fallback
from config import CONFIG

logger = logging.getLogger(__name__)


class NetworkError(Exception):
    """Exception raised for simulated network errors."""




class TimeoutError(Exception):
    """Exception raised for simulated timeout errors."""




class BadConfigurationError(Exception):
    """Exception raised for simulated bad configuration errors."""




def local_fallback_config(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Fallback function that returns a default local configuration.
    """
    logger.info("Using local fallback configuration.")
    fallback_cfg: Dict[str, Any] = CONFIG["simulation"]["fallback"].copy()
    fallback_cfg["status"] = "fallback"
    return fallback_cfg


class RemoteConfigurationService:
    """
    Simulates a remote service that provides configuration data
    but is prone to failures.
    """

    def __init__(self, failure_rate: float = -1.0) -> None:
        """
        Args:
            failure_rate (float): Probability (0.0 to 1.0) of a call failing.
        """
        if failure_rate == -1.0:
            self.failure_rate = float(CONFIG["simulation"]["failure_rate"])
        else:
            self.failure_rate = failure_rate
        self.call_count = 0

    @retry_with_fallback(
        retries=CONFIG["simulation"]["retry"]["retries"],
        delay=CONFIG["simulation"]["retry"]["delay"],
        backoff=CONFIG["simulation"]["retry"]["backoff"],
        exceptions=(NetworkError, TimeoutError, BadConfigurationError),
        fallback=local_fallback_config,
    )
    def fetch_config(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
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
            if error_type == TimeoutError:
                raise TimeoutError("Request to remote host timed out.")
            raise BadConfigurationError(
                "Remote host returned invalid configuration data."
            )

        logger.info("Successfully fetched remote configuration.")
        success_cfg: Dict[str, Any] = CONFIG["simulation"]["success"].copy()
        success_cfg["status"] = "success"
        return success_cfg
