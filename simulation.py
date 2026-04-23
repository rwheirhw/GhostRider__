"""
Main simulation loop for dynamic replanning with A* while fire spreads.
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
    """Orchestrates grid updates, agent movement, replanning, and rendering."""

    def __init__(self):
        pygame.init()

        self.win_w = GRID_COLS * CELL_SIZE
        self.win_h = GRID_ROWS * CELL_SIZE + PANEL_HEIGHT

        self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        pygame.display.set_caption("Dynamic Wildfire Evacuation Router — A* Pathfinding")
        self.clock = pygame.time.Clock()

        self._reset()

    def _reset(self):
        self.grid = GridEnvironment(GRID_ROWS, GRID_COLS)
        self.router = AStarRouter(self.grid)

        self.agent_pos = self.grid.start
        self.path = self.router.find_path(self.agent_pos, self.grid.end)
        self.path_index = 1

        self.step = 0
        self.replans = 0
        self.fps = FPS
        self.paused = False
        self.finished = False
        self.replan_flash = False
        self.status = "Navigating..."

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)

            if not self.paused and not self.finished:
                self._tick()

            self._render()
            self.clock.tick(self.fps)

    def _tick(self):
        self.replan_flash = False

        if self.path and self.path_index < len(self.path):
            self.agent_pos = self.path[self.path_index]
            self.path_index += 1
            self.step += 1
        elif self.path is None:
            self.status = "TRAPPED — No escape route!"
            self.finished = True
            return

        if self.agent_pos == self.grid.end:
            self.status = "EVACUATED — Reached Safe Zone!"
            self.finished = True
            return

        if self.step % FIRE_SPREAD_INTERVAL == 0:
            self.grid.spread_fire()

        self._check_and_replan()

    def _check_and_replan(self):
        needs_replan = self.path is None

        if not needs_replan and self.path:
            for (r, c) in self.path[self.path_index:]:
                cell = self.grid.grid[r][c]
                if cell in (FIRE, HIGH_RISK):
                    needs_replan = True
                    break

        if not needs_replan:
            return

        self.replans += 1
        self.replan_flash = True
        new_path = self.router.find_path(self.agent_pos, self.grid.end)

        if new_path is None:
            self.path = None
            self.status = "TRAPPED — No escape route!"
            self.finished = True
            return

        self.path = new_path
        self.path_index = 1
        self.status = f"Replanned! (replan #{self.replans})"

    def _handle_key(self, key):
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_r:
            self._reset()
        elif key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self.fps = min(self.fps + 2, MAX_FPS)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.fps = max(self.fps - 2, MIN_FPS)

    def _render(self):
        self.screen.fill(COLOR_PANEL_BG)

        remaining_path = self.path[self.path_index:] if self.path else []
        self.grid.draw(self.screen, remaining_path, self.agent_pos, replan_flash=self.replan_flash)

        path_len = len(remaining_path) if remaining_path else 0
        display_status = "PAUSED" if (self.paused and not self.finished) else self.status
        self.grid.draw_hud(self.screen, self.step, self.replans, path_len, display_status)

        if self.finished:
            if "TRAPPED" in self.status:
                self.grid.draw_overlay(self.screen, "TRAPPED — No Escape!", COLOR_TRAPPED_BG)
            elif "EVACUATED" in self.status:
                self.grid.draw_overlay(self.screen, "EVACUATED SAFELY!", COLOR_SUCCESS_BG)

        pygame.display.flip()