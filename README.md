## Constraint Based Route Planning for Autonomous Drone Missions

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![PyVista](https://img.shields.io/badge/Visualization-PyVista-green)](https://pyvista.org)
[![License](https://img.shields.io/github/license/swetha-arul/constraint-based-drone-route-planner)](LICENSE)

A 3D constraint-based drone mission planner that prioritizes **safe, feasible routes** over shortest-path solutions — navigating dynamic obstacles, no-fly zones, weather hazards, and battery constraints in a 3D grid environment.

---

<img src="https://github.com/user-attachments/assets/a25db945-84d2-4212-a498-2091b5a54382" width="700"/>

> *Drone mid-flight — green spline shows the planned route, cyan trail shows path already covered*

---

## ✨ Features

- **3D A\* pathfinding** with battery-aware cost pruning — routes that exceed battery capacity are never explored
- **Dynamic obstacle avoidance** — click to place obstacles mid-flight and watch the drone replan in real time
- **No-fly zone enforcement** — cuboid restricted airspace regions baked into the grid at mission start
- **Weather system** — rain, wind, and storm zones each add energy penalties; rain is visualized as animated falling particles
- **Payload-aware battery model** — heavier payloads increase energy cost per step; altitude changes adjust cost asymmetrically (climbing costs more than descending)
- **Preflight authorization** — GO/NO-GO decision gate before the mission starts, checking route validity and mission budget
- **Live battery visualizer** — drone color shifts green → yellow → red as battery depletes; terminal bar tracks percentage in real time
- **Mission recovery** — automatic replanning on obstacle detection with a flat energy penalty for the replanning event itself

---

## 📁 Project Structure

```
constraint-based-drone-route-planner/
├── src/
│   ├── main.py                        # Entry point — mission setup and orchestration
│   ├── battery/
│   │   └── battery_model.py           # Energy cost model (distance × payload × altitude × weather)
│   ├── decision/
│   │   └── preflight_checker.py       # GO/NO-GO mission authorization gate
│   ├── environment/
│   │   ├── grid.py                    # 3D numpy grid — FREE / OBSTACLE / NO_FLY cells
│   │   └── constraints.py             # Cuboid no-fly zone helper
│   ├── planner/
│   │   └── planner.py                 # Battery-constrained 3D A* planner
│   ├── recovery/
│   │   └── replanner.py               # Replan-or-return-home recovery logic
│   ├── validation/
│   │   └── route_validator.py         # Post-plan route legality checker
│   ├── visualization/
│   │   └── simulator.py               # PyVista 3D simulation + interaction loop
│   └── weather/
│       └── weather_model.py           # Randomized rain / wind / storm zone generator
```

---

## 🗺️ How It Works

### 1. Environment Setup

A `20 × 20 × 10` voxel grid is initialized. A cuboid no-fly zone is carved out at grid coordinates `(10,10,2) → (12,12,5)`. The simulator then procedurally generates 30 buildings and 20 trees, each registering their cells as obstacles in the live grid.



---

### 2. Weather Generation

Five weather zones are placed randomly across the grid each run:

| Type  | Penalty per step | Visual |
|-------|-----------------|--------|
| Rain  | +2              | Animated falling blue particles |
| Wind  | +4              | — |
| Storm | +8              | — |

The planner routes around high-cost weather zones when battery budget allows.



---

### 3. Planning (Battery-Constrained A\*)

The `GridPlanner` runs A\* over the 3D grid. Each neighbor expansion checks:

```
tentative_g = g_cost[current] + movement_cost + weather_cost
if tentative_g > battery_capacity → skip (prune)
```

Movement cost factors in Euclidean distance, payload weight, altitude direction, and weather. Any path that would exceed the battery budget is never expanded — the planner only returns routes the drone can actually complete.



---

### 4. Preflight Check

Before the simulator starts, a `PreflightChecker` runs a GO/NO-GO gate:

1. **Route exists** — planner returned a non-empty path
2. **Route is legal** — every cell is in-bounds, not an obstacle, not a no-fly zone
3. **Mission budget** — path length is within `max_route_length = 500`

If any check fails, the mission is aborted with a typed reason before takeoff.

---

### 5. Simulation Loop

The drone steps along the planned path one cell at a time. On each step:

- Energy is deducted using the battery model
- The drone sphere color updates (green → yellow → red)
- A cyan trail is drawn behind the drone
- Rain particles animate downward and reset at the top

On each step, a 2-cell lookahead checks for newly placed obstacles. If one is detected:
- A flat `10.0` energy replanning penalty is deducted
- The planner is called from the current position to the goal
- The new path replaces the old one and the green spline updates

<img src = "https://github.com/user-attachments/assets/deeb7416-7a92-429f-b195-70143fb9c4aa" width="700"/>

> *Red obstacle placed mid-flight — drone detects it ahead and recalculates a new route around it*

---

### 6. Battery Visualization

```
🔋 Battery: [████████████--------] 62.3%
```

The terminal bar updates every step. The drone mesh also changes color:

| Battery %  | Drone color |
|-----------|-------------|
| > 60%     | 🟢 Green   |
| 30–60%    | 🟡 Yellow  |
| < 30%     | 🔴 Red     |
| < 10%     | Mission aborted |

<img src="https://github.com/user-attachments/assets/739e5b77-a41a-4325-8466-00a4803e8bd1" width="400"/>

> *Terminal output — step-by-step energy usage and live battery bar*

---

## 🚀 Getting Started

### Requirements

```
Python 3.9+
numpy
pyvista
```

Install dependencies:

```bash
pip install numpy pyvista
```

### Run

```bash
python -m src.main
```

You will be prompted:

```
📦 Enter payload weight (kg): 3
🔋 Enter battery capacity: 300
```

**Payload guide:**
- `≤ 5 kg` — ✅ Safe payload
- `5–15 kg` — ⚠️ Medium payload, higher consumption
- `> 15 kg` — ❌ Heavy payload, risk of mission failure

Once the simulation window opens, **right-click on the grid** to place a red obstacle tower. The drone will detect it and replan automatically.

> ⚠️ **For accurate obstacle placement, view the simulation from directly above (top-down).** The click-to-grid mapping uses the mouse pointer's X/Y position and ignores Z depth — if you click from an angled perspective, the obstacle may be placed at the wrong grid cell due to Z-axis misalignment.

---

## ⚙️ Configuration

All core parameters are set in `src/main.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Grid size | `20 × 20 × 10` | Voxel environment dimensions |
| Start | `(0, 0, 2)` | Drone start position |
| Goal | `(19, 19, 3)` | Mission target |
| No-fly zone | `(10,10,2) → (12,12,5)` | Cuboid restricted airspace |
| Max route length | `500` | Preflight budget check |
| Replan penalty | `10.0` | Flat energy cost per replanning event |

---

## 🧩 Module Reference

### `BatteryModel`
Computes per-step energy cost:
```
cost = distance × (1 + payload × 0.4) × altitude_factor × weather_factor
```
- Climbing (`dz > 0`): `altitude_factor = 2.5`
- Descending (`dz < 0`): `altitude_factor = 0.8`
- Level flight: `altitude_factor = 1.0`

### `GridPlanner`
Battery-constrained 3D A\* — any path whose cumulative cost exceeds `battery_capacity` is pruned. Heuristic mirrors the cost model for admissibility.

### `RouteValidator`
Takes a grid snapshot and checks every waypoint: in-bounds, not `OBSTACLE`, not `NO_FLY`. Used by `PreflightChecker` and can be called mid-mission for live validation.

### `PreflightChecker`
Returns a `PreflightResult` with `decision = GO | NO_GO` and a typed `PreflightRejectReason`. Call `result.approved()` for a simple boolean check.

### `WeatherModel`
Generates 5 random zones per run (2 rain, 2 wind, 1 storm). `cost(pos)` returns the summed penalty for any zones whose radius contains that position.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.









