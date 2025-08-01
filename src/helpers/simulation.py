import streamlit as st
import numpy as np
import pandas as pd


class ProcessModel:
    def __init__(self, Kp, tau, theta, dt):
        self.Kp = Kp
        self.tau = tau
        self.theta = theta
        self.pv = 0.0
        self.buffer = [0.0] * (int(theta / dt) if dt > 0 else 0)

    def update(self, cv, dt):
        if self.buffer:
            delayed_cv = self.buffer.pop(0)
            self.buffer.append(cv)
        else:
            delayed_cv = cv
        # Simple process simulation
        d_pv = (self.Kp * delayed_cv - self.pv) / self.tau
        self.pv += d_pv * dt
        return self.pv


class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.integral = 0.0
        self.previous_error = 0.0

    def calculate(self, sp, pv, dt):
        error = sp - pv
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        self.previous_error = error
        return self.Kp * error + self.Ki * self.integral + self.Kd * derivative


def run_simulation(process, controller, setpoints, duration, dt):
    time_points = np.arange(0, duration, dt)
    pv_history, cv_history, sp_history = [], [], []
    iae = coi = oscillation_index = 0.0
    error_last = cv_last = 0.0
    current_sp = setpoints[0][1]

    for t in time_points:
        for sp_time, sp_value in reversed(setpoints):
            if t >= sp_time:
                current_sp = sp_value
                break
        sp_history.append(current_sp)
        cv = controller.calculate(current_sp, process.pv, dt)
        pv = process.update(cv, dt)

        pv_history.append(pv)
        cv_history.append(cv)

        error = current_sp - pv
        iae += abs(error) * dt
        if t > 0:
            coi += abs(cv - cv_last) * dt
            if error * error_last < 0:
                oscillation_index += 1
        cv_last = cv
        error_last = error

    metrics = {"IAE": iae, "COI": coi, "Oscillation Index": oscillation_index}

    df = pd.DataFrame(
        {"Time": time_points, "SP": sp_history, "PV": pv_history, "MV": cv_history}
    )

    return df, metrics
