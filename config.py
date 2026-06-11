import json
import os
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

DEFAULT_CONFIG: Dict[str, Any] = {
    "simulation": {
        "failure_rate": 0.5,
        "fallback": {
            "api_url": "http://localhost:8080/api",
            "timeout_ms": 5000,
            "features": {"advanced_calc": False},
        },
        "success": {
            "api_url": "https://api.vedic-astro.remote/v1",
            "timeout_ms": 2000,
            "features": {"advanced_calc": True},
        },
        "retry": {"retries": 3, "delay": 0.1, "backoff": 2.0},
    },
    "main": {"jd": 2451545.0},
}


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    config: Dict[str, Any] = DEFAULT_CONFIG.copy()
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                loaded_config = json.load(f)

            # Merge loaded config over default config
            for key, value in loaded_config.items():
                if isinstance(value, dict) and key in config:
                    config[key].update(value)
                else:
                    config[key] = value
        except Exception as e:
            logger.warning(f"Could not load config from {config_path}: {e}")

    # Allow environment variables to override some key settings
    # E.g. VEDIC_ASTRO_JD
    jd_env = os.environ.get("VEDIC_ASTRO_JD")
    if jd_env:
        try:
            config["main"]["jd"] = float(jd_env)
        except ValueError:
            pass

    return config


CONFIG = load_config()
