import logging
import json
from calculator import VedicAstroCalculator

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Check if handlers already exist to avoid duplicate logs in tests
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Application started: vedic-astro-calculator")
    print("Welcome to vedic-astro-calculator!")
    
    # J2000 epoch as an example JD
    jd = 2451545.0
    logger.info("Calculating planetary positions for Julian Date (JD): %s", jd)
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
