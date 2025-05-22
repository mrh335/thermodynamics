# -*- coding: utf-8 -*-
"""
Created on Thu May 22 08:50:53 2025

@author: markh
"""

import numpy as np
import matplotlib.pyplot as plt
from CoolProp.HumidAirProp import HAPropsSI
from CoolProp.CoolProp import PropsSI


def altitude_to_pressure(altitude_m):
    """Convert altitude in meters to atmospheric pressure in Pa using barometric formula."""
    P0 = 101325  # sea level standard atmospheric pressure, Pa
    T0 = 288.15  # standard temperature, K
    g = 9.80665  # gravity, m/s^2
    L = 0.0065   # temperature lapse rate, K/m
    R = 287.05   # specific gas constant for dry air, J/(kg·K)

    return P0 * (1 - L * altitude_m / T0) ** (g / (R * L))


def generate_psychrometric_chart(altitude_m=0.0, T_min=0.0, T_max=50.0, RH_steps=10):
    """
    Generate and plot a psychrometric chart for a given altitude.

    :param altitude_m: Altitude in meters
    :param T_min: Minimum dry bulb temperature in °C
    :param T_max: Maximum dry bulb temperature in °C
    :param RH_steps: Number of RH lines (e.g. 10 for 10%, 20%...100%)
    """

    P = altitude_to_pressure(altitude_m)
    Tdb_range = np.linspace(T_min, T_max, 100) + 273.15  # K
    RH_range = np.linspace(0.1, 1.0, RH_steps)

    plt.figure(figsize=(12, 8))

    # Plot RH lines
    for RH in RH_range:
        dewpoints_C = [HAPropsSI("Tdp", "T", T, "P", P, "RH", RH) - 273.15 for T in Tdb_range]
        plt.plot(Tdb_range - 273.15, dewpoints_C, label=f"{int(RH*100)}% RH", linestyle='--')

    # Saturation curve
    dewpoints_saturation = [HAPropsSI("Tdp", "T", T, "P", P, "RH", 1.0) - 273.15 for T in Tdb_range]
    plt.plot(Tdb_range - 273.15, dewpoints_saturation, label="100% RH", color='blue', linewidth=2)

    # Enthalpy lines
    h_lines = np.linspace(20e3, 100e3, 6)  # J/kg
    for h in h_lines:
        T_line = []
        dew_line = []
        for T in Tdb_range:
            try:
                RH = HAPropsSI("RH", "T", T, "P", P, "H", h)
                dew = HAPropsSI("Tdp", "T", T, "P", P, "RH", RH) - 273.15
                T_line.append(T - 273.15)
                dew_line.append(dew)
            except:
                continue
        if T_line:
            plt.plot(T_line, dew_line, label=f"h={h/1000:.0f} kJ/kg", linestyle=':')

    # Wet bulb lines
    wb_lines = np.linspace(10, 30, 5)  # example values in deg C
    for wb in wb_lines:
        T_line = []
        dew_line = []
        for T in Tdb_range:
            try:
                RH = HAPropsSI("RH", "T", T, "P", P, "Twb", wb + 273.15)
                if 0 <= RH <= 1:
                    dew = HAPropsSI("Tdp", "T", T, "P", P, "RH", RH) - 273.15
                    T_line.append(T - 273.15)
                    dew_line.append(dew)
            except:
                continue
        if T_line:
            plt.plot(T_line, dew_line, label=f"Twb={wb}°C", linestyle='-.')

    # Constant density lines
    rho_lines = np.linspace(0.8, 1.3, 6)  # kg/m^3
    for rho in rho_lines:
        T_line = []
        dew_line = []
        for T in Tdb_range:
            try:
                RH = HAPropsSI("RH", "T", T, "P", P, "Rho", rho)
                if 0 <= RH <= 1:
                    dew = HAPropsSI("Tdp", "T", T, "P", P, "RH", RH) - 273.15
                    T_line.append(T - 273.15)
                    dew_line.append(dew)
            except:
                continue
        if T_line:
            plt.plot(T_line, dew_line, label=f"Density={rho:.2f} kg/m3", linestyle='--')

    # Labels and title
    plt.title(f"Psychrometric Chart (Y: Dew Point) at Altitude {altitude_m} m")
    plt.xlabel("Dry Bulb Temperature [°C]")
    plt.ylabel("Dew Point Temperature [°C]")
    plt.grid(True, which='both', linestyle=':', linewidth=0.5)
    plt.legend(loc='best', frameon=True)
    plt.tight_layout()
    plt.show()


# Example use
if __name__ == "__main__":
    generate_psychrometric_chart(altitude_m=0)  # Sea level by default
