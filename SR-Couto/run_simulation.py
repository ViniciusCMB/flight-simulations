"""Run full flight simulation and save trajectory data to CSV.

Run this OUTSIDE the Jupyter notebook to avoid UI freezing.
Then load flight_data.csv in the notebook for analysis.
"""
import pandas as pd
import numpy as np
from rocketpy import Environment, Flight, Rocket, SolidMotor
import warnings, time, json
warnings.filterwarnings('ignore')

print("="*60)
print("SR-Couto Flight Simulation - Standalone Runner")
print("="*60)

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

# Drag curves as callable functions (faster than Function objects)
def make_drag_func(filepath):
    drag_data = pd.read_csv(filepath, delimiter=';', skipinitialspace=True, header=None, decimal=',')
    drag_data.dropna(axis=1, how='all', inplace=True)
    for col in drag_data.columns:
        drag_data[col] = pd.to_numeric(drag_data[col], errors='coerce')
    drag_data.dropna(inplace=True)
    drag_data = drag_data.sort_values(drag_data.columns[0]).drop_duplicates(drag_data.columns[0])
    mach = drag_data.iloc[:, 0].values
    cd = drag_data.iloc[:, 1].values
    def drag_func(mach_value):
        return float(np.interp(mach_value, mach, cd))
    return drag_func

power_off_drag = make_drag_func("poweroffdragcurve.csv")
power_on_drag = make_drag_func("powerondragcurve.csv")

# Rocket
SRrocket = Rocket(
    radius=0.038, mass=3.275, inertia=(0.723, 0.723, 0.002),
    power_off_drag=power_off_drag, power_on_drag=power_on_drag,
    center_of_mass_without_motor=0.735, coordinate_system_orientation="nose_to_tail",
)
SRrocket.add_motor(SRmotor, position=1.5)
SRrocket.add_nose(length=0.197, kind="Ogive", position=0)
SRrocket.add_trapezoidal_fins(n=4, root_chord=0.10, tip_chord=0.047, span=0.057, position=1.395, cant_angle=58.99)
SRrocket.add_parachute(name="main", cd_s=1.5, trigger=750, sampling_rate=10, lag=1.5, radius=0.6, noise=(0, 0, 0))
SRrocket.set_rail_buttons(upper_button_position=0.385, lower_button_position=1.08, angular_position=45)

print("\nStarting Flight simulation...")
print("(This takes ~40s - do not interrupt)")
t0 = time.time()
tf = Flight(rocket=SRrocket, environment=env, rail_length=4, inclination=85, heading=0,
            max_time=90, terminate_on_apogee=False)
elapsed = time.time()-t0
print(f"\nSimulation completed in {elapsed:.1f}s")
print(f"Apogee: {tf.apogee:.1f} m")

# Extract and save solution
solution = tf.solution
# Each row: [t, x, y, z, vx, vy, vz, e0, e1, e2, e3, w1, w2, w3, mass]
solution_cols = ['Time', 'X', 'Y', 'Z', 'Vx', 'Vy', 'Vz', 'e0', 'e1', 'e2', 'e3', 'w1', 'w2', 'w3']
if solution.shape[1] > 14:
    solution_cols.append('mass')
if solution.shape[1] > 15:
    solution_cols.append('mass_i')

df = pd.DataFrame(solution, columns=solution_cols[:solution.shape[1]])
df.to_csv("flight_data.csv", index=False)
print(f"Saved flight_data.csv ({len(df)} rows)")

# Print summary
print("\n" + "="*60)
print("FLIGHT SUMMARY")
print("="*60)
print(f"Apogee:              {tf.apogee:.1f} m (ASL)")
print(f"Max speed:           {tf.max_speed:.1f} m/s (Mach {tf.max_speed/340:.2f})")
print(f"Max Mach:            {tf.max_mach_number:.3f}")
print(f"Rail departure V:    {tf.rail_departure_velocity:.1f} m/s")
print(f"Burn time:           {tf.burn_out_time:.2f} s")
print(f"Time to apogee:      {tf.time_to_apogee:.2f} s")

# Save summary as JSON
summary = {
    "apogee": float(tf.apogee),
    "max_speed": float(tf.max_speed),
    "max_mach": float(tf.max_mach_number),
    "rail_departure_velocity": float(tf.rail_departure_velocity),
    "burn_out_time": float(tf.burn_out_time),
    "time_to_apogee": float(tf.time_to_apogee),
    "simulation_time_s": elapsed,
    "impact_time": float(df['Time'].iloc[-1]),
}
with open("flight_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("Saved flight_summary.json")
