"""
Grid world state, fire spread, and Pygame rendering.
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
    """Owns the grid state and rendering helpers for the simulation."""

    def __init__(self, rows: int = GRID_ROWS, cols: int = GRID_COLS):
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols), dtype=int)
        self.start = (0, 0)
        self.end = (rows - 1, cols - 1)
        self.fire_cells: set = set()
        self.frame_tick = 0

        # Retry until start→end is reachable (ignoring fire/high-risk).
        self.generate_map()

    def generate_map(self):
        """Generate obstacles, start/end, initial fires, and validate reachability."""
        while True:
            self.grid = np.zeros((self.rows, self.cols), dtype=int)
            self.fire_cells.clear()

            for r in range(self.rows):
                for c in range(self.cols):
                    if random.random() < OBSTACLE_DENSITY:
                        self.grid[r][c] = OBSTACLE

            self.start = (
                random.randint(0, self.rows // 4),
                random.randint(0, self.cols // 4),
            )
            self.end = (
                random.randint(3 * self.rows // 4, self.rows - 1),
                random.randint(3 * self.cols // 4, self.cols - 1),
            )

            self.grid[self.start[0]][self.start[1]] = CLEAR
            self.grid[self.end[0]][self.end[1]] = CLEAR

            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    for anchor in (self.start, self.end):
                        nr, nc = anchor[0] + dr, anchor[1] + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            self.grid[nr][nc] = CLEAR

            fires_placed = 0
            attempts = 0
            while fires_placed < FIRE_SEEDS and attempts < 500:
                fr = random.randint(self.rows // 4, 3 * self.rows // 4)
                fc = random.randint(self.cols // 4, 3 * self.cols // 4)
                if self.grid[fr][fc] == CLEAR:
                    self.grid[fr][fc] = FIRE
                    self.fire_cells.add((fr, fc))
                    fires_placed += 1
                attempts += 1

            self._update_high_risk_zones()

            if self._bfs_reachable(self.start, self.end):
                break

    def _bfs_reachable(self, src: tuple, dst: tuple) -> bool:
        """Reachability check that treats everything except obstacles as passable."""
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

    def spread_fire(self):
        """Probabilistically ignite neighbors, then rebuild the high-risk buffer."""
        new_fires: list = []

        for (r, c) in list(self.fire_cells):
            for nr, nc in self._four_neighbors(r, c):
                if self.grid[nr][nc] in (CLEAR, HIGH_RISK) and random.random() < FIRE_SPREAD_PROB:
                    new_fires.append((nr, nc))

        for (r, c) in new_fires:
            self.grid[r][c] = FIRE
            self.fire_cells.add((r, c))

        self._update_high_risk_zones()

    def _update_high_risk_zones(self):
        """Maintain a 1-cell buffer of HIGH_RISK around FIRE."""
        self.grid[self.grid == HIGH_RISK] = CLEAR

        for (r, c) in self.fire_cells:
            for nr, nc in self._four_neighbors(r, c):
                if self.grid[nr][nc] == CLEAR:
                    self.grid[nr][nc] = HIGH_RISK

    def get_neighbors(self, pos: tuple) -> list:
        """4-neighbor moves that are currently passable."""
        result = []
        r, c = pos
        for nr, nc in self._four_neighbors(r, c):
            if self.is_passable((nr, nc)):
                result.append((nr, nc))
        return result

    def get_cost(self, pos: tuple) -> float:
        state = self.grid[pos[0]][pos[1]]
        if state == CLEAR:
            return CLEAR_COST
        if state == HIGH_RISK:
            return HIGH_RISK_COST
        return INF_COST

    def is_passable(self, pos: tuple) -> bool:
        state = self.grid[pos[0]][pos[1]]
        return state in (CLEAR, HIGH_RISK)

    def _four_neighbors(self, r: int, c: int) -> list:
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbors.append((nr, nc))
        return neighbors

    def draw(self, surface: pygame.Surface, path: list, agent_pos: tuple,
             replan_flash: bool = False):
        """Draw grid cells, then overlays (path, markers, agent)."""
        self.frame_tick += 1

        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                state = self.grid[r][c]

                if state == OBSTACLE:
                    pygame.draw.rect(surface, COLOR_CLEAR, rect)
                    inner_rect = rect.inflate(-4, -4)
                    pygame.draw.rect(surface, COLOR_OBSTACLE, inner_rect, border_radius=4)
                elif state == FIRE:
                    pygame.draw.rect(surface, COLOR_CLEAR, rect)
                    color = COLOR_FIRE_A if (self.frame_tick + r + c) % 2 == 0 else COLOR_FIRE_B
                    pygame.draw.circle(surface, color, rect.center, CELL_SIZE // 2 - 2)
                elif state == HIGH_RISK:
                    pygame.draw.rect(surface, COLOR_HIGH_RISK, rect)
                else:
                    pygame.draw.rect(surface, COLOR_CLEAR, rect)

                if state != OBSTACLE:
                    pygame.draw.rect(surface, COLOR_GRID_LINE, rect, 1)

        if path:
            path_color = COLOR_REPLAN_FLASH if replan_flash else COLOR_PATH

            points = []
            for (r, c) in path:
                if self.grid[r][c] not in (FIRE, OBSTACLE):
                    px = c * CELL_SIZE + CELL_SIZE // 2
                    py = r * CELL_SIZE + CELL_SIZE // 2
                    points.append((px, py))

            if len(points) > 1:
                pygame.draw.lines(surface, path_color, False, points, width=3)

            for (px, py) in points:
                radius = max(2, CELL_SIZE // 6)
                pygame.draw.circle(surface, path_color, (px, py), radius)

        self._draw_marker(surface, self.start, COLOR_START, "S")
        self._draw_marker(surface, self.end, COLOR_END, "E")

        if agent_pos:
            ax = agent_pos[1] * CELL_SIZE + CELL_SIZE // 2
            ay = agent_pos[0] * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(surface, COLOR_START, (ax, ay), int(CELL_SIZE * 0.45), 2)
            pygame.draw.circle(surface, COLOR_AGENT, (ax, ay), int(CELL_SIZE * 0.25))

    def draw_hud(self, surface: pygame.Surface, steps: int, replans: int,
                 path_len: int, status: str):
        """Bottom panel with status + basic metrics."""
        panel_y = self.rows * CELL_SIZE
        panel_rect = pygame.Rect(0, panel_y, self.cols * CELL_SIZE, PANEL_HEIGHT)
        pygame.draw.rect(surface, COLOR_PANEL_BG, panel_rect)
        pygame.draw.line(surface, COLOR_OBSTACLE, (0, panel_y), (self.cols * CELL_SIZE, panel_y), 2)

        font = pygame.font.SysFont("segoe ui", 16, bold=True)
        small_font = pygame.font.SysFont("segoe ui", 12)

        status_color = COLOR_SUCCESS_BG if "EVACUATED" in status else (
            COLOR_TRAPPED_BG if "TRAPPED" in status else COLOR_PATH
        )

        status_text = font.render(f"STATUS » {status}", True, status_color)
        surface.blit(status_text, (10, panel_y + 10))

        metrics = f"STEPS: {steps}   |   REPLANS: {replans}   |   PATH: {path_len}"
        metrics_text = small_font.render(metrics, True, COLOR_TEXT)
        surface.blit(metrics_text, (10, panel_y + 35))

        controls = "SPACE=Pause  R=Restart  +/-=Speed  ESC=Quit"
        controls_text = font.render(controls, True, (255, 255, 255))
        surface.blit(controls_text, (10, panel_y + 55))

    def draw_overlay(self, surface: pygame.Surface, text: str, bg_color: tuple):
        """Centered end-state overlay."""
        overlay = pygame.Surface((self.cols * CELL_SIZE, self.rows * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((*bg_color, 200))
        surface.blit(overlay, (0, 0))

        font = pygame.font.SysFont("segoe ui black", 36, bold=False)
        label = font.render(text, True, (255, 255, 255))
        lx = (self.cols * CELL_SIZE - label.get_width()) // 2
        ly = (self.rows * CELL_SIZE - label.get_height()) // 2

        shadow_label = font.render(text, True, (10, 10, 20))
        surface.blit(shadow_label, (lx + 2, ly + 2))
        surface.blit(label, (lx, ly))

    def _draw_marker(self, surface: pygame.Surface, pos: tuple,
                     color: tuple, letter: str):
        """Start/end cell marker."""
        r, c = pos
        rect = pygame.Rect(c * CELL_SIZE + 2, r * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.rect(surface, color, rect, border_radius=6)
        pygame.draw.rect(surface, (255, 255, 255), rect, width=2, border_radius=6)

        font = pygame.font.SysFont("segoe ui", int(CELL_SIZE * 0.7), bold=True)
        label = font.render(letter, True, (20, 20, 20))
        lx = rect.x + (rect.width - label.get_width()) // 2
        ly = rect.y + (rect.height - label.get_height()) // 2
        surface.blit(label, (lx, ly))