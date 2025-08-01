
## Features

* **Interactive Simulation**: Visualize the real-time response of a PID-controlled system by adjusting parameters in the sidebar and viewing the `SP` and `PV` chart.
* **Customizable Process Parameters**: Adjust the Process Gain (`Kp`), Time Constant (`tau`), and Dead Time (`theta`) of the FOPDT model.
* **Real-time PID Tuning**: Modify the Proportional (`Kp`), Integral (`Ki`), and Derivative (`Kd`) gains of the PID controller and observe the effects on the simulation.
* **Performance Metrics**: The simulation calculates and displays key performance indicators, including Integral Absolute Error (IAE), Control Output Index (COI), and an Oscillation Index.
* **Automated PID Tuning**: On-demand calculation of optimal PID parameters using well-known tuning rules:
    * Ziegler-Nichols
    * Cohen-Coon
    * IMC (Lambda)
* **System Identification**: The application can estimate the process model parameters from the simulation data using a `differential_evolution` optimization algorithm.

---


## Code Overview

* `app.py`: This is the main file that creates the Streamlit user interface. It handles user inputs, runs the simulation, displays the output chart, and manages the optimization process.
* `simulation.py`: This file contains the core logic for the simulation. The `ProcessModel` class represents the FOPDT process, the `PIDController` class implements the control algorithm, and `run_simulation` executes the simulation loop.
* `optimization.py`: This file includes the functions for identifying the process model and calculating optimal PID tuning parameters. It uses `differential_evolution` to find the best-fit model and then calculates tuning parameters for Ziegler-Nichols, Cohen-Coon, and IMC methods.
