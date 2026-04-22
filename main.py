"""
main.py — Entry Point for the Dynamic Wildfire Evacuation Router.

Run this file to launch the simulation:
    python main.py

The simulation will:
  1. Generate a random 40×40 town grid with obstacles and fire seeds.
  2. Compute an initial A* path from Start to the Safe Zone.
  3. Animate the agent moving along the path while wildfire spreads.
  4. Dynamically replan the route whenever fire blocks the path.

Controls:
  SPACE  — Pause / Resume
  R      — Restart with a new random map
  +/-    — Adjust simulation speed
  ESC    — Quit
"""

from simulation import Simulation


def main():
    """Create and run the wildfire evacuation simulation."""
    sim = Simulation()
    sim.run()


if __name__ == "__main__":
    main()
