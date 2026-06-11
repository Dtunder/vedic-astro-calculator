# vedic-astro-calculator

A basic planetary coordinate calculator in Python. It computes the coordinates using simplified Keplerian orbital elements for the 9 Vedic grahas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu). 

It features methods to calculate raw geocentric positions (Sayana/tropical longitudes) for a given Julian Date (JD) and also applies a simplified Lahiri Ayanamsa offset to return Nirayana (sidereal) longitudes.

## Usage

To run the demonstration from the CLI:

```bash
python3 main.py
```

This will output structured JSON logs to standard output and calculate the Sayana and Nirayana longitudes for the J2000 epoch (JD = 2451545.0).

## Configuration

The application natively outputs structured JSON logs. This is configured in `main.py` via the `setup_logging` function and a custom `JsonFormatter` class.

By default, logs include:
- The time of log creation
- The log level
- The logger name
- The log message
- Any exception traceback information

The `setup_logging` function configures the root logger, setting the level to `INFO`.

## API Reference

The primary class for using the calculator programmatically is the `VedicAstroCalculator` class located in `calculator.py`.

### `VedicAstroCalculator`

Initializes and precomputes J2000 epoch elements.

#### Methods

- **`calculate_raw_positions(self, jd: Union[int, float]) -> Dict[str, float]`**
  - **Description**: Calculates raw (Sayana/tropical) geocentric longitudes for 9 grahas.
  - **Args**: `jd` - The Julian Date as a number.
  - **Returns**: A dictionary mapping graha names to their geocentric longitudes in degrees.

- **`calculate_nirayana_longitudes(self, jd: Union[int, float]) -> Dict[str, float]`**
  - **Description**: Calculates Nirayana (sidereal) longitudes for 9 grahas by subtracting the Ayanamsa.
  - **Args**: `jd` - The Julian Date as a number.
  - **Returns**: A dictionary mapping graha names to their Nirayana longitudes in degrees.

- **`get_lahiri_ayanamsa(self, jd: Union[int, float]) -> float`**
  - **Description**: Calculates a simplified Lahiri Ayanamsa offset.
  - **Args**: `jd` - The Julian Date as a number.
  - **Returns**: The Ayanamsa offset in degrees.

- **`calculate_heliocentric(self, planet: str, d: Union[int, float]) -> Tuple[float, float, float]`**
  - **Description**: Calculates heliocentric ecliptic coordinates for a given planet and days since epoch (`d`).
  - **Args**:
    - `planet` - Name of the planet (e.g., 'Mars').
    - `d` - Days since the epoch.
  - **Returns**: A tuple of `(x, y, z)` coordinates in AU.

- **`calculate_moon_geocentric(self, d: Union[int, float]) -> Tuple[float, float]`**
  - **Description**: Calculates geocentric ecliptic longitude for the Moon and Rahu (North Node) based on simple elements.
  - **Args**: `d` - Days since the epoch.
  - **Returns**: A tuple containing `(moon_longitude, rahu_longitude)` in degrees.

- **`solve_kepler(self, M: Union[int, float], e: Union[int, float]) -> float`**
  - **Description**: Solves Kepler's equation `M = E - e*sin(E)` using Newton's method.
  - **Args**:
    - `M` - Mean anomaly in degrees.
    - `e` - Eccentricity (must be in the range `[0, 1)`).
  - **Returns**: Eccentric anomaly in radians.

## Testing

To run the unit tests:
```bash
python3 -m unittest discover tests
```