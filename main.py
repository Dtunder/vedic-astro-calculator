from calculator import VedicAstroCalculator

def main():
    print("Welcome to vedic-astro-calculator!")
    
    # J2000 epoch as an example JD
    jd = 2451545.0
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

if __name__ == "__main__":
    main()
