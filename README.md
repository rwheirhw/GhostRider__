# 🔥 Dynamic Wildfire Evacuation Router

> An AI-powered dynamic pathfinding agent that calculates the safest escape route in real-time as wildfire spreads across a simulated town grid.

**Course:** Principles of Artificial Intelligence — Unit II (Informed Search Strategies)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.6+-green?logo=pygame)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## 📋 Problem Statement

Static GPS navigation systems fail during rapidly spreading natural disasters like wildfires — they route people into danger based on outdated maps. This project solves this by implementing a **Dynamic Pathfinding Agent** that:

- Calculates the **safest and fastest** escape route using **A\* Search**
- **Dynamically replans** the route when wildfire blocks the current path
- Simulates realistic fire spread using a **probabilistic cellular automaton**

---

## 🎮 Demo

When you run the simulation, you'll see:

| Element | Visual |
|---------|--------|
| 🟩 **Start (S)** | Green cell — civilian's starting position |
| 🟦 **End (E)** | Blue cell — safe evacuation zone |
| ⬜ **Clear Path** | Off-white cells — normal walkable roads |
| ⬛ **Obstacles** | Dark charcoal cells — buildings/walls |
| 🟥 **Fire** | Animated orange-red cells — spreading wildfire |
| 🟨 **High-Risk Zone** | Amber cells — 1-cell buffer around fire |
| 🔵 **Planned Path** | Blue dots — agent's current A\* route |
| 🟢 **Agent** | Cyan-teal circle — moving civilian |

The path **visibly shifts** when the agent detects fire blocking its route and triggers a replan.

---

## 🏗️ Architecture

```
┌─────────────┐     grid state, costs     ┌──────────────┐
│   Grid      │◄────────────────────────► │   A* Router  │
│ Environment │    neighbors, passability  │  (from scratch)│
└──────┬──────┘                           └──────┬───────┘
       │                                         │
       │  render calls          optimal path     │
       ▼                                         ▼
┌──────────────────────────────────────────────────┐
│                  Simulation                       │
│  agent movement → fire spread → validate → replan │
└──────────────────────────────────────────────────┘
```

### File Structure

```
├── main.py               # Entry point
├── simulation.py          # Main loop (movement, fire timing, replanning)
├── grid_environment.py    # Grid state, fire spread, Pygame rendering
├── astar_router.py        # A* search algorithm (implemented from scratch)
├── config.py              # All tunable parameters
├── report.md              # Project report (theory & analysis)
└── requirements.txt       # Dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/wildfire-evacuation-router.git
cd wildfire-evacuation-router

# Install dependencies
pip install -r requirements.txt
```

### Run the Simulation

```bash
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| `SPACE` | Pause / Resume |
| `R` | Restart with a new random map |
| `+` / `=` | Speed up simulation |
| `-` | Slow down simulation |
| `ESC` | Quit |

---

## ⚙️ How It Works

### 1. Grid Environment (State Space)

A **40×40** 2D grid represents a town map. Each cell has a state and associated movement cost:

| State | Code | Cost | Description |
|-------|------|-----:|-------------|
| Clear | `0` | 1 | Normal walkable road |
| Obstacle | `1` | ∞ | Building/wall — impassable |
| Fire | `2` | ∞ | Active wildfire — impassable |
| High-Risk | `3` | 50 | Adjacent to fire — heavily penalized |

### 2. Fire Spread (Cellular Automaton)

Every **N** agent steps, fire expands:

```
For each cell currently on fire:
    For each 4-directional neighbor:
        If neighbor is CLEAR or HIGH_RISK:
            Ignite with probability P (default 0.4)
    
Recalculate 1-cell high-risk buffer around all fire cells
```

### 3. A\* Search Algorithm

Implemented **from scratch** — no external pathfinding libraries.

- **g(n):** Accumulated movement cost from start to node `n`
  - Clear cell = 1, High-Risk cell = 50, Fire/Obstacle = ∞
- **h(n):** Manhattan distance to the goal (admissible heuristic)
- **f(n) = g(n) + h(n):** Total estimated cost through node `n`
- **Data structures:** `heapq` min-heap (open set), `set` (closed set), `dict` (g-scores, parents)

### 4. Dynamic Replanning

```
Agent computes initial A* path from S → E
┌──────────────────────────────────────────┐
│  Loop:                                    │
│    1. Agent moves 1 step along path       │
│    2. Fire spreads (every N steps)        │
│    3. Scan remaining path for FIRE cells  │
│    4. If path is blocked → replan A*      │
│    5. If no path exists → TRAPPED         │
│    6. If goal reached → EVACUATED         │
└──────────────────────────────────────────┘
```

---

## 🔧 Configuration

All parameters are tunable in [`config.py`](config.py):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `GRID_ROWS` / `GRID_COLS` | 40 | Grid dimensions |
| `CELL_SIZE` | 16 | Pixel size per cell |
| `OBSTACLE_DENSITY` | 0.15 | Fraction of obstacle cells |
| `FIRE_SEEDS` | 3 | Initial fire ignition points |
| `FIRE_SPREAD_INTERVAL` | 3 | Fire expands every N agent steps |
| `FIRE_SPREAD_PROB` | 0.4 | Probability of fire spreading to a neighbor |
| `HIGH_RISK_COST` | 50 | Cost penalty for fire-adjacent cells |
| `FPS` | 8 | Simulation speed (frames per second) |

---

## 📊 Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|-----------------|
| Single A\* search | O(V log V) | O(V) |
| Fire spread | O(F × 4) | O(F) |
| Path validation | O(P) | O(1) |
| Full simulation | O(T × V log V) worst case | O(V) |

Where V = grid cells (1,600), F = fire cells, P = path length, T = total steps.

In practice, replans are **infrequent** — A\* is only triggered when the path is actually blocked, not every step.

---

## 📝 Project Report

See [`report.md`](report.md) for the full theoretical writeup covering:

- How **g(n)** and **h(n)** balance shortest path vs. fire avoidance
- Time complexity of continuous A\* in dynamic environments
- **PEAS** analysis and environment classification
- Why this fulfils the concept of **Intelligent Agents in a Dynamic Environment**

---

## 🧠 Key AI Concepts Demonstrated

| Concept | How It's Applied |
|---------|-----------------|
| **Informed Search (A\*)** | Heuristic-guided pathfinding with admissible Manhattan distance |
| **Dynamic Replanning** | Agent senses environment changes and recalculates |
| **Cost-based Decision Making** | High-risk zones penalized via g(n) to prefer safer routes |
| **Goal-based Agent** | Maintains internal model (path), revises when invalidated |
| **Stochastic Environment** | Fire spread is probabilistic, creating uncertainty |

---

## 📚 References

1. Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
2. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A Formal Basis for the Heuristic Determination of Minimum Cost Paths. *IEEE Transactions on SSC*, 4(2), 100–107.
3. Koenig, S. & Likhachev, M. (2002). D\* Lite. *Proceedings of AAAI*, 476–483.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built as a Capstone Project for <strong>Principles of Artificial Intelligence</strong>
</p>
