import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.interpolate import interp1d
from scipy.optimize import differential_evolution


def objective_function(params, t, pv_hist, cv_hist):
    # Unpack parameters
    Kp, tau, theta = params

    # Basic constraints to keep parameters realistic
    if Kp <= 0 or tau <= 0 or theta < 0:
        return 1e9  # Return a large number for invalid parameters

    # Simulate the model response
    pv_sim = simulate_fopdt(params, t, cv_hist)

    # Calculate Sum of Squared Errors (SSE)
    error = np.sum((pv_hist - pv_sim) ** 2)
    return error


def simulate_fopdt(params, t, cv):
    Kp, tau, theta = params
    dt = t[1] - t[0]
    pv_sim = np.zeros_like(t)

    # Calculate the number of discrete steps for the dead time
    delay_steps = int(round(theta / dt))

    # Create a delayed version of the CV signal
    cv_delayed = np.zeros_like(cv)
    if delay_steps > 0 and delay_steps < len(cv):
        cv_delayed[delay_steps:] = cv[:-delay_steps]
    else:
        cv_delayed = cv

    for i in range(1, len(t)):
        # First-order dynamics using the pre-calculated delayed CV
        d_pv = (Kp * cv_delayed[i] - pv_sim[i - 1]) / tau
        pv_sim[i] = pv_sim[i - 1] + d_pv * dt

    return pv_sim


def identify_process_model(t, pv, cv):
    bounds = [(0.1, 5.0), (1, 20.0), (0.5, 5.0)]  # Adjusted bounds for robustness

    # Run the optimization using differential_evolution.
    result = differential_evolution(
        objective_function,
        bounds,
        args=(t, pv, cv),
        popsize=30,
        maxiter=1000,
        tol=0.01,
        recombination=0.7,
        strategy="best1bin",
    )

    if result.success:
        identified_params = result.x
        return identified_params
    else:
        print("Error: System identification failed.")
        print(result.message)
        return None


def calculate_tuning_params(Kp, tau, theta):
    if Kp is None or tau is None or theta is None or theta == 0:
        print("Cannot calculate tuning rules with invalid model parameters.")
        return {}

    # --- Ziegler-Nichols ---
    zn_kc = (1.2 * tau) / (Kp * theta)
    zn_ti = 2.0 * theta
    zn_td = 0.5 * theta

    zn_kp = zn_kc
    zn_ki = zn_kc / zn_ti
    zn_kd = zn_kc * zn_td

    # --- Cohen-Coon ---
    cc_kc = (tau / (Kp * theta)) * (4 / 3 + theta / (4 * tau))
    cc_ti = theta * (32 + 6 * theta / tau) / (13 + 8 * theta / tau)
    cc_td = theta * 4 / (11 + 2 * theta / tau)

    cc_kp = cc_kc
    cc_ki = cc_kc / cc_ti
    cc_kd = cc_kc * cc_td

    # --- IMC (Lambda) Tuning ---
    lambda_val = tau
    imc_kc = (tau + 0.5 * theta) / (Kp * (lambda_val + 0.5 * theta))
    imc_ti = tau + 0.5 * theta
    imc_td = (tau * theta) / (2 * tau + theta)

    imc_kp = imc_kc
    imc_ki = imc_kc / imc_ti
    imc_kd = imc_kc * imc_td

    tuning_results = {
        "Ziegler-Nichols": {"Kp": zn_kp, "Ki": zn_ki, "Kd": zn_kd},
        "Cohen-Coon": {"Kp": cc_kp, "Ki": cc_ki, "Kd": cc_kd},
        "IMC (Lambda)": {"Kp": imc_kp, "Ki": imc_ki, "Kd": imc_kd},
    }
    return tuning_results
