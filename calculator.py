import math
import logging
from typing import Dict, Tuple, Union

logger = logging.getLogger(__name__)


class VedicAstroCalculator:
    """
    A calculator for computing planetary coordinates for Vedic astrology.

    This class precomputes elements at instantiation based on the J2000 epoch
    to quickly calculate both raw (Sayana/tropical) and Nirayana (sidereal)
    planetary longitudes for the 9 Vedic grahas.
    """

    def __init__(self) -> None:
        """
        Initializes the calculator with J2000 epoch and precomputes constants.
        """
        logger.info("Initializing VedicAstroCalculator with J2000 epoch")
        # J2000 epoch
        self.epoch: float = 2451545.0

        # Simplified Keplerian elements (J2000)
        # a: semi-major axis (AU)
        # e: eccentricity
        # I: inclination (deg)
        # L: mean longitude (deg)
        # omega_bar: longitude of perihelion (deg)
        # Omega: longitude of ascending node (deg)
        # n: daily motion (deg/day)

        raw_elements = {
            "Earth": {
                "a": 1.000000,
                "e": 0.016710,
                "I": 0.00005,
                "L": 100.46435,
                "omega_bar": 102.9404,
                "Omega": 0.0,
                "n": 0.9856091,
            },
            "Mercury": {
                "a": 0.387099,
                "e": 0.205630,
                "I": 7.005,
                "L": 252.25032,
                "omega_bar": 77.45779,
                "Omega": 48.33076,
                "n": 4.0923344,
            },
            "Venus": {
                "a": 0.723332,
                "e": 0.006773,
                "I": 3.3946,
                "L": 181.97909,
                "omega_bar": 131.5637,
                "Omega": 76.67984,
                "n": 1.6021302,
            },
            "Mars": {
                "a": 1.523679,
                "e": 0.093400,
                "I": 1.8497,
                "L": 355.43327,
                "omega_bar": 336.0602,
                "Omega": 49.5581,
                "n": 0.5240207,
            },
            "Jupiter": {
                "a": 5.202603,
                "e": 0.048498,
                "I": 1.303,
                "L": 34.35148,
                "omega_bar": 14.3313,
                "Omega": 100.4643,
                "n": 0.0830853,
            },
            "Saturn": {
                "a": 9.554909,
                "e": 0.055546,
                "I": 2.488,
                "L": 50.07747,
                "omega_bar": 93.0567,
                "Omega": 113.6634,
                "n": 0.0334442,
            },
        }

        self.elements: Dict[str, Dict[str, float]] = {}
        for planet, elem in raw_elements.items():
            e = elem["e"]
            I_rad = math.radians(elem["I"])
            Omega_rad = math.radians(elem["Omega"])
            omega_bar_rad = math.radians(elem["omega_bar"])
            w_rad = omega_bar_rad - Omega_rad

            self.elements[planet] = {
                "a": elem["a"],
                "e": e,
                "L": elem["L"],
                "n": elem["n"],
                "omega_bar": elem["omega_bar"],
                "I_rad": I_rad,
                "Omega_rad": Omega_rad,
                "w_rad": w_rad,
                "sqrt_1_plus_e": math.sqrt(1 + e),
                "sqrt_1_minus_e": math.sqrt(1 - e),
                "cos_Omega": math.cos(Omega_rad),
                "sin_Omega": math.sin(Omega_rad),
                "cos_I": math.cos(I_rad),
            }

        logger.debug(
            "Precomputing orbital elements for %d planets", len(raw_elements)
        )
        # Moon specific precomputed constants
        self.e_moon = 0.0549
        self.I_moon = math.radians(5.145)
        self.cos_I_moon = math.cos(self.I_moon)
        self.sqrt_1_plus_e_moon = math.sqrt(1 + self.e_moon)
        self.sqrt_1_minus_e_moon = math.sqrt(1 - self.e_moon)

    def solve_kepler(
        self, mean_anomaly: Union[int, float], eccentricity: Union[int, float]
    ) -> float:
        """
        Solves Kepler's equation M = E - e*sin(E) using Newton's method.

        Args:
            M (Union[int, float]): Mean anomaly in degrees.
            e (Union[int, float]): Eccentricity.

        Returns:
            float: Eccentric anomaly in radians.
        """
        if not isinstance(mean_anomaly, (int, float)) or not isinstance(
            eccentricity, (int, float)
        ):
            logger.error(
                "Invalid types: mean_anomaly=%s, ecc=%s",
                type(mean_anomaly),
                type(eccentricity),
            )
            raise TypeError("mean_anomaly and eccentricity must be numbers.")
        if not (0 <= eccentricity < 1):
            logger.error("Eccentricity out of bounds: %s", eccentricity)
            raise ValueError("Eccentricity must be in the range [0, 1).")

        logger.debug(
            "Solving Kepler's equation for mean anomaly=%s, eccentricity=%s",
            mean_anomaly,
            eccentricity,
        )
        m_rad = math.radians(mean_anomaly)
        e_anom = m_rad
        for _ in range(10):
            try:
                cos_e_anom = math.cos(e_anom)
                denominator = 1 - eccentricity * cos_e_anom
                if denominator == 0:
                    raise ZeroDivisionError(
                        "Denominator in Newton's method became zero."
                    )
                delta_e_anom = (
                    e_anom - eccentricity * math.sin(e_anom) - m_rad
                ) / denominator
            except ZeroDivisionError as err:
                logger.exception("Zero division in Newton's method")
                raise ValueError(f"Failed to solve Kepler's equation: {err}")

            e_anom -= delta_e_anom
            if abs(delta_e_anom) < 1e-6:
                break
        return e_anom

    def calculate_heliocentric(
        self, planet: str, days_since_epoch: Union[int, float]
    ) -> Tuple[float, float, float]:
        """
        Calculates heliocentric ecliptic coordinates.

        Args:
            planet (str): Name of the planet.
            d (Union[int, float]): Days since epoch.

        Returns:
            Tuple[float, float, float]: A tuple of (x, y, z) coordinates in AU.
        """
        if not isinstance(planet, str):
            logger.error("Planet name is not a string: %s", type(planet))
            raise TypeError("Planet name must be a string.")
        if planet not in self.elements:
            logger.error("Planet not found: %s", planet)
            raise ValueError(f"Planet '{planet}' not found in elements.")
        if not isinstance(days_since_epoch, (int, float)):
            logger.error("Days since epoch is not a number.")
            raise TypeError("Days since epoch must be a number.")

        logger.debug(
            "Calculating heliocentric coordinates for %s at days=%s",
            planet,
            days_since_epoch,
        )
        elem = self.elements[planet]
        a = elem["a"]
        e = elem["e"]
        l_mean = elem["L"] + elem["n"] * days_since_epoch
        omega_bar = elem["omega_bar"]

        m = (l_mean - omega_bar) % 360

        try:
            e_anom = self.solve_kepler(m, e)

            # True anomaly
            v = 2 * math.atan2(
                elem["sqrt_1_plus_e"] * math.sin(e_anom / 2),
                elem["sqrt_1_minus_e"] * math.cos(e_anom / 2),
            )

            # Distance
            r = a * (1 - e * math.cos(e_anom))

            w_plus_v = elem["w_rad"] + v
            cos_w_plus_v = math.cos(w_plus_v)
            sin_w_plus_v = math.sin(w_plus_v)

            # Heliocentric coordinates
            x_prime = r * (
                elem["cos_Omega"] * cos_w_plus_v
                - elem["sin_Omega"] * sin_w_plus_v * elem["cos_I"]
            )
            y_prime = r * (
                elem["sin_Omega"] * cos_w_plus_v
                + elem["cos_Omega"] * sin_w_plus_v * elem["cos_I"]
            )
            z_prime = r * (sin_w_plus_v * math.sin(elem["I_rad"]))

            return x_prime, y_prime, z_prime
        except Exception as err:
            logger.exception(
                "Error calculating heliocentric coordinates for %s", planet
            )
            raise RuntimeError(
                f"Error calculating helio coords for {planet}: {err}"
            )

    def calculate_moon_geocentric(
        self, days_since_epoch: Union[int, float]
    ) -> Tuple[float, float]:
        """
        Calculates geocentric ecliptic longitude for Moon and Rahu.

        Args:
            d (Union[int, float]): Days since epoch.

        Returns:
            Tuple[float, float]: Tuple of (moon_long, rahu_long) in degrees.
        """
        if not isinstance(days_since_epoch, (int, float)):
            logger.error("Days since epoch is not a number.")
            raise TypeError("Days since epoch must be a number.")

        logger.debug(
            "Calculating Moon geocentric coordinates at days=%s",
            days_since_epoch,
        )
        l_moon = (218.316 + 13.176396 * days_since_epoch) % 360
        m_moon = (l_moon - (83.3532 + 0.11140353 * days_since_epoch)) % 360

        try:
            e_anom = self.solve_kepler(m_moon, self.e_moon)
            v = 2 * math.atan2(
                self.sqrt_1_plus_e_moon * math.sin(e_anom / 2),
                self.sqrt_1_minus_e_moon * math.cos(e_anom / 2),
            )

            # Simplified distance in AU
            r_moon = 0.00257 * (1 - self.e_moon * math.cos(e_anom))

            # Longitude of ascending node (Rahu)
            omega_moon = (125.0445 - 0.05295376 * days_since_epoch) % 360
            omega_moon_rad = math.radians(omega_moon)
            cos_omega_moon = math.cos(omega_moon_rad)
            sin_omega_moon = math.sin(omega_moon_rad)

            w_moon = (
                math.radians((83.3532 + 0.11140353 * days_since_epoch) % 360)
                - omega_moon_rad
            )

            w_plus_v = w_moon + v
            cos_w_plus_v = math.cos(w_plus_v)
            sin_w_plus_v = math.sin(w_plus_v)

            x_m = r_moon * (
                cos_omega_moon * cos_w_plus_v
                - sin_omega_moon * sin_w_plus_v * self.cos_I_moon
            )
            y_m = r_moon * (
                sin_omega_moon * cos_w_plus_v
                + cos_omega_moon * sin_w_plus_v * self.cos_I_moon
            )

            lon = math.degrees(math.atan2(y_m, x_m)) % 360
            return lon, omega_moon
        except Exception as err:
            logger.exception("Error calculating Moon geocentric coordinates")
            raise RuntimeError(
                f"Error calculating Moon geocentric coordinates: {err}"
            )

    def get_lahiri_ayanamsa(self, jd: Union[int, float]) -> float:
        """
        Calculates a simplified Lahiri Ayanamsa offset.

        Args:
            jd (Union[int, float]): Julian Date.

        Returns:
            float: The Ayanamsa offset in degrees.
        """
        if not isinstance(jd, (int, float)):
            logger.error("Julian Date 'jd' is not a number.")
            raise TypeError("Julian Date 'jd' must be a number.")

        logger.debug("Calculating Lahiri Ayanamsa for JD=%s", jd)
        d = jd - self.epoch
        years = d / 365.25
        # Lahiri Ayanamsa was approximately 23.85 degrees at J2000
        # Progression is roughly 50.29 arcseconds per year
        return 23.85 + years * (50.29 / 3600.0)

    def calculate_raw_positions(
        self, jd: Union[int, float]
    ) -> Dict[str, float]:
        """
        Calculates raw (Sayana/tropical) geocentric longitudes for 9 grahas.

        Args:
            jd (Union[int, float]): Julian Date.

        Returns:
            Dict[str, float]: Dict mapping grahas to longitudes.
        """
        if not isinstance(jd, (int, float)):
            logger.error("Julian Date 'jd' is not a number.")
            raise TypeError("Julian Date 'jd' must be a number.")

        logger.info("Calculating raw positions for JD=%s", jd)
        try:
            d = jd - self.epoch
            ex, ey, _ = self.calculate_heliocentric("Earth", d)

            # Sun is opposite to Earth from geocentric perspective
            if ex == 0 and ey == 0:
                logger.error("Earth coordinates evaluate to zero.")
                raise ValueError("Earth coordinates evaluate to zero.")

            sx, sy = -ex, -ey
            sun_lon = math.degrees(math.atan2(sy, sx)) % 360

            positions = {"Sun": sun_lon}

            # Moon and Nodes (Rahu/Ketu)
            moon_lon, moon_node = self.calculate_moon_geocentric(d)
            positions["Moon"] = moon_lon
            positions["Rahu"] = moon_node
            positions["Ketu"] = (moon_node + 180) % 360

            # Other planets
            for planet in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
                px, py, _ = self.calculate_heliocentric(planet, d)
                # Geocentric coordinates
                gx = px - ex
                gy = py - ey

                if gx == 0 and gy == 0:
                    logger.error("Geocen coords for %s are zero.", planet)
                    raise ValueError(f"Geocen coords for {planet} are zero.")

                lon = math.degrees(math.atan2(gy, gx)) % 360
                positions[planet] = lon

            logger.info("Raw positions calculated successfully.")
            return positions
        except Exception as err:
            logger.exception("Error calculating raw positions for JD=%s", jd)
            raise RuntimeError(f"Error calculating raw positions: {err}")

    def calculate_nirayana_longitudes(
        self, jd: Union[int, float]
    ) -> Dict[str, float]:
        """
        Calculates Nirayana longitudes for 9 grahas.

        Args:
            jd (Union[int, float]): Julian Date.

        Returns:
            Dict[str, float]: Dict mapping grahas to Nirayana longitudes.
        """
        if not isinstance(jd, (int, float)):
            logger.error("Julian Date 'jd' is not a number.")
            raise TypeError("Julian Date 'jd' must be a number.")

        logger.info("Calculating nirayana longitudes for JD=%s", jd)
        try:
            raw = self.calculate_raw_positions(jd)
            ayanamsa = self.get_lahiri_ayanamsa(jd)

            # Using dictionary comprehension
            nirayana = {k: (v - ayanamsa) % 360 for k, v in raw.items()}
            logger.info("Nirayana longitudes calculated successfully.")
            return nirayana
        except Exception as err:
            logger.exception(
                "Error calculating nirayana longitudes for JD=%s", jd
            )
            raise RuntimeError(f"Error calculating nirayana longitudes: {err}")
