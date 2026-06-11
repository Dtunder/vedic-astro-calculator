import unittest
import sys
import os

# Adjust import path to find calculator.py from tests folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculator import VedicAstroCalculator

class TestVedicAstroCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = VedicAstroCalculator()
        self.jd = 2451545.0 # J2000 Epoch

    def test_calculate_raw_positions(self):
        raw = self.calc.calculate_raw_positions(self.jd)
        
        # Check all 9 grahas are present
        grahas = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
        for graha in grahas:
            self.assertIn(graha, raw)
            self.assertIsInstance(raw[graha], float)
            self.assertTrue(0 <= raw[graha] < 360)

        # Rahu and Ketu should be 180 degrees apart
        diff = abs(raw['Rahu'] - raw['Ketu'])
        self.assertAlmostEqual(diff, 180.0, places=5)

    def test_get_lahiri_ayanamsa(self):
        ayanamsa = self.calc.get_lahiri_ayanamsa(self.jd)
        # At J2000, Lahiri Ayanamsa should be around 23.85
        self.assertAlmostEqual(ayanamsa, 23.85, places=2)

    def test_calculate_nirayana_longitudes(self):
        raw = self.calc.calculate_raw_positions(self.jd)
        nirayana = self.calc.calculate_nirayana_longitudes(self.jd)
        ayanamsa = self.calc.get_lahiri_ayanamsa(self.jd)
        
        for k in raw:
            expected = (raw[k] - ayanamsa) % 360
            self.assertAlmostEqual(nirayana[k], expected, places=5)

    def test_solve_kepler_validation(self):
        # TypeError for non-numbers
        with self.assertRaises(TypeError):
            self.calc.solve_kepler("M", 0.1)
        with self.assertRaises(TypeError):
            self.calc.solve_kepler(100, "e")
            
        # ValueError for out of bounds eccentricity
        with self.assertRaises(ValueError):
            self.calc.solve_kepler(100, -0.1)
        with self.assertRaises(ValueError):
            self.calc.solve_kepler(100, 1.0)
            
    def test_calculate_heliocentric_validation(self):
        # TypeError for wrong types
        with self.assertRaises(TypeError):
            self.calc.calculate_heliocentric(123, self.jd)
        with self.assertRaises(TypeError):
            self.calc.calculate_heliocentric("Earth", "d")
            
        # ValueError for unknown planet
        with self.assertRaises(ValueError):
            self.calc.calculate_heliocentric("Pluto", self.jd)

    def test_jd_validation(self):
        # Test methods taking jd/d raise TypeError for non-numbers
        with self.assertRaises(TypeError):
            self.calc.calculate_moon_geocentric("d")
        with self.assertRaises(TypeError):
            self.calc.get_lahiri_ayanamsa("jd")
        with self.assertRaises(TypeError):
            self.calc.calculate_raw_positions("jd")
        with self.assertRaises(TypeError):
            self.calc.calculate_nirayana_longitudes("jd")

if __name__ == '__main__':
    unittest.main()
