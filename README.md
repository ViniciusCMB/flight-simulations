# flight-simulations

Flight simulations for **Serra Rocketry / UERJ** (Projeto S) rockets, built with [RocketPy](https://github.com/RocketPy-Team/RocketPy).

Three vehicles are simulated: the sounding rockets **Dédalo** and **Thonyan**, and the **SR-Couto** reference model. Simulations use GFS forecast wind data, static-fire-derived thrust curves, and Monte Carlo dispersion analysis for apogee/landing predictions.

## Repository layout

```
flight-simulations/
├── Dedalo/     # Dédalo — 1000 m apogee target
├── Thonyan/    # Thonyan — 500 m apogee target
└── SR-Couto/   # SR-Couto reference simulation + drag curves
```

### Dedalo/

| File | Description |
|------|-------------|
| `Simulacao_dedalo.ipynb` | Full flight simulation: environment (GFS winds), rocket, solid motor, single Flight run and Monte Carlo analysis |
| `simulacao_balistica_dedalo.ipynb` | Ballistic (drogueless) trajectory simulation |
| `tratamento_teste.ipynb` | Static fire data processing: raw load cell logs → cleaned thrust curve |
| `dedalo_data.json` | Rocket geometry/mass parameters (RocketPy `Rocket`) |
| `dedalo_motor.json` | Motor grain/nozzle parameters (RocketPy `SolidMotor`) |
| `motor_teste_estatico_final.csv` | Current official thrust curve (from 25/08/2026 static fire) |
| `Dados_031.csv`, `motor_teste_statco2.csv`, `dadoslimpos.csv`, `motor_data_novo_1.csv`, `motor_data_pronto.csv`, `motor.csv`, `poweron/off.csv` | Raw and intermediate static-fire datasets and legacy thrust curves |
| `monte_carlo_dedalo_output.*.txt` | Monte Carlo inputs/outputs/errors logs |
| `Dedalo.zip` | Delivery package |

### Thonyan/

Same structure as Dedalo:

| File | Description |
|------|-------------|
| `simulacao_thonyan.ipynb` | Full flight simulation + Monte Carlo |
| `simulacao_balistica_thonyan.ipynb` | Ballistic trajectory simulation |
| `tratamento_teste.ipynb` | Static fire data processing (`500m.csv` → `teste_estatico_2_500.csv`) |
| `thonyan_data.json` / `thonyan_motor.json` | Rocket and motor parameters |
| `teste_estatico_2_500.csv` | Current official thrust curve (25/08/2026 static fire, 2 s burn) |
| `500m.csv`, `thrust_500.csv`, `motor.csv`, `drag.csv`, `poweron/off.csv` | Raw static fire data and aerodynamic/motor curves |
| `monte_carlo_thonyan_output.*.txt` | Monte Carlo logs |
| `Thonyan.zip` | Delivery package |

### SR-Couto/

Reference simulation notebook (`simulacao.ipynb`) plus motor and power on/off drag curves (`team100.pdf` contains the original design documentation).

## Workflow

1. **Static fire** — record load cell + pressure data of the motor test.
2. **Thrust curve processing** — run the folder's `tratamento_teste.ipynb` to clean, offset (t₀ = ignition), rescale (ms → s, g → N) and export the thrust CSV.
3. **Simulation** — run the main notebook (`Simulacao_dedalo.ipynb` / `simulacao_thonyan.ipynb`):
   - Environment set for the launch site (lat −21.9431°, lon −48.9541°, elev 478 m) with **GFS forecast** wind profile;
   - Rocket/motor built from the `.json` parameter files;
   - Single deterministic `Flight` run;
   - **Monte Carlo** dispersion analysis (outputs written to `monte_carlo_*_output.*.txt`).
4. **Delivery** — results are packaged into the per-rocket `.zip`.

## Requirements

- Python ≥ 3.12
- [RocketPy](https://docs.rocketpy.org/) (+ Jupyter, pandas, numpy, matplotlib)

```bash
pip install rocketpy jupyter pandas numpy matplotlib
jupyter lab   # then open any notebook
```

> Note: notebooks using GFS fetch forecast data from NOAA at runtime — an internet connection is required, and results reflect the forecast valid at the simulated date.

## Notes

- Thrust curve files are in RocketPy format: `Time(s), Thrust(N)` with t₀ at ignition.
- The ballistic notebooks simulate a no-recovery trajectory; the main notebooks include parachute/deployment events as configured per mission.
- Monte Carlo outputs are plain-text summaries written by RocketPy's `MonteCarlo` class.
