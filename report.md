# Dynamic Wildfire Evacuation Router — Project Report

## Course: Principles of Artificial Intelligence
## Focus Area: Unit II — Informed Search Strategies

---

## 1. Introduction

Static GPS navigation systems rely on pre-computed routes that do not adapt
to rapidly changing environmental hazards.  During a wildfire, a route
that was safe five minutes ago may now pass directly through an advancing
fire front.  This project addresses the problem by implementing a
**Dynamic Pathfinding Agent** that continuously recalculates the safest
escape route as the wildfire spreads across a simulated town grid.

The agent uses the **A\* Search Algorithm** — an informed search strategy
that combines actual travel cost with a heuristic estimate to find optimal
paths efficiently — and triggers **dynamic replanning** whenever the
environment changes in a way that invalidates its current route.

---

## 2. Environment Representation (State Space)

The simulation models the town as a 2D grid of size 40 × 40.  Each cell
can be in one of the following states:

| Code | State        | Movement Cost | Description                            |
|------|------------- |--------------:|----------------------------------------|
| 0    | Clear        |             1 | Normal walkable road                   |
| 1    | Obstacle     |            ∞  | Building / wall — impassable           |
| 2    | Fire         |            ∞  | Active wildfire — impassable           |
| 3    | High-Risk    |            50 | Adjacent to fire — passable but costly |

- **Start (S)**: The civilian's initial position (top-left quadrant).
- **End (E)**: The safe evacuation zone (bottom-right quadrant).
- **Fire Seeds**: Initial ignition points placed in the centre of the map.

---

## 3. How g(n) and h(n) Balance Shortest Path vs. Fire Avoidance

### 3.1  The Cost Function g(n)

`g(n)` represents the **accumulated actual cost** of travelling from the
start node to node `n` along the path discovered so far.  The cost of
each move depends on the destination cell's state:

- Moving to a **CLEAR** cell costs **1** (base cost).
- Moving to a **HIGH-RISK** cell (adjacent to fire) costs **50**.
- **FIRE** and **OBSTACLE** cells are **impassable** (cost = ∞).

This cost structure encodes the agent's *survival priorities* directly
into the search.  A path through a high-risk zone is technically valid
but fifty times more expensive per step, so A\* will strongly prefer
longer detours through safe cells over short cuts near the fire.

### 3.2  The Heuristic Function h(n)

`h(n)` is the **Manhattan distance** from node `n` to the goal:

```
h(n) = |n.row − goal.row| + |n.col − goal.col|
```

Manhattan distance is **admissible** for a 4-directional grid: it never
overestimates the true minimum cost because the agent can only move
up/down/left/right and the cheapest cell cost is 1.  Admissibility
guarantees that A\* will always find the **optimal** (lowest-cost) path.

### 3.3  The Balance: f(n) = g(n) + h(n)

The evaluation function `f(n)` blends both components:

- **g(n) steers away from danger.**  High-risk cells inflate the
  accumulated cost, causing A\* to deprioritise paths that pass near
  the fire even if they are geometrically shorter.
- **h(n) steers toward the goal.**  The heuristic ensures A\* doesn't
  aimlessly wander — it always expands the most promising node in the
  direction of the safe zone.

Together, they produce a path that is both **short** (thanks to h)
and **safe** (thanks to the cost penalties in g).  When the fire
advances and creates new high-risk zones, the replanned path will
automatically route around them because the g-costs of those cells
have increased.

---

## 4. Time Complexity Analysis

### 4.1  Single A\* Invocation

For a grid with `V` cells and branching factor `b` (at most 4 for
a 4-directional grid):

- **Worst-case time**: O(V log V), where the log V factor comes from
  the priority queue (min-heap) operations.  In a 40×40 grid,
  V = 1 600, so each A\* call is very fast.
- **Space**: O(V) for the open set, closed set, and g-score table.

### 4.2  Repeated A\* in a Dynamic Environment

The agent does **not** run A\* every single step.  It only replans
when the remaining path is detected to intersect newly created FIRE
or HIGH\_RISK cells.  In the worst case (fire spreads every step and
always blocks the path), A\* is re-invoked every step, giving a
total cost of O(T × V log V) where T is the number of steps.

In practice, replans are infrequent — the path is validated with a
simple O(P) scan (P = remaining path length), and A\* is only triggered
on failure.  This makes the approach efficient for real-time simulation.

### 4.3  Comparison with D\* Lite

A more sophisticated approach is **D\* Lite**, which incrementally
repairs the previous search tree rather than computing from scratch.
However, A\* replanning is chosen here for **pedagogical clarity**: it
directly demonstrates the core concepts of informed search, heuristic
design, and intelligent adaptation without the complexity of
incremental graph repair.

---

## 5. Intelligent Agents in a Dynamic Environment

### 5.1  PEAS Description

| Component       | Description                                         |
|-----------------|-----------------------------------------------------|
| **Performance** | Reach the safe zone in minimum cost; avoid fire     |
| **Environment** | 40×40 grid with spreading wildfire                  |
| **Actuators**   | Movement in 4 directions (up, down, left, right)    |
| **Sensors**     | Full grid visibility (cell states, fire locations)  |

### 5.2  Environment Properties

| Property              | Classification     | Rationale                                   |
|-----------------------|--------------------|---------------------------------------------|
| Observable            | Fully observable   | Agent sees the entire grid state             |
| Deterministic         | Stochastic         | Fire spread is probabilistic                 |
| Episodic/Sequential   | Sequential         | Each move affects future options              |
| Static/Dynamic        | Dynamic            | Fire spreads independently of agent actions  |
| Discrete/Continuous   | Discrete           | Grid cells, discrete time steps              |
| Single/Multi-agent    | Single agent       | One civilian evacuating                      |

### 5.3  Why This Fulfils "Intelligent Agents" Curriculum Requirements

The agent exhibits **intelligent behaviour** as defined in standard AI
textbooks (Russell & Norvig):

1. **Rationality**: The agent selects the action (next cell) that
   maximises its performance measure (reaching the goal at minimum
   cost) given its current knowledge of the environment.

2. **Adaptiveness**: Unlike a simple reflex agent, this agent
   maintains an internal model (the planned path) and revises it
   when the environment changes — this is characteristic of a
   **model-based, goal-based agent**.

3. **Informed Search**: The use of A\* with an admissible heuristic
   demonstrates how domain knowledge (Manhattan distance) can
   dramatically reduce the search space compared to uninformed
   strategies like BFS or DFS.

4. **Dynamic Replanning**: The replan-on-invalidation loop directly
   embodies the concept of an agent operating in a **dynamic,
   stochastic environment** — it cannot compute a single plan and
   execute it blindly; it must continuously sense, evaluate, and act.

---

## 6. Conclusion

This project demonstrates how the A\* search algorithm — augmented with
risk-aware cost functions and dynamic replanning — can serve as the
decision-making core of an intelligent evacuation agent.  The simulation
shows that informed search strategies are not merely academic constructs
but practical tools that can be applied to life-safety problems in
dynamic, uncertain environments.

---

## 7. References

1. Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern
   Approach* (4th ed.). Pearson. — Chapters 3–4 (Search Strategies,
   Informed Search, Heuristic Functions).
2. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A Formal Basis
   for the Heuristic Determination of Minimum Cost Paths. *IEEE
   Transactions on Systems Science and Cybernetics*, 4(2), 100–107.
3. Koenig, S. & Likhachev, M. (2002). D\* Lite. *Proceedings of the
   AAAI Conference on Artificial Intelligence*, 476–483.
