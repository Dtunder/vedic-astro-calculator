import math

class VedicAstroCalculator:
    def __init__(self):
        # J2000 epoch
        self.epoch = 2451545.0
        
        # Simplified Keplerian elements (J2000)
        # a: semi-major axis (AU)
        # e: eccentricity
        # I: inclination (deg)
        # L: mean longitude (deg)
        # omega_bar: longitude of perihelion (deg)
        # Omega: longitude of ascending node (deg)
        # n: daily motion (deg/day)
        self.elements = {
            'Earth': { 'a': 1.000000, 'e': 0.016710, 'I': 0.00005, 'L': 100.46435, 'omega_bar': 102.9404, 'Omega': 0.0, 'n': 0.9856091 },
            'Mercury': { 'a': 0.387099, 'e': 0.205630, 'I': 7.005, 'L': 252.25032, 'omega_bar': 77.45779, 'Omega': 48.33076, 'n': 4.0923344 },
            'Venus': { 'a': 0.723332, 'e': 0.006773, 'I': 3.3946, 'L': 181.97909, 'omega_bar': 131.5637, 'Omega': 76.67984, 'n': 1.6021302 },
            'Mars': { 'a': 1.523679, 'e': 0.093400, 'I': 1.8497, 'L': 355.43327, 'omega_bar': 336.0602, 'Omega': 49.5581, 'n': 0.5240207 },
            'Jupiter': { 'a': 5.202603, 'e': 0.048498, 'I': 1.303, 'L': 34.35148, 'omega_bar': 14.3313, 'Omega': 100.4643, 'n': 0.0830853 },
            'Saturn': { 'a': 9.554909, 'e': 0.055546, 'I': 2.488, 'L': 50.07747, 'omega_bar': 93.0567, 'Omega': 113.6634, 'n': 0.0334442 },
        }

    def solve_kepler(self, M, e):
        """Solves Kepler's equation M = E - e*sin(E) using Newton's method."""
        if not isinstance(M, (int, float)) or not isinstance(e, (int, float)):
            raise TypeError("M and e must be numbers.")
        if not (0 <= e < 1):
            raise ValueError("Eccentricity e must be in the range [0, 1).")
            
        M_rad = math.radians(M)
        E = M_rad
        for _ in range(10):
            try:
                denominator = 1 - e * math.cos(E)
                if denominator == 0:
                    raise ZeroDivisionError("Denominator in Newton's method became zero.")
                delta_E = (E - e * math.sin(E) - M_rad) / denominator
            except ZeroDivisionError as err:
                raise ValueError(f"Failed to solve Kepler's equation: {err}")
                
            E -= delta_E
            if abs(delta_E) < 1e-6:
                break
        return E

    def calculate_heliocentric(self, planet, d):
        """Calculates heliocentric ecliptic coordinates for a given planet and days since epoch (d)."""
        if not isinstance(planet, str):
            raise TypeError("Planet name must be a string.")
        if planet not in self.elements:
            raise ValueError(f"Planet '{planet}' not found in elements. Supported planets: {list(self.elements.keys())}")
        if not isinstance(d, (int, float)):
            raise TypeError("Days since epoch 'd' must be a number.")
            
        elem = self.elements[planet]
        a = elem['a']
        e = elem['e']
        I = math.radians(elem['I'])
        L = elem['L'] + elem['n'] * d
        omega_bar = elem['omega_bar']
        Omega = math.radians(elem['Omega'])

        M = (L - omega_bar) % 360
        w = math.radians(omega_bar) - Omega

        try:
            E = self.solve_kepler(M, e)
            
            # True anomaly
            v = 2 * math.atan2(math.sqrt(1 + e) * math.sin(E / 2), math.sqrt(1 - e) * math.cos(E / 2))
            
            # Distance
            r = a * (1 - e * math.cos(E))
            
            # Heliocentric coordinates
            x_prime = r * (math.cos(Omega) * math.cos(w + v) - math.sin(Omega) * math.sin(w + v) * math.cos(I))
            y_prime = r * (math.sin(Omega) * math.cos(w + v) + math.cos(Omega) * math.sin(w + v) * math.cos(I))
            z_prime = r * (math.sin(w + v) * math.sin(I))
            
            return x_prime, y_prime, z_prime
        except Exception as err:
            raise RuntimeError(f"Error calculating heliocentric coordinates for {planet}: {err}")

    def calculate_moon_geocentric(self, d):
        """Calculates geocentric ecliptic longitude for Moon, Rahu (North Node) based on simple elements."""
        if not isinstance(d, (int, float)):
            raise TypeError("Days since epoch 'd' must be a number.")
            
        L_moon = (218.316 + 13.176396 * d) % 360
        M_moon = (L_moon - (83.3532 + 0.11140353 * d)) % 360
        e_moon = 0.0549
        
        try:
            E = self.solve_kepler(M_moon, e_moon)
            v = 2 * math.atan2(math.sqrt(1 + e_moon) * math.sin(E / 2), math.sqrt(1 - e_moon) * math.cos(E / 2))
            
            # Simplified distance in AU
            r_moon = 0.00257 * (1 - e_moon * math.cos(E))
            
            # Longitude of ascending node (Rahu)
            Omega_moon = (125.0445 - 0.05295376 * d) % 360
            w_moon = math.radians((83.3532 + 0.11140353 * d) % 360) - math.radians(Omega_moon)
            I_moon = math.radians(5.145)
            
            x_m = r_moon * (math.cos(math.radians(Omega_moon)) * math.cos(w_moon + v) - math.sin(math.radians(Omega_moon)) * math.sin(w_moon + v) * math.cos(I_moon))
            y_m = r_moon * (math.sin(math.radians(Omega_moon)) * math.cos(w_moon + v) + math.cos(math.radians(Omega_moon)) * math.sin(w_moon + v) * math.cos(I_moon))
            
            lon = math.degrees(math.atan2(y_m, x_m)) % 360
            return lon, Omega_moon
        except Exception as err:
            raise RuntimeError(f"Error calculating Moon geocentric coordinates: {err}")

    def get_lahiri_ayanamsa(self, jd):
        """Calculates a simplified Lahiri Ayanamsa offset."""
        if not isinstance(jd, (int, float)):
            raise TypeError("Julian Date 'jd' must be a number.")
            
        d = jd - self.epoch
        years = d / 365.25
        # Lahiri Ayanamsa was approximately 23.85 degrees at J2000
        # Progression is roughly 50.29 arcseconds per year
        return 23.85 + years * (50.29 / 3600.0)

    def calculate_raw_positions(self, jd):
        """Calculates raw (Sayana/tropical) geocentric longitudes for 9 grahas."""
        if not isinstance(jd, (int, float)):
            raise TypeError("Julian Date 'jd' must be a number.")
            
        try:
            d = jd - self.epoch
            ex, ey, ez = self.calculate_heliocentric('Earth', d)
            
            # Sun is opposite to Earth from geocentric perspective
            if ex == 0 and ey == 0:
                raise ValueError("Earth coordinates (ex, ey) evaluate to zero; cannot calculate Sun longitude.")
                
            sx, sy = -ex, -ey
            sun_lon = math.degrees(math.atan2(sy, sx)) % 360
            
            positions = {'Sun': sun_lon}
            
            # Moon and Nodes (Rahu/Ketu)
            moon_lon, moon_node = self.calculate_moon_geocentric(d)
            positions['Moon'] = moon_lon
            positions['Rahu'] = moon_node
            positions['Ketu'] = (moon_node + 180) % 360
            
            # Other planets
            for planet in ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
                px, py, pz = self.calculate_heliocentric(planet, d)
                # Geocentric coordinates
                gx = px - ex
                gy = py - ey
                
                if gx == 0 and gy == 0:
                    raise ValueError(f"Geocentric coordinates for {planet} evaluate to zero.")
                    
                lon = math.degrees(math.atan2(gy, gx)) % 360
                positions[planet] = lon
                
            return positions
        except Exception as err:
            raise RuntimeError(f"Error calculating raw positions: {err}")

    def calculate_nirayana_longitudes(self, jd):
        """Calculates Nirayana (sidereal) longitudes for 9 grahas by subtracting Ayanamsa."""
        if not isinstance(jd, (int, float)):
            raise TypeError("Julian Date 'jd' must be a number.")
            
        try:
            raw = self.calculate_raw_positions(jd)
            ayanamsa = self.get_lahiri_ayanamsa(jd)
            
            nirayana = {}
            for k, v in raw.items():
                nirayana[k] = (v - ayanamsa) % 360
                
            return nirayana
        except Exception as err:
            raise RuntimeError(f"Error calculating nirayana longitudes: {err}")
