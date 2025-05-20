import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI
import CoolProp.CoolProp as CP

def plot_ph_v3():
    # -*- coding: utf-8 -*-
    """
    Created on Thu Apr  3 21:52:23 2025

    @author: markh
    """

    # -*- coding: utf-8 -*-
    """
    Created on Wed Apr  2 17:15:12 2025

    @author: markh
    """



    def calculate_slhx_state_points(refrigerant='R134a', effectiveness=0.6, T_evap_C=0, T_cond_C=45, superheat=5, subcool=5, use_slhx=True, use_two_phase_evap_exit=False, high_side_pressure_bar=None):
        T_evap = 273.15 + T_evap_C
        T_cond = 273.15 + T_cond_C

        # Pressures
        P_evap = CP.PropsSI('P', 'T', T_evap, 'Q', 1, refrigerant)

        if refrigerant.lower() == 'co2':
            if high_side_pressure_bar is None:
                high_side_pressure_bar = 120.0  # default to 120 bar
            P_cond = high_side_pressure_bar * 1e5  # convert to Pa
        else:
            P_cond = CP.PropsSI('P', 'T', T_cond, 'Q', 0, refrigerant)

        # State 6: Evap outlet (before SLHX)
        if use_two_phase_evap_exit:
            x6 = 0.95
            h6 = CP.PropsSI('H', 'P', P_evap, 'Q', x6, refrigerant)
            T6 = CP.PropsSI('T', 'P', P_evap, 'Q', x6, refrigerant)
            s6 = CP.PropsSI('S', 'P', P_evap, 'Q', x6, refrigerant)
        else:
            T6 = T_evap + superheat
            h6 = CP.PropsSI('H', 'T', T6, 'P', P_evap, refrigerant)
            s6 = CP.PropsSI('S', 'T', T6, 'P', P_evap, refrigerant)

        # State 3: Condenser outlet (before SLHX)
        T3 = T_cond - subcool
        h3 = CP.PropsSI('H', 'T', T3, 'P', P_cond, refrigerant)
        s3 = CP.PropsSI('S', 'T', T3, 'P', P_cond, refrigerant)

        if use_slhx:
            # Method 1: Cool high-side liquid to suction temp
            h3_cooled_to_T6 = CP.PropsSI('H', 'T', T6, 'P', P_cond, refrigerant)
            q_max_method1 = h3 - h3_cooled_to_T6

            # Method 2: Heat suction vapor to condenser temp
            h6_heated_to_T3 = CP.PropsSI('H', 'T', T3, 'P', P_evap, refrigerant)
            q_max_method2 = h6_heated_to_T3 - h6

            # Use the minimum of method 1 and method 2 for q_max
            q_max = min(q_max_method1, q_max_method2)

            print("Comparison of q_max methods:")
            print(f"q_max (method 1 - liquid to suction temp): {q_max_method1 / 1000:.3f} kJ/kg")
            print(f"q_max (method 2 - vapor to condenser temp): {q_max_method2 / 1000:.3f} kJ/kg")

            q_actual = effectiveness * q_max

            # State 1: Suction (after SLHX)
            h1 = h6 + q_actual
            T1 = CP.PropsSI('T', 'P', P_evap, 'H', h1, refrigerant)
            s1 = CP.PropsSI('S', 'P', P_evap, 'H', h1, refrigerant)

            # State 4: SLHX outlet (after subcooling)
            h4 = h3 - q_actual
            T4 = CP.PropsSI('T', 'P', P_cond, 'H', h4, refrigerant)
            s4 = CP.PropsSI('S', 'P', P_cond, 'H', h4, refrigerant)
        else:
            # State 1: Suction (no SLHX)
            h1 = h6
            T1 = T6
            s1 = s6

            # State 4: Condenser outlet (no SLHX)
            h4 = h3
            T4 = T3
            s4 = s3

        # State 5: Evaporator inlet (after expansion valve)
        h5 = h4  # isenthalpic expansion
        T5 = CP.PropsSI('T', 'P', P_evap, 'H', h5, refrigerant)
        s5 = CP.PropsSI('S', 'P', P_evap, 'H', h5, refrigerant)

        # State 2: Discharge (isentropic compression from suction to cond pressure)
        s2 = s1
        h2 = CP.PropsSI('H', 'P', P_cond, 'S', s2, refrigerant)
        T2 = CP.PropsSI('T', 'P', P_cond, 'H', h2, refrigerant)

        states = {
            1: {'P': P_evap, 'T': T1, 'H': h1, 'S': s1},
            2: {'P': P_cond, 'T': T2, 'H': h2, 'S': s2},
            3: {'P': P_cond, 'T': T3, 'H': h3, 'S': s3},
            4: {'P': P_cond, 'T': T4, 'H': h4, 'S': s4},
            5: {'P': P_evap, 'T': T5, 'H': h5, 'S': s5},
            6: {'P': P_evap, 'T': T6, 'H': h6, 'S': s6}
        }

        for i in range(1, 7):
            state = states[i]
            print(f"State {i}: P = {state['P'] / 1e5:.2f} bar, T = {state['T'] - 273.15:.2f} °C, H = {state['H'] / 1000:.2f} kJ/kg, S = {state['S'] / 1000:.4f} kJ/kg·K")

        return states


    def plot_ph_diagram_with_cycle(refrigerant, use_slhx, use_two_phase_evap_exit):
        T_min = PropsSI('Tmin', refrigerant)
        T_crit = PropsSI('Tcrit', refrigerant)
        P_crit = PropsSI('Pcrit', refrigerant)
        p_max = P_crit * 2

        h_sat_liq = PropsSI('H', 'T', 253.15, 'Q', 0, refrigerant)
        h_min = h_sat_liq * 0.75

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
        h_max = max(h_q1) * 1.2
        h_range = np.linspace(h_min, h_max, 1000)

        T_triple = PropsSI('Ttriple', refrigerant)
        p_min = PropsSI('P', 'T', T_triple, 'Q', 0, refrigerant)
        print(f"Minimum pressure is {p_min}")

        fig, ax = plt.subplots(figsize=(10, 6))

        h_plot_max = max(h_range)
        try:
            T_max_calc = PropsSI('T', 'P', p_max, 'H', h_plot_max, refrigerant)
            if np.isnan(T_max_calc):
                T_max_calc = T_crit - 0.1
        except:
            T_max_calc = T_crit - 0.1

        temperatures = np.linspace(T_min, T_max_calc, 30)
        pressures = np.logspace(np.log10(p_min), np.log10(p_max), 400)
        for T in temperatures:
            h_vals, p_vals = [], []
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

        qualities = np.linspace(0, 1, 11)
        for Q in qualities:
            h_sat, p_sat = [], []
            T_range_low = np.linspace(T_min, T_crit - 5, 200)
            T_range_high = np.linspace(T_crit - 5, T_crit - 0.00001, 300)
            T_range = np.concatenate((T_range_low, T_range_high))
            for T in T_range:
                try:
                    p = PropsSI('P', 'T', T, 'Q', Q, refrigerant)
                    hq = PropsSI('H', 'T', T, 'Q', Q, refrigerant)
                    h_sat.append(hq / 1000)
                    p_sat.append(p / 100000)
                except:
                    continue
            ax.plot(h_sat, p_sat, color='black' if Q in [0, 1] else 'lightgray', lw=1.5 if Q in [0, 1] else 0.5)

        rho_min = PropsSI('D', 'T', T_min + 1, 'Q', 1, refrigerant)
        rho_max = PropsSI('D', 'T', T_crit - 1, 'Q', 0, refrigerant)
        densities = np.geomspace(rho_min * 2, rho_max, 20)
        for rho in densities:
            h_vals, p_vals = [], []
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

        s_min = PropsSI('S', 'T', T_min + 1, 'Q', 0, refrigerant) / 1000
        s_max = PropsSI('S', 'P', p_max, 'H', h_plot_max * 1.1, refrigerant) / 1000
        entropies = np.linspace(s_min, s_max, 30)
        for s in entropies:
            h_vals, p_vals = [], []
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
        return ax, p_min, p_max, h_min, h_max


    def overlay_cycle_on_ax(ax, data_with_slhx, refrigerant, use_slhx, p_min, p_max, h_min, h_max):
        cycle_points = [1, 2, 3, 4, 5, 6, 1]
        cycle_h = [data_with_slhx[i]['H'] / 1000 for i in cycle_points]
        cycle_p = [data_with_slhx[i]['P'] / 1e5 for i in cycle_points]

        ax.plot(cycle_h, cycle_p, 'ko-', lw=2, label='Cycle with SLHX' if use_slhx else 'Cycle without SLHX')
        ax.legend()

        ax.set_xlabel('Enthalpy [kJ/kg]')
        ax.set_ylabel('Pressure [bar]')
        ax.set_ylim(bottom=p_min / 100000, top=p_max / 100000)
        ax.set_xlim(left=h_min / 1000, right=1.1 * max(max(cycle_h), h_max / 1000))
        ax.set_title(f"Pressure-Enthalpy Diagram for {refrigerant.upper()} {'with SLHX' if use_slhx else 'without SLHX'}")
        ax.grid(True, which='both', ls='--', lw=0.5)

        return ax


    # Call the function
    refrigerant = "co2"
    use_slhx = True
    use_two_phase_evap_exit = True

    data_with_slhx = calculate_slhx_state_points(refrigerant=refrigerant, use_slhx=use_slhx, use_two_phase_evap_exit=use_two_phase_evap_exit)
    ax_figure, p_min, p_max, h_min, h_max = plot_ph_diagram_with_cycle(refrigerant=refrigerant, use_slhx=use_slhx, use_two_phase_evap_exit=use_two_phase_evap_exit)
    final_figure = overlay_cycle_on_ax(ax_figure, data_with_slhx, refrigerant, use_slhx, p_min, p_max, h_min, h_max)
    plt.show()

if __name__ == "__main__":
    plot_ph_v3()