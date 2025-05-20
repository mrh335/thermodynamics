import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

def plot_ph_basic():

    # Set refrigerant
    refrigerant = 'R134a'

    # Get fluid-specific properties
    T_min = PropsSI('Tmin', refrigerant)
    T_crit = PropsSI('Tcrit', refrigerant)
    T_max = T_crit - 0.1
    P_crit = PropsSI('Pcrit', refrigerant)
    p_max = P_crit * 1.5

    # Enthalpy range for plotting
    #T_hmin = T_min + 5
    h_sat_liq = PropsSI('H', 'T', 253.15, 'Q', 0, refrigerant)  # -20C in K
    h_min = h_sat_liq * 0.75  # 25% less than saturation liquid enthalpy at -20C

    # Determine h_max from saturated vapor line
    T_range_low = np.linspace(T_min, T_crit - 5, 200)
    T_range_high = np.linspace(T_crit - 5, T_crit - 0.01, 300)
    T_range = np.concatenate((T_range_low, T_range_high))
    h_q1 = []
    for T in T_range:
        try:
            hq = PropsSI('H', 'T', T, 'Q', 1, refrigerant)
            h_q1.append(hq)
        except:
            continue
    h_max = max(h_q1) * 1.2  # add 20% buffer
    h_range = np.linspace(h_min, h_max, 1000)

    # Pressure bounds for plotting
    p_min = 0

    # Prepare plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Determine maximum temperature for isotherms from max enthalpy and pressure
    h_plot_max = max(h_range)
    try:
        T_max_calc = PropsSI('T', 'P', p_max, 'H', h_plot_max, refrigerant)
        if np.isnan(T_max_calc):
            T_max_calc = T_crit - 0.1
    except:
        T_max_calc = T_crit - 0.1

    # Plot isotherms
    temperatures = np.linspace(T_min, T_max_calc, 30)
    pressures = np.logspace(np.log10(1e4), np.log10(p_max), 400)
    for T in temperatures:
        h_vals = []
        p_vals = []
        for P in pressures:
            try:
                h = PropsSI('H', 'T', T, 'P', P, refrigerant)
                if not np.isnan(h):
                    h_vals.append(h / 1000)
                    p_vals.append(P / 100000)
            except:
                continue
        if h_vals:
            ax.plot(h_vals, p_vals, color='red', lw=0.5)

    # Plot lines of constant quality
    qualities = np.linspace(0, 1, 11)
    for Q in qualities:
        h_sat = []
        p_sat = []
        T_range_low = np.linspace(T_min, T_crit - 5, 200)
        T_range_high = np.linspace(T_crit - 5, T_crit - 0.01, 300)
        T_range = np.concatenate((T_range_low, T_range_high))
        for T in T_range:
            try:
                p = PropsSI('P', 'T', T, 'Q', Q, refrigerant)
                hq = PropsSI('H', 'T', T, 'Q', Q, refrigerant)
                h_sat.append(hq / 1000)
                p_sat.append(p / 100000)
            except:
                continue
        if Q == 0 or Q == 1:
            ax.plot(h_sat, p_sat, color='black', lw=1.5)
        else:
            ax.plot(h_sat, p_sat, color='lightgray', lw=0.5)

    # Plot isochors
    rho_min = PropsSI('D', 'T', T_min + 1, 'Q', 1, refrigerant)
    rho_max = PropsSI('D', 'T', T_crit - 1, 'Q', 0, refrigerant)
    densities = np.geomspace(rho_min * 2, rho_max, 20)
    for rho in densities:
        h_vals = []
        p_vals = []
        for P in pressures:
            try:
                h = PropsSI('H', 'D', rho, 'P', P, refrigerant)
                if not np.isnan(h):
                    h_vals.append(h / 1000)
                    p_vals.append(P / 100000)
            except:
                continue
        if h_vals:
            ax.plot(h_vals, p_vals, 'green', lw=0.5)

    # Plot isentropes
    s_min = PropsSI('S', 'T', T_min + 1, 'Q', 0, refrigerant) / 1000
    s_max = PropsSI('S', 'P', p_max, 'H', h_plot_max * 1.1, refrigerant) / 1000
    entropies = np.linspace(s_min, s_max, 30)
    for s in entropies:
        h_vals = []
        p_vals = []
        for P in pressures:
            try:
                h = PropsSI('H', 'S', s * 1000, 'P', P, refrigerant)
                if not np.isnan(h):
                    h_vals.append(h / 1000)
                    p_vals.append(P / 100000)
            except:
                continue
        if h_vals:
            ax.plot(h_vals, p_vals, 'blue', lw=0.5)

    # === Refrigeration Cycle with Suction Line Heat Exchanger ===
    T_evap = 273.15  # 0°C in Kelvin
    T_cond = min(318.15, T_crit - 0.5)  # 45°C in Kelvin
    superheat = 5
    subcool = 5

    # Point 1: After SLHX (superheated)
    P1 = PropsSI('P', 'T', T_evap, 'Q', 1, refrigerant)
    T1 = T_evap + superheat
    h1 = PropsSI('H', 'T', T1, 'P', P1, refrigerant)
    s1 = PropsSI('S', 'T', T1, 'P', P1, refrigerant)

    # Point 2: After compressor
    is_transcritical = T_cond >= T_crit or P1 > P_crit
    if is_transcritical:
        if refrigerant.lower() == 'co2':
            P2 = 120e5  # 120 bar in Pa for CO2
        else:
            P2 = P_crit * 1.3
    else:
        P2 = PropsSI('P', 'T', T_cond, 'Q', 0, refrigerant)
    try:
        h2 = PropsSI('H', 'P', P2, 'S', s1, refrigerant)
    except Exception as e:
        print(f"Error computing h2 at P2={P2}, s1={s1}: {e}")
        h2 = h1

    # Point 3: After condenser (before SLHX)
    T3 = T_cond - subcool
    h3_base = PropsSI('H', 'T', T3, 'P', P2, refrigerant)

    # SLHX effectiveness calculation
    slhx_effectiveness = 0.6
    if is_transcritical:
        T5_in = T_evap + superheat
        T3_in = T3
        cp_vapor = PropsSI('C', 'T', T5_in, 'P', P1, refrigerant)
        cp_liquid = PropsSI('C', 'T', T3_in, 'P', P2, refrigerant)
        delta_T1 = T3_in - T5_in
        q_max = min(cp_vapor, cp_liquid) * delta_T1
        q_slhx = slhx_effectiveness * q_max
        h3 = h3_base - q_slhx
        h5 = h1 - q_slhx
    else:
        x5 = 0.2
        h5 = PropsSI('H', 'P', P1, 'Q', x5, refrigerant)
        q_max = h3_base - h5
        q_slhx = slhx_effectiveness * q_max
        h3 = h3_base - q_slhx

    # Point 4: Expansion valve (isenthalpic)
    h4 = h3
    P4 = P1

    # Cycle sequence
    cycle_h = [h1, h2, h3, h4, h5, h1]
    cycle_p = [P1, P2, P2, P1, P1, P1]

    # Plot cycle
    cycle_h_plot = [val / 1000 for val in cycle_h]
    cycle_p_plot = [val / 100000 for val in cycle_p]
    ax.plot(cycle_h_plot, cycle_p_plot, 'ko-', lw=2, label='Cycle with SLHX')
    ax.legend()

    # Final formatting
    ax.set_xlabel('Enthalpy [kJ/kg]')
    ax.set_ylabel('Pressure [bar]')
    ax.set_ylim(bottom=0, top=p_max / 100000)
    ax.set_xlim(left=h_min / 1000, right=h_max / 1000)
    ax.set_title(f'Pressure-Enthalpy Diagram for {refrigerant.upper()} with SLHX')
    ax.grid(True, which='both', ls='--', lw=0.5)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_ph_basic()