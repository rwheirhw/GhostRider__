"""
grid_environment.py — Grid State Manager & Renderer.

Responsibilities:
  • Maintain the 2D numpy grid representing the town map.
  • Procedurally generate obstacles, fire seeds, and start/end positions.
  • Implement cellular-automata fire-spread logic.
  • Render the grid, overlays (path, agent), and HUD via Pygame.

Cell State Codes (from config.py):
  0 = CLEAR   |  1 = OBSTACLE  |  2 = FIRE  |  3 = HIGH_RISK
"""

import random
from collections import deque

import numpy as np
import pygame

from config import (
    GRID_ROWS, GRID_COLS, CELL_SIZE,
    OBSTACLE_DENSITY, FIRE_SEEDS,
    FIRE_SPREAD_PROB,
    CLEAR, OBSTACLE, FIRE, HIGH_RISK,
    CLEAR_COST, HIGH_RISK_COST, INF_COST,
    COLOR_CLEAR, COLOR_OBSTACLE,
    COLOR_FIRE_A, COLOR_FIRE_B,
    COLOR_HIGH_RISK, COLOR_START, COLOR_END,
    COLOR_AGENT, COLOR_PATH, COLOR_GRID_LINE,
    PANEL_HEIGHT, COLOR_PANEL_BG, COLOR_TEXT,
    COLOR_TRAPPED_BG, COLOR_SUCCESS_BG,
    COLOR_REPLAN_FLASH,
)


