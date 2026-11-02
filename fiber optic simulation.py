#!/usr/bin/env python3
"""fiber_optics.py"""

import math

def simulate_fiber(n_core: float, n_cladding: float, n_medium: float, test_angles: list):
    """Simulate optical fiber and test light ray guidance"""
    print(f"\n{'='*45}")
    print(f"          OPTICAL FIBER SIMULATION ")
    print(f"{'='*45}")
    print(f" Core index:      {n_core}")
    print(f" Cladding index:  {n_cladding}")
    print(f" Medium index:    {n_medium}")
    print(f"{'-'*45}")
    
    # validity check for total internal reflection
    if n_cladding >= n_core:
        print("Error: Core index must be greater than cladding.\n")
        return False
        
    # calculate critical angle
    crit_deg = math.degrees(math.asin(n_cladding / n_core))
    
    # calculate numerical aperture
    na = math.sqrt(n_core**2 - n_cladding**2)
    
    # calculate maximum acceptance angle
    if na > n_medium:
        accept_deg = 90.0
    else:
        accept_deg = math.degrees(math.asin(na / n_medium))
        
    print(f"\n Calculated Critical Angle:     {crit_deg:.2f}°")
    print(f" Calculated Numerical Aperture: {na:.4f}")
    print(f" Calculated Acceptance Angle:   {accept_deg:.2f}°\n")
    
    print(" RAY TRACING RESULTS")
    print(f"{'-'*45}")
    
    # loop through incident test angles
    for angle in test_angles:
        
        # check if incident angle is within acceptance cone
        if angle <= accept_deg:
            print(f" Angle {angle:05.2f}° ->  GUIDED (TIR Achieved)")
            
        # incident angle is too steep
        else:
            print(f" Angle {angle:05.2f}° ->  LOST   (Refracted out)")
            
    print(f"{'='*45}\n")
    
    return True

def main() -> None:
    # standard step-index fiber parameters
    test_angles = [5.0, 10.0, 14.0, 15.0, 20.0]
    
    print("Testing standard fiber optics...")
    simulate_fiber(1.48, 1.46, 1.0, test_angles)
    
    print("Testing high-density difference fiber optics...")
    simulate_fiber(1.50, 1.40, 1.0, test_angles)

if __name__ == "__main__":
    main()