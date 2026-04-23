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

from pathlib import Path
import os
import sys


def _ensure_runtime():
    """Re-launch through the repo virtual environment when pygame is missing."""
    try:
        import pygame  # noqa: F401
        return
    except ModuleNotFoundError:
        venv_python = Path(__file__).with_name(".venv") / "Scripts" / "python.exe"
        if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
            os.execv(str(venv_python), [str(venv_python), str(Path(__file__)), *sys.argv[1:]])

        raise SystemExit(
            "pygame is not installed for this Python interpreter. "
            "Run `py -m venv .venv` and `.venv\\Scripts\\Activate.ps1`, then `pip install -r requirements.txt`."
        )


_ensure_runtime()

from simulation import Simulation


def main():
    """Create and run the wildfire evacuation simulation."""
    sim = Simulation()
    sim.run()


if __name__ == "__main__":
    main()
