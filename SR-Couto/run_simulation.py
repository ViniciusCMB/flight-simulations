"""Run flight simulation and save results to pickle."""
import pandas as pd
import numpy as np
import pickle
import time
from rocketpy import Environment, Flight, Function, Rocket, SolidMotor
import warnings
warnings.filterwarnings('ignore')

print("Starting simulation...")
t0 = time.time()

# Environment
env = Environment(latitude=-21.9430528, longitude=-48.9540861, elevation=478)

# Motor
motor_data = pd.read_csv("motor_data.csv")
thrust_source_array = motor_data[['Time(s)', 'Thrust(N)']].values
SRmotor = SolidMotor(
    thrust_source=thrust_source_array,
    dry_mass=0.85601,
    dry_inertia=(0.00001932937824, 0.00001932937909, 0.00000038491070),
    nozzle_radius=0.014885, grain_number=2, grain_density=1750,
    grain_outer_radius=0.022, grain_initial_inner_radius=0.0075,
    grain_initial_height=0.175, grain_separation=0,
    grains_center_of_mass_position=0.2, center_of_dry_mass_position=0.24,
    nozzle_position=0, burn_time=motor_data['Time(s)'].iloc[-1],
    throat_radius=0.0070, coordinate_system_orientation="nozzle_to_combustion_chamber",
)

# Drag curves
def load_drag_curve(filepath):
    drag_data = pd.read_csv(filepath, delimiter=';', skipinitialspace=True, header=None, decimal=',')
    drag_data.dropna(axis=1, how='all', inplace=True)
    for col in drag_data.columns:
        drag_data[col] = pd.to_numeric(drag_data[col], errors='coerce')
    drag_data.dropna(inplace=True)
    drag_data = drag_data.sort_values(drag_data.columns[0]).drop_duplicates(drag_data.columns[0])
    return Function(
        drag_data.values.tolist(),
        inputs=["Mach"],
        outputs=["Drag Coefficient"],
        extrapolation="constant",
    )

power_off_drag = load_drag_curve("poweroffdragcurve.csv")
power_on_drag = load_drag_curve("powerondragcurve.csv")

# Rocket
SRrocket = Rocket(
    radius=0.038, mass=3.275, inertia=(0.723, 0.723, 0.002),
    power_off_drag=power_off_drag, power_on_drag=power_on_drag,
    center_of_mass_without_motor=0.735, coordinate_system_orientation="nose_to_tail",
)
SRrocket.add_motor(SRmotor, position=1.5)
SRrocket.add_nose(length=0.197, kind="Ogive", position=0)
SRrocket.add_trapezoidal_fins(n=4, root_chord=0.10, tip_chord=0.047, span=0.057, position=1.395, cant_angle=58.99)
SRrocket.add_parachute(name="main", cd_s=1.5, trigger=750, sampling_rate=10, lag=1.5, radius=0.6, noise=(0, 8.3, 0.5))
SRrocket.set_rail_buttons(upper_button_position=0.385, lower_button_position=1.08, angular_position=45)

print(f"Rocket ready. Running Flight... ({time.time()-t0:.1f}s elapsed)")

# Flight
test_flight = Flight(
    rocket=SRrocket, environment=env, rail_length=4, inclination=85, heading=0,
    max_time=90, terminate_on_apogee=False, verbose=True,
)

elapsed = time.time() - t0
print(f"\nSimulation completed in {elapsed:.1f}s")
print(f"Apogee: {test_flight.apogee:.1f} m")

# Save results
with open("simulation_results.pkl", "wb") as f:
    pickle.dump(test_flight, f)

print("Results saved to simulation_results.pkl")