class GridEnvironment:
    """
    Manages the 2D grid world for the wildfire evacuation simulation.

    Attributes:
        rows, cols : int
            Dimensions of the grid.
        grid : np.ndarray (rows x cols)
            Current state of every cell (CLEAR / OBSTACLE / FIRE / HIGH_RISK).
        start : tuple (row, col)
            Civilian's starting position.
        end : tuple (row, col)
            Safe-zone / evacuation point.
        fire_cells : set
            Fast-lookup set of all cells currently on fire.
        frame_tick : int
            Counter toggled each frame to animate fire glow.
    """

    # ------------------------------------------------------------------ #
    #  Initialisation & Map Generation
    # ------------------------------------------------------------------ #
    def __init__(self, rows: int = GRID_ROWS, cols: int = GRID_COLS):
        """Initialise the grid and generate a valid map."""
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols), dtype=int)  # All cells start CLEAR
        self.start = (0, 0)
        self.end = (rows - 1, cols - 1)
        self.fire_cells: set = set()
        self.frame_tick = 0  # Used to alternate fire colour for glow effect

        # Attempt map generation until we get one where S→E is reachable
        self.generate_map()

    # ------------------------------------------------------------------ #
    def generate_map(self):
        """
        Procedurally build the grid:
          1. Place random obstacles.
          2. Choose Start (top-left quadrant) and End (bottom-right quadrant).
          3. Seed fire in the middle band.
          4. Validate that a path from S→E exists (BFS).
        Retries automatically if the map is unsolvable.
        """
        while True:
            self.grid = np.zeros((self.rows, self.cols), dtype=int)
            self.fire_cells.clear()

            # --- Step 1: Random obstacles -----------------------------------
            for r in range(self.rows):
                for c in range(self.cols):
                    if random.random() < OBSTACLE_DENSITY:
                        self.grid[r][c] = OBSTACLE

            # --- Step 2: Place Start and End --------------------------------
            # Start in the top-left quadrant
            self.start = (
                random.randint(0, self.rows // 4),
                random.randint(0, self.cols // 4),
            )
            # End in the bottom-right quadrant
            self.end = (
                random.randint(3 * self.rows // 4, self.rows - 1),
                random.randint(3 * self.cols // 4, self.cols - 1),
            )

            # Guarantee Start and End cells are clear
            self.grid[self.start[0]][self.start[1]] = CLEAR
            self.grid[self.end[0]][self.end[1]] = CLEAR

            # Clear a small area around start and end so they aren't boxed in
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    for anchor in (self.start, self.end):
                        nr, nc = anchor[0] + dr, anchor[1] + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            self.grid[nr][nc] = CLEAR

            # --- Step 3: Seed initial fire cells ----------------------------
            fires_placed = 0
            attempts = 0
            while fires_placed < FIRE_SEEDS and attempts < 500:
                # Fire appears in the middle horizontal band of the grid
                fr = random.randint(self.rows // 4, 3 * self.rows // 4)
                fc = random.randint(self.cols // 4, 3 * self.cols // 4)
                if self.grid[fr][fc] == CLEAR:
                    self.grid[fr][fc] = FIRE
                    self.fire_cells.add((fr, fc))
                    fires_placed += 1
                attempts += 1

            # Build initial high-risk buffer around fire
            self._update_high_risk_zones()

            # --- Step 4: Validate reachability with BFS --------------------
            if self._bfs_reachable(self.start, self.end):
                break  # Map is valid — proceed

    # ------------------------------------------------------------------ #
    #  BFS Reachability Check (used during map generation only)
    # ------------------------------------------------------------------ #
    def _bfs_reachable(self, src: tuple, dst: tuple) -> bool:
        """
        Quick BFS to verify that *dst* is reachable from *src*
        treating FIRE and HIGH_RISK cells as passable (they aren't
        blocked yet at generation time — we only care about obstacles).
        """
        visited = set()
        queue = deque([src])
        visited.add(src)

        while queue:
            r, c = queue.popleft()
            if (r, c) == dst:
                return True
            for nr, nc in self._four_neighbors(r, c):
                if (nr, nc) not in visited and self.grid[nr][nc] != OBSTACLE:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return False

    # ------------------------------------------------------------------ #
    #  Fire Spread (Cellular Automata)
    # ------------------------------------------------------------------ #
    def spread_fire(self):
        """
        Expand the wildfire using a probabilistic cellular automaton:
          • For every cell currently on fire, examine its 4-directional
            neighbors.
          • If a neighbor is CLEAR or HIGH_RISK, it ignites with
            probability FIRE_SPREAD_PROB.
          • After spreading, recalculate the 1-cell high-risk buffer
            around all fire cells.

        This is the *hazard simulation* described in the project spec.
        """
        new_fires: list = []

        for (r, c) in list(self.fire_cells):
            for nr, nc in self._four_neighbors(r, c):
                cell_state = self.grid[nr][nc]
                # Fire can spread into CLEAR or HIGH_RISK cells
                if cell_state in (CLEAR, HIGH_RISK):
                    if random.random() < FIRE_SPREAD_PROB:
                        new_fires.append((nr, nc))

        # Apply all new fires (deferred to avoid mutation during iteration)
        for (r, c) in new_fires:
            self.grid[r][c] = FIRE
            self.fire_cells.add((r, c))

        # Recalculate the high-risk buffer after fire has expanded
        self._update_high_risk_zones()

    # ------------------------------------------------------------------ #
    #  High-Risk Zone Calculation
    # ------------------------------------------------------------------ #
    def _update_high_risk_zones(self):
        """
        Mark every CLEAR cell adjacent to at least one FIRE cell as
        HIGH_RISK (state 3).  Previously HIGH_RISK cells that are no
        longer adjacent to fire revert to CLEAR.

        Called after every fire-spread step.
        """
        # First, reset all existing HIGH_RISK cells to CLEAR
        high_risk_mask = self.grid == HIGH_RISK
        self.grid[high_risk_mask] = CLEAR

        # Then mark neighbors of fire cells
        for (r, c) in self.fire_cells:
            for nr, nc in self._four_neighbors(r, c):
                if self.grid[nr][nc] == CLEAR:
                    self.grid[nr][nc] = HIGH_RISK

    # ------------------------------------------------------------------ #
    #  Neighbor & Cost Queries (used by AStarRouter)
    # ------------------------------------------------------------------ #
    def get_neighbors(self, pos: tuple) -> list:
        """
        Return a list of 4-directional neighbors of *pos* that are
        within bounds and passable (not FIRE, not OBSTACLE).

        Parameters:
            pos : (row, col)

        Returns:
            List of (row, col) tuples the agent could move into.
        """
        result = []
        r, c = pos
        for nr, nc in self._four_neighbors(r, c):
            if self.is_passable((nr, nc)):
                result.append((nr, nc))
        return result

    def get_cost(self, pos: tuple) -> float:
        """
        Return the movement cost for entering cell *pos*.

        Costs:
            CLEAR     →  1   (base cost)
            HIGH_RISK → 50   (heavily penalized but passable)
            FIRE      →  ∞   (impassable)
            OBSTACLE  →  ∞   (impassable)
        """
        state = self.grid[pos[0]][pos[1]]
        if state == CLEAR:
            return CLEAR_COST
        elif state == HIGH_RISK:
            return HIGH_RISK_COST
        else:
            return INF_COST  # FIRE or OBSTACLE

    def is_passable(self, pos: tuple) -> bool:
        """Return True if the cell is neither fire nor an obstacle."""
        state = self.grid[pos[0]][pos[1]]
        return state in (CLEAR, HIGH_RISK)

    # ------------------------------------------------------------------ #
    #  Internal Helper
    # ------------------------------------------------------------------ #
    def _four_neighbors(self, r: int, c: int) -> list:
        """Return up/down/left/right neighbors within grid bounds."""
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbors.append((nr, nc))
        return neighbors

    # ================================================================== #
    #  RENDERING  (Pygame)
    # ================================================================== #
    def draw(self, surface: pygame.Surface, path: list, agent_pos: tuple,
             replan_flash: bool = False):
        """
        Render the full grid, path overlay, and agent onto the given
        Pygame surface.

        Parameters:
            surface      : Pygame display surface.
            path         : List of (row, col) cells in the planned path.
            agent_pos    : Current (row, col) of the agent.
            replan_flash : If True, tint path cells yellow to indicate replan.
        """
        self.frame_tick += 1  # Advance glow animation counter

        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE,
                                   CELL_SIZE, CELL_SIZE)
                state = self.grid[r][c]

                # --- Base cell colour ---
                if state == OBSTACLE:
                    color = COLOR_OBSTACLE
                elif state == FIRE:
                    # Alternate between two fire colours for glow effect
                    color = COLOR_FIRE_A if (self.frame_tick + r + c) % 2 == 0 \
                        else COLOR_FIRE_B
                elif state == HIGH_RISK:
                    color = COLOR_HIGH_RISK
                else:
                    color = COLOR_CLEAR

                pygame.draw.rect(surface, color, rect)

                # Subtle grid lines
                pygame.draw.rect(surface, COLOR_GRID_LINE, rect, 1)

        # --- Draw the planned path overlay ---------------------------------
        if path:
            path_color = COLOR_REPLAN_FLASH if replan_flash else COLOR_PATH
            for (r, c) in path:
                # Skip drawing path on fire/obstacle cells (stale path data)
                if self.grid[r][c] in (FIRE, OBSTACLE):
                    continue
                px = c * CELL_SIZE + CELL_SIZE // 2
                py = r * CELL_SIZE + CELL_SIZE // 2
                radius = CELL_SIZE // 4
                pygame.draw.circle(surface, path_color, (px, py), radius)

        # --- Draw Start and End markers ------------------------------------
        self._draw_marker(surface, self.start, COLOR_START, "S")
        self._draw_marker(surface, self.end, COLOR_END, "E")

        # --- Draw the Agent ------------------------------------------------
        if agent_pos:
            ax = agent_pos[1] * CELL_SIZE + CELL_SIZE // 2
            ay = agent_pos[0] * CELL_SIZE + CELL_SIZE // 2
            # Outer glow ring
            pygame.draw.circle(surface, (0, 180, 150), (ax, ay),
                               CELL_SIZE // 2, 2)
            # Inner filled circle
            pygame.draw.circle(surface, COLOR_AGENT, (ax, ay),
                               CELL_SIZE // 3)

    # ------------------------------------------------------------------ #
    def draw_hud(self, surface: pygame.Surface, steps: int, replans: int,
                 path_len: int, status: str):
        """
        Draw the heads-up display panel at the bottom of the window.

        Shows current step count, number of replans, remaining path length,
        and simulation status.
        """
        panel_y = self.rows * CELL_SIZE
        panel_rect = pygame.Rect(0, panel_y,
                                 self.cols * CELL_SIZE, PANEL_HEIGHT)
        pygame.draw.rect(surface, COLOR_PANEL_BG, panel_rect)

        font = pygame.font.SysFont("consolas", 14)

        # Status line
        status_text = font.render(
            f"Status: {status}", True, COLOR_TEXT)
        surface.blit(status_text, (10, panel_y + 5))

        # Metrics line
        metrics = (f"Steps: {steps}   |   Replans: {replans}   |   "
                   f"Path Length: {path_len}")
        metrics_text = font.render(metrics, True, COLOR_TEXT)
        surface.blit(metrics_text, (10, panel_y + 25))

        # Controls line
        controls = "SPACE=Pause  R=Restart  +/-=Speed  ESC=Quit"
        controls_text = font.render(controls, True,
                                    (140, 140, 140))
        surface.blit(controls_text, (10, panel_y + 42))

    # ------------------------------------------------------------------ #
    def draw_overlay(self, surface: pygame.Surface, text: str,
                     bg_color: tuple):
        """Draw a translucent overlay with a large centred message."""
        overlay = pygame.Surface(
            (self.cols * CELL_SIZE, self.rows * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((*bg_color, 160))  # Semi-transparent
        surface.blit(overlay, (0, 0))

        font = pygame.font.SysFont("consolas", 32, bold=True)
        label = font.render(text, True, (255, 255, 255))
        lx = (self.cols * CELL_SIZE - label.get_width()) // 2
        ly = (self.rows * CELL_SIZE - label.get_height()) // 2
        surface.blit(label, (lx, ly))

    # ------------------------------------------------------------------ #
    #  Small rendering helpers
    # ------------------------------------------------------------------ #
    def _draw_marker(self, surface: pygame.Surface, pos: tuple,
                     color: tuple, letter: str):
        """Draw a coloured square with a centred letter for S / E markers."""
        r, c = pos
        rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE,
                           CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, COLOR_GRID_LINE, rect, 1)

        font = pygame.font.SysFont("consolas", CELL_SIZE - 4, bold=True)
        label = font.render(letter, True, (255, 255, 255))
        lx = rect.x + (CELL_SIZE - label.get_width()) // 2
        ly = rect.y + (CELL_SIZE - label.get_height()) // 2
        surface.blit(label, (lx, ly))
