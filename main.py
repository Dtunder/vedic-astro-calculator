import logging
import json
from calculator import VedicAstroCalculator
from config import CONFIG


class JsonFormatter(logging.Formatter):
    """
    A custom logging formatter that outputs log records as JSON strings.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the given log record into a JSON string.

        Args:
            record: The log record to format.

        Returns:
            The formatted log record as a JSON string.
        """
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logging() -> None:
    """
    Configures root logger to output JSON logs to standard output.
    Avoids adding duplicate handlers if they are already configured.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Check if handlers already exist to avoid duplicate logs in tests
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def main() -> None:
    """
    The main execution entrypoint for the vedic-astro-calculator application.
    Calculates and prints longitudes for the J2000 epoch.
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Application started: vedic-astro-calculator")
    print("Welcome to vedic-astro-calculator!")

    # Load jd from configuration
    jd = CONFIG["main"]["jd"]
    logger.info("Calculating positions for Julian Date (JD): %s", jd)
    print(f"Calculating planetary positions for Julian Date (JD): {jd}\n")

    calc = VedicAstroCalculator()

    raw = calc.calculate_raw_positions(jd)
    print("--- Sayana (Tropical) Longitudes ---")
    for planet, lon in raw.items():
        print(f"{planet:>8}: {lon:.4f}°")

    print("\n")
    ayanamsa = calc.get_lahiri_ayanamsa(jd)
    print(f"Lahiri Ayanamsa: {ayanamsa:.4f}°\n")

    nirayana = calc.calculate_nirayana_longitudes(jd)
    print("--- Nirayana (Sidereal) Longitudes ---")
    for planet, lon in nirayana.items():
        print(f"{planet:>8}: {lon:.4f}°")

    logger.info("Application finished successfully")


if __name__ == "__main__":
    main()
