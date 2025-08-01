import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.interpolate import interp1d
from scipy.optimize import differential_evolution

from helpers.simulation import *
from helpers.optimization import *

st.set_page_config(page_title="PID Controller Simulation")

st.title("PID Controller Simulation")

# Sidebar input: Process parameters
st.sidebar.header("Process Parameters")
proc_Kp = st.sidebar.number_input("Process Gain (Kp)", value=2.0, step=0.1)
proc_tau = st.sidebar.number_input("Time Constant (tau)", value=10.0, step=0.1)
proc_theta = st.sidebar.number_input("Dead Time (theta)", value=2.0, step=0.1)

# Sidebar input: PID parameters
st.sidebar.header("PID Tunning")
pid_Kp = st.sidebar.number_input("PID Kp", value=2.0, step=0.1)
pid_Ki = st.sidebar.number_input("PID Ki", value=0.5, step=0.1)
pid_Kd = st.sidebar.number_input("PID Kd", value=1.0, step=0.1)

# Simulation constants
SIM_DURATION = 400
DT = 0.1
SETPOINTS = [
    (0, 21.0),
    (50, 80.0),
    (75, 40.0),
    (100, 100.0),
    (120, 60.0),
    (150, 10.0),
    (175, 50.0),
    (200, 100.0),
    (220, 83.0),
    (250, 40.0),
    (275, 50.0),
    (300, 10.0),
    (320, 43.0),
    (350, 28.0),
    (375, 87.0),
    (400, 100.0),
]

# Run simulation
process = ProcessModel(proc_Kp, proc_tau, proc_theta, DT)
controller = PIDController(pid_Kp, pid_Ki, pid_Kd)
process_simulation, metrics = run_simulation(
    process, controller, SETPOINTS, SIM_DURATION, DT
)

# Chart
st.line_chart(process_simulation.set_index("Time")[["SP", "PV"]])

# Optimization calculations button
if st.button("Run PID Optimization"):
    with st.spinner(text="In progress..."):
        estimated_model_params = identify_process_model(
            process_simulation["Time"],
            process_simulation["PV"],
            process_simulation["MV"],
        )
        pid_tuning_results = calculate_tuning_params(*estimated_model_params)

        info_groups = {
            "Performance Metrics": {
                "IAE": metrics["IAE"],
                "COI": metrics["COI"],
                "Oscillation": metrics["Oscillation Index"],
            },
            "Ziegler-Nichols": {
                "P": pid_tuning_results["Ziegler-Nichols"]["Kp"],
                "I": pid_tuning_results["Ziegler-Nichols"]["Ki"],
                "D": pid_tuning_results["Ziegler-Nichols"]["Kd"],
            },
            "Cohen-Coon": {
                "P": pid_tuning_results["Cohen-Coon"]["Kp"],
                "I": pid_tuning_results["Cohen-Coon"]["Ki"],
                "D": pid_tuning_results["Cohen-Coon"]["Kd"],
            },
            "IMC (Lambda)": {
                "P": pid_tuning_results["IMC (Lambda)"]["Kp"],
                "I": pid_tuning_results["IMC (Lambda)"]["Ki"],
                "D": pid_tuning_results["IMC (Lambda)"]["Kd"],
            },
        }

        for group, group_metrics in info_groups.items():
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"### {group}")
            with col2:
                for name, value in group_metrics.items():
                    st.write(f"**{name}**: {value:.2f}")
