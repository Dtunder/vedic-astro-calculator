# vedic-astro-calculator

A basic planetary coordinate calculator in Python. It computes the coordinates using simplified Keplerian orbital elements for the 9 Vedic grahas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu). 

It features methods to calculate raw geocentric positions (Sayana/tropical longitudes) for a given Julian Date (JD) and also applies a simplified Lahiri Ayanamsa offset to return Nirayana (sidereal) longitudes.

## Usage

To run the demonstration:
```bash
python3 main.py
```

This will calculate the Sayana and Nirayana longitudes for the J2000 epoch (JD = 2451545.0).

## Testing

To run the unit tests:
```bash
python3 -m unittest test_calculator.py
```
