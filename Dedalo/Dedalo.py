from rocketpy import Environment, Flight, Rocket, SolidMotor
import numpy
import datetime
import pandas as pd
import numpy as np
import json

env = Environment(latitude=-21.9430528, longitude=-48.9540861, elevation=478)
env.set_date(datetime.datetime.now())
env.set_atmospheric_model(type="Forecast", file="GFS")
# motor and rocket data 
motor_data = pd.read_csv("motor_teste_estatico_final.csv")
motor_config  = pd.read_json("dedalo_motor.json" , typ="series")
rocket_data = pd.read_json("dedalo_data.json", typ="series")

Dedalo_motor = SolidMotor(
    thrust_source=motor_data, # Use the NumPy array
    dry_mass= motor_config["dry_mass"],
    dry_inertia=motor_config["dry_inertia"],
    nozzle_radius=motor_config["nozzle_radius"],
    grain_number=motor_config["grain_number"],
    grain_density=motor_config["grain_density"],
    grain_outer_radius=motor_config["grain_outer_radius"],
    grain_initial_inner_radius=motor_config["grain_initial_inner_radius"],
    grain_initial_height=motor_config["grain_initial_height"],
    grain_separation=motor_config["grain_separation"],
    grains_center_of_mass_position=motor_config["grains_center_of_mass_position"], 
    center_of_dry_mass_position=motor_config["center_of_dry_mass_position"], 
    nozzle_position=motor_config["nozzle_position"], 
    burn_time=motor_data['Time(s)'].iloc[-1],
    throat_radius=motor_config["throat_radius"],
    coordinate_system_orientation=motor_config["coordinate_system_orientation"],
)
print("\nSolidMotor initialized successfully!")
Dedalo_rocket = Rocket(
    radius = rocket_data["radius"],
    mass= rocket_data["mass"],
    power_off_drag="poweroff.csv",
    power_on_drag="poweron.csv",
    inertia= rocket_data["inertia"],
    center_of_mass_without_motor= rocket_data["center_of_mass_without_motor"],
    coordinate_system_orientation= rocket_data["coordinate_system_orientation"],
)

print("Rocket object created successfully!")
Dedalo_rocket.add_motor(Dedalo_motor, position=1.65)

nose_cone = Dedalo_rocket.add_nose(
    length=rocket_data["nose_length"], kind=rocket_data["nose_type"], position=rocket_data["nose_position"]
)

fins = Dedalo_rocket.add_trapezoidal_fins(
    n = rocket_data["n_aletas"],
    root_chord= rocket_data["root_chord"],
    tip_chord= rocket_data["tip_chord"],
    span= rocket_data["span"],
    position= rocket_data["position"],
    cant_angle= rocket_data["cant_angle"]
)

rail_buttons = Dedalo_rocket.set_rail_buttons(
    upper_button_position=0.385,
    lower_button_position=1.08,
    angular_position=45,
)

def apogee_acc_trigger(_pressure, _height, state_vector, u_dot):
    vz = state_vector[5]
    az = u_dot[5]
    return abs(vz) < 1.0 and az < -0.1

main = Dedalo_rocket.add_parachute(
    name="main",
    cd_s=1.5,
    trigger=apogee_acc_trigger, 
    sampling_rate=105,
    lag=1.5,
    radius=0.6,
    noise=(0, 8.3, 0.5),
)


Dedalo_flight = Flight(
    rocket=Dedalo_rocket, environment=env, rail_length=4, inclination=85, heading=0
    )


# ============================================================
# EXPORTAÇÃO DO LOG DE VOO
# ============================================================

import os
# Tempos da simulação
tempos = Dedalo_flight.solution_array[:, 0]

dados = []

for t in tempos:

    dados.append([
        # ----------------------------------------------------
        # time
        # ----------------------------------------------------
        t,

        # ----------------------------------------------------
        # altp
        # Altitude de pressão
        # ----------------------------------------------------
        44330.0 * (
            1.0 - (
                Dedalo_flight.pressure(t) / 101325.0
            ) ** 0.190294957
        ),

        # ----------------------------------------------------
        # temp
        # Temperatura atmosférica
        # ----------------------------------------------------
        env.temperature(Dedalo_flight.altitude(t)),

        # ----------------------------------------------------
        # p
        # Pressão atmosférica em Pa
        # ----------------------------------------------------
        Dedalo_flight.pressure(t),

        # ----------------------------------------------------
        # gx, gy, gz
        # Velocidades angulares do corpo
        # ----------------------------------------------------
        Dedalo_flight.w1(t),
        Dedalo_flight.w2(t),
        Dedalo_flight.w3(t),

        # ----------------------------------------------------
        # ax, ay, az
        # ACELERAÇÕES DO ROCKETPY
        # ----------------------------------------------------
        Dedalo_flight.ax(t),
        Dedalo_flight.ay(t),
        Dedalo_flight.az(t),

        # ----------------------------------------------------
        # vz
        # Velocidade vertical
        # ----------------------------------------------------
        Dedalo_flight.vz(t),

        # ----------------------------------------------------
        # alt
        # Altitude acima do solo
        # ----------------------------------------------------
        Dedalo_flight.altitude(t),

        # ----------------------------------------------------
        # lat / lon
        # ----------------------------------------------------
        Dedalo_flight.latitude(t),
        Dedalo_flight.longitude(t),
    ])


# ============================================================
# Nomes das colunas
# ============================================================

colunas = [
    "time",
    "altp",
    "temp",
    "p",
    "gx",
    "gy",
    "gz",
    "ax",
    "ay",
    "az",
    "vz",
    "alt",
    "lat",
    "lon",
]


# ============================================================
# DataFrame
# ============================================================

df = pd.DataFrame(
    dados,
    columns=colunas
)


# ============================================================
# Exportação
# ============================================================

os.makedirs("logs", exist_ok=True)

arquivo = "logs/log_voo_rocketpy.csv"

df.to_csv(
    arquivo,
    index=False
)

print(
    f"Log de voo exportado com sucesso para '{arquivo}'!"
)

print(f"Total de amostras: {len(df)}")
print(f"Colunas: {list(df.columns)}")

