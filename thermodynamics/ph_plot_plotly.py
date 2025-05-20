import numpy as np
import plotly.graph_objects as go
import webbrowser
from CoolProp.CoolProp import PropsSI
import CoolProp.CoolProp as CP

def plot_ph_plotly():
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
    # import plotly.io as pio



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
        T_range_high = np.linspace(T_crit - 5, T_crit - 0.00000001, 300)
        T_range = np.concatenate((T_range_low, T_range_high))
        h_q1 = []
        for T in T_range:
            try:
                hq = PropsSI('H', 'T', T, 'Q', 1, refrigerant)
                h_q1.append(hq)
            except:
                continue
        h_max = max(h_q1) * 1.2

        T_triple = PropsSI('Ttriple', refrigerant)
        p_min = PropsSI('P', 'T', T_triple, 'Q', 0, refrigerant)
        print(f"Minimum pressure is {p_min}")

        fig = go.Figure()

        # h_plot_max = max(h_q1)
        try:
            T_max_calc = PropsSI('T', 'P', p_max, 'H', h_max * 1.2, refrigerant)
            if np.isnan(T_max_calc):
                T_max_calc = T_crit - 0.001
        except:
            T_max_calc = T_crit - 0.001

        temperatures = np.linspace(T_min, T_max_calc, 50)
        pressures = np.logspace(np.log10(p_min), np.log10(p_max), 400)
        for T in temperatures:
            h_vals, p_vals, customdata = [], [], []
            for P in pressures:
                try:
                    h = PropsSI('H', 'T', T, 'P', P, refrigerant)
                    if not np.isnan(h):
                        h_vals.append(h / 1000)
                    p_vals.append(P / 100000)
                    try:
                        s = PropsSI('S', 'T', T, 'P', P, refrigerant) / 1000
                        rho = PropsSI('D', 'T', T, 'P', P, refrigerant)
                        q = PropsSI('Q', 'T', T, 'P', P, refrigerant)
                        customdata.append([P / 100000, h / 1000, f"{T - 273.15:.2f}", f"{s:.3f}", f"{rho:.2f}", f"{q:.2f}"])
                    except:
                        customdata.append([P / 100000, h / 1000, T - 273.15, 'N/A', 'N/A', 'N/A'])
                except:
                    continue
            if h_vals:
                fig.add_trace(go.Scatter(
                    x=h_vals, y=p_vals, mode='lines',
                    line=dict(color='red', width=1),
                    customdata=customdata,
                    hovertemplate='P: %{customdata[0]:.2f} bar<br>h: %{customdata[1]:.2f} kJ/kg<br>T: %{customdata[2]:.2f} °C<br>s: %{customdata[3]} kJ/kg·K<br>ρ: %{customdata[4]} kg/m³<br>Q: %{customdata[5]}',
                    showlegend=False))

        qualities = np.linspace(0, 1, 11)
        for Q in qualities:
            h_sat, p_sat, customdata = [], [], []
            T_range = np.concatenate((T_range_low, T_range_high))
            for T in T_range:
                try:
                    p = PropsSI('P', 'T', T, 'Q', Q, refrigerant)
                    hq = PropsSI('H', 'T', T, 'Q', Q, refrigerant)
                    h_sat.append(hq / 1000)
                    p_sat.append(p / 100000)
                    try:
                        s = PropsSI('S', 'T', T, 'Q', Q, refrigerant) / 1000
                        rho = PropsSI('D', 'T', T, 'Q', Q, refrigerant)
                        customdata.append([P / 100000, h / 1000, f"{T - 273.15:.2f}", f"{s:.3f}", f"{rho:.2f}", f"{q:.2f}"])
                    except:
                        customdata.append([p / 100000, hq / 1000, T - 273.15, 'N/A', 'N/A', f"{Q:.2f}"])
                except:
                    continue
            fig.add_trace(go.Scatter(
                    x=h_sat,
                    y=p_sat,
                    mode='lines',
                    line=dict(color='black' if Q in [0, 1] else 'lightgray', width=2 if Q in [0, 1] else 1),
                    customdata=customdata,
                    hovertemplate='P: %{customdata[0]:.2f} bar<br>h: %{customdata[1]:.2f} kJ/kg<br>T: %{customdata[2]:.2f} °C<br>s: %{customdata[3]} kJ/kg·K<br>ρ: %{customdata[4]} kg/m³<br>Q: %{customdata[5]}',
                    showlegend=False))

        rho_min = PropsSI('D', 'T', T_min + 1, 'Q', 1, refrigerant)
        rho_max = PropsSI('D', 'T', T_crit - 1, 'Q', 0, refrigerant)
        densities = np.geomspace(rho_min * 2, rho_max, 20)
        for rho in densities:
            h_vals, p_vals, customdata = [], [], []
            for P in pressures:
                try:
                    h = PropsSI('H', 'D', rho, 'P', P, refrigerant)
                    if not np.isnan(h):
                        h_vals.append(h / 1000)
                        p_vals.append(P / 100000)
                        try:
                            T = PropsSI('T', 'D', rho, 'P', P, refrigerant)
                            s = PropsSI('S', 'D', rho, 'P', P, refrigerant) / 1000
                            q = PropsSI('Q', 'D', rho, 'P', P, refrigerant)
                            customdata.append([P / 100000, h / 1000, T - 273.15, s, rho, f"{q:.2f}"])
                        except:
                            customdata.append([P / 100000, h / 1000, 'N/A', 'N/A', 'N/A', 'N/A'])
                        try:
                            T = PropsSI('T', 'S', s * 1000, 'P', P, refrigerant)
                            rho = PropsSI('D', 'S', s * 1000, 'P', P, refrigerant)
                            q = PropsSI('Q', 'S', s * 1000, 'P', P, refrigerant)
                            customdata.append([P / 100000, h / 1000, f"{T - 273.15:.2f}", f"{s:.3f}", f"{rho:.2f}", f"{q:.2f}"])
                        except:
                            customdata.append([P / 100000, h / 1000, 'N/A', s, 'N/A', 'N/A'])
                except:
                    continue
            if h_vals:
                fig.add_trace(go.Scatter(
                    x=h_vals,
                    y=p_vals,
                    mode='lines',
                    line=dict(color='green', width=1),
                    customdata=customdata,
                    hovertemplate='P: %{customdata[0]:.2f} bar<br>h: %{customdata[1]:.2f} kJ/kg<br>T: %{customdata[2]} °C<br>s: %{customdata[3]} kJ/kg·K<br>ρ: %{customdata[4]} kg/m³<br>Q: %{customdata[5]}',
                    showlegend=False))

        s_min = PropsSI('S', 'T', T_min + 1, 'Q', 0, refrigerant) / 1000
        s_max = PropsSI('S', 'P', p_max, 'H', h_max * 1.2, refrigerant) / 1000
        entropies = np.linspace(s_min, s_max, 50)
        for s in entropies:
            h_vals, p_vals, customdata = [], [], []
            for P in pressures:
                try:
                    h = PropsSI('H', 'S', s * 1000, 'P', P, refrigerant)
                    if not np.isnan(h):
                        h_vals.append(h / 1000)
                        p_vals.append(P / 100000)
                        try:
                            T = PropsSI('T', 'H', h, 'P', P, refrigerant)
                            rho = PropsSI('D', 'H', h, 'P', P, refrigerant)
                            q = PropsSI('Q', 'H', h, 'P', P, refrigerant)
                            customdata.append([P / 100000, h / 1000, f"{T - 273.15:.2f}", f"{s:.3f}", f"{rho:.2f}", f"{q:.2f}"])
                        except:
                            customdata.append([P / 100000, h / 1000, 'N/A', 'N/A', 'N/A', 'N/A'])
                except:
                    continue
            if h_vals:
                fig.add_trace(go.Scatter(
                    x=h_vals,
                    y=p_vals,
                    mode='lines',
                    line=dict(color='blue', width=1),
                    customdata=customdata,
                    hovertemplate='P: %{customdata[0]:.2f} bar<br>h: %{customdata[1]:.2f} kJ/kg<br>T: %{customdata[2]} °C<br>s: %{customdata[3]:.3f} kJ/kg·K<br>ρ: %{customdata[4]} kg/m³<br>Q: %{customdata[5]}',
                    showlegend=False))

        return fig, p_min, p_max, h_min, h_max


    def overlay_cycle_on_ax(fig, data_with_slhx, refrigerant, use_slhx, p_min, p_max, h_min, h_max):
        cycle_points = [1, 2, 3, 4, 5, 6, 1]
        cycle_h = [data_with_slhx[i]['H'] / 1000 for i in cycle_points]
        cycle_p = [data_with_slhx[i]['P'] / 1e5 for i in cycle_points]

        hover_texts = []
        for i, point in enumerate(cycle_points):
            st = data_with_slhx[point if point != 1 else 1]
            P_bar = st['P'] / 1e5
            T_C = st['T'] - 273.15
            h = st['H'] / 1000
            s = st['S'] / 1000
            rho = PropsSI('D', 'P', st['P'], 'H', st['H'], refrigerant)
            try:
                Q = PropsSI('Q', 'P', st['P'], 'H', st['H'], refrigerant)
                Q_str = f"{Q:.2f}"
            except:
                Q_str = "N/A"
            hover_texts.append(
                f"<b>State {point if point != 1 or i == 0 else 1}</b><br>P: {P_bar:.2f} bar<br>T: {T_C:.2f} °C<br>h: {h:.2f} kJ/kg<br>s: {s:.3f} kJ/kg·K<br>ρ: {rho:.2f} kg/m³<br>Q: {Q_str}"
            )

        fig.add_trace(go.Scatter(
            x=cycle_h,
            y=cycle_p,
            mode='lines+markers',
            line=dict(color='black', width=3),
            name='Cycle',
            text=hover_texts,
            hoverinfo='text'
        ))

        font_scale = 2  # Adjustable font scale for axis titles and ticks

        fig.update_layout(
            title=f"Pressure-Enthalpy Diagram for {refrigerant.upper()} {'with SLHX' if use_slhx else 'without SLHX'}",
            xaxis_title=dict(text='Enthalpy [kJ/kg]', font=dict(size=14 * font_scale)),
            yaxis_title=dict(text='Pressure [bar]', font=dict(size=14 * font_scale)),
            yaxis_type='linear',
            xaxis_range=[h_min / 1000, max(1.1 * h_max / 1000, max(cycle_h) * 1.05)],
            yaxis_range=[p_min / 100000, p_max / 100000],
            template='plotly_white',
            xaxis=dict(tickfont=dict(size=12 * font_scale)),
            yaxis=dict(tickfont=dict(size=12 * font_scale))
        )

        return fig


    # Call the function
    refrigerant = "co2"
    use_slhx = True
    use_two_phase_evap_exit = True

    data_with_slhx = calculate_slhx_state_points(refrigerant=refrigerant, use_slhx=use_slhx, use_two_phase_evap_exit=use_two_phase_evap_exit)
    ax_figure, p_min, p_max, h_min, h_max = plot_ph_diagram_with_cycle(refrigerant=refrigerant, use_slhx=use_slhx, use_two_phase_evap_exit=use_two_phase_evap_exit)
    final_figure = overlay_cycle_on_ax(ax_figure, data_with_slhx, refrigerant, use_slhx, p_min, p_max, h_min, h_max)
    final_figure.write_html("ph_diagram.html")
    webbrowser.open("ph_diagram.html")


    def simulate_multiple_cycles(refrigerant='co2', pressure_range=(60, 130), num_cycles=10, use_slhx=True, use_two_phase_evap_exit=False):
        pressures = np.linspace(pressure_range[0], pressure_range[1], num_cycles)
        fig, p_min, p_max, h_min, h_max = plot_ph_diagram_with_cycle(refrigerant, use_slhx, use_two_phase_evap_exit)

        for i, P_bar in enumerate(pressures):
            print(f"Cycle {i+1} at {P_bar:.1f} bar")
            data = calculate_slhx_state_points(
                refrigerant=refrigerant,
                high_side_pressure_bar=P_bar,
                use_slhx=use_slhx,
                use_two_phase_evap_exit=use_two_phase_evap_exit
            )
            fig = overlay_cycle_on_ax(fig, data, refrigerant, use_slhx, p_min, p_max, h_min, h_max)

        fig.write_html("ph_diagram_multiple_cycles.html")
        webbrowser.open("ph_diagram_multiple_cycles.html")


    # simulate_multiple_cycles()

if __name__ == "__main__":
    plot_ph_plotly()