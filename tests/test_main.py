import unittest
import sys
import io
from unittest.mock import patch

# Adjust import path to find main.py from tests folder
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main

class TestMain(unittest.TestCase):
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main(self, mock_stdout):
        # Run main function
        main.main()
        
        # Capture the output
        output = mock_stdout.getvalue()
        
        # Verify specific keywords are in output to ensure correctness
        self.assertIn("Welcome to vedic-astro-calculator!", output)
        self.assertIn("Calculating planetary positions for Julian Date (JD): 2451545.0", output)
        self.assertIn("--- Sayana (Tropical) Longitudes ---", output)
        self.assertIn("--- Nirayana (Sidereal) Longitudes ---", output)
        
        # Verify planets are in output
        planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
        for planet in planets:
            self.assertIn(planet, output)
            
        self.assertIn("Lahiri Ayanamsa:", output)

if __name__ == '__main__':
    unittest.main()
