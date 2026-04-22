"""
simulation.py — Main Simulation Controller.

Orchestrates the interaction between the GridEnvironment (state + fire)
and the AStarRouter (pathfinding).  Handles:
  • Agent movement along the planned path.
  • Periodic fire spread.
  • Dynamic path-validity checks and replanning.
  • Pygame event loop, rendering, and user controls.

Controls:
  SPACE  — Pause / Resume
  R      — Restart with a new random map
  +  / = — Increase simulation speed
  -      — Decrease simulation speed
  ESC    — Quit
"""

import sys
import pygame

from config import (
    GRID_ROWS, GRID_COLS, CELL_SIZE,
    PANEL_HEIGHT, FPS, MIN_FPS, MAX_FPS,
    FIRE_SPREAD_INTERVAL,
    FIRE, HIGH_RISK,
    COLOR_PANEL_BG, COLOR_TRAPPED_BG, COLOR_SUCCESS_BG,
)
from grid_environment import GridEnvironment
from astar_router import AStarRouter


class Simulation:
    """
    Top-level simulation loop.

    Lifecycle:
      1. Generate a grid and compute the initial A* path.
      2. Each frame:
         a. Move the agent one step.
         b. Potentially spread fire.
         c. Validate the remaining path; replan if blocked.
         d. Render everything.
      3. End when the agent reaches the safe zone or is trapped.

    Attributes:
        grid     : GridEnvironment
        router   : AStarRouter
        agent_pos: (row, col) — agent's current position
        path     : list of (row, col) — current planned route
        step     : int — total steps the agent has taken
        replans  : int — how many times A* was re-invoked
        fps      : int — current frames per second
        paused   : bool
        finished : bool
        status   : str — human-readable status for the HUD
    """

    def __init__(self):
        """Set up Pygame, generate the grid, and find the first path."""
        pygame.init()

        # Window dimensions
        self.win_w = GRID_COLS * CELL_SIZE
        self.win_h = GRID_ROWS * CELL_SIZE + PANEL_HEIGHT

        self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        pygame.display.set_caption(
            "Dynamic Wildfire Evacuation Router — A* Pathfinding")
        self.clock = pygame.time.Clock()

        # Initialise simulation state
        self._reset()

    # ------------------------------------------------------------------ #
    #  Reset / Restart
    # ------------------------------------------------------------------ #
    def _reset(self):
        """Create a fresh grid, router, and initial path."""
        self.grid = GridEnvironment(GRID_ROWS, GRID_COLS)
        self.router = AStarRouter(self.grid)

        self.agent_pos = self.grid.start
        self.path = self.router.find_path(self.agent_pos, self.grid.end)
        self.path_index = 1  # Index 0 is the start cell — agent is there

        self.step = 0
        self.replans = 0
        self.fps = FPS
        self.paused = False
        self.finished = False
        self.replan_flash = False   # True for one frame after a replan
        self.status = "Navigating..."

    # ------------------------------------------------------------------ #
    #  Main Loop
    # ------------------------------------------------------------------ #
    def run(self):
        """
        Pygame main loop.  Runs until the user quits.

        Each iteration:
          1. Handle input events.
          2. If not paused/finished, advance the simulation one tick.
          3. Render the frame.
        """
        while True:
            # --- Event Handling -----------------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)

            # --- Simulation Tick ----------------------------------------
            if not self.paused and not self.finished:
                self._tick()

            # --- Render -------------------------------------------------
            self._render()
            self.clock.tick(self.fps)

    # ------------------------------------------------------------------ #
    #  Simulation Tick (one agent step)
    # ------------------------------------------------------------------ #
    def _tick(self):
        """
        Advance the simulation by one agent step.

        Order of operations:
          1. Move the agent along the current path.
          2. Check for goal arrival.
          3. Spread fire (every FIRE_SPREAD_INTERVAL steps).
          4. Validate the remaining path.
          5. Replan if the path is blocked or lost.
        """
        self.replan_flash = False  # Reset flash each tick

        # ---- 1. Move the agent ----------------------------------------
        if self.path and self.path_index < len(self.path):
            self.agent_pos = self.path[self.path_index]
            self.path_index += 1
            self.step += 1
        elif self.path is None:
            # No path at all — agent is trapped
            self.status = "TRAPPED — No escape route!"
            self.finished = True
            return

        # ---- 2. Goal check --------------------------------------------
        if self.agent_pos == self.grid.end:
            self.status = "EVACUATED — Reached Safe Zone!"
            self.finished = True
            return

        # ---- 3. Fire spread -------------------------------------------
        if self.step % FIRE_SPREAD_INTERVAL == 0:
            self.grid.spread_fire()

        # ---- 4 & 5. Validate path & replan if needed ------------------
        self._check_and_replan()

    # ------------------------------------------------------------------ #
    #  Path Validation & Dynamic Replanning
    # ------------------------------------------------------------------ #
    def _check_and_replan(self):
        """
        Inspect every cell remaining on the planned path.  If *any* cell
        has become FIRE or HIGH_RISK (newly dangerous), trigger a full
        A* replan from the agent's current position.

        This is the **dynamic replanning** mechanism: the agent doesn't
        blindly follow a stale path — it detects environmental changes
        and recalculates.
        """
        needs_replan = False

        if self.path is None:
            needs_replan = True
        else:
            # Check each future cell on the path
            remaining = self.path[self.path_index:]
            for (r, c) in remaining:
                cell = self.grid.grid[r][c]
                if cell == FIRE:
                    # Path goes through fire — definitely blocked
                    needs_replan = True
                    break
                elif cell == HIGH_RISK:
                    # Path goes through a newly high-risk zone — replan
                    # to find a potentially cheaper/safer route
                    needs_replan = True
                    break

        if needs_replan:
            self.replans += 1
            self.replan_flash = True  # Visual indicator
            new_path = self.router.find_path(self.agent_pos, self.grid.end)

            if new_path is None:
                # No viable route exists — agent is trapped
                self.path = None
                self.status = "TRAPPED — No escape route!"
                self.finished = True
            else:
                self.path = new_path
                self.path_index = 1  # Start moving along the new path
                self.status = f"Replanned! (replan #{self.replans})"

    # ------------------------------------------------------------------ #
    #  Input Handling
    # ------------------------------------------------------------------ #
    def _handle_key(self, key):
        """Process a single key-press event."""
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_r:
            self._reset()
        elif key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self.fps = min(self.fps + 2, MAX_FPS)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.fps = max(self.fps - 2, MIN_FPS)

    # ------------------------------------------------------------------ #
    #  Rendering
    # ------------------------------------------------------------------ #
    def _render(self):
        """Draw the grid, path, agent, HUD, and any end-state overlays."""
        self.screen.fill(COLOR_PANEL_BG)

        # Remaining path for visualization
        remaining_path = []
        if self.path:
            remaining_path = self.path[self.path_index:]

        # Draw the grid world
        self.grid.draw(self.screen, remaining_path, self.agent_pos,
                       replan_flash=self.replan_flash)

        # Draw the HUD panel
        path_len = len(remaining_path) if remaining_path else 0
        display_status = self.status
        if self.paused and not self.finished:
            display_status = "PAUSED"
        self.grid.draw_hud(self.screen, self.step, self.replans,
                           path_len, display_status)

        # End-state overlays
        if self.finished:
            if "TRAPPED" in self.status:
                self.grid.draw_overlay(
                    self.screen, "TRAPPED — No Escape!", COLOR_TRAPPED_BG)
            elif "EVACUATED" in self.status:
                self.grid.draw_overlay(
                    self.screen, "EVACUATED SAFELY!", COLOR_SUCCESS_BG)

        pygame.display.flip()
