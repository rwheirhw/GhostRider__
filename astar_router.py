"""
A* pathfinding for GridEnvironment.
"""

import heapq


class AStarRouter:
    """A* search on a 2D grid using GridEnvironment for neighbors and costs."""

    def __init__(self, grid_env):
        self.grid_env = grid_env

    @staticmethod
    def heuristic(a: tuple, b: tuple) -> int:
        """Manhattan distance (admissible for 4-neighbor grids)."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, start: tuple, goal: tuple) -> list | None:
        counter = 0
        open_set: list = []
        heapq.heappush(open_set, (0, counter, start))

        came_from: dict = {}
        g_score: dict = {start: 0}
        f_score: dict = {start: self.heuristic(start, goal)}
        closed_set: set = set()

        while open_set:
            current_f, _, current = heapq.heappop(open_set)

            if current in closed_set:
                continue

            if current == goal:
                return self._reconstruct_path(came_from, current)

            closed_set.add(current)

            for neighbor in self.grid_env.get_neighbors(current):
                if neighbor in closed_set:
                    continue

                move_cost = self.grid_env.get_cost(neighbor)
                tentative_g = g_score[current] + move_cost

                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor, goal)
                    f_score[neighbor] = f

                    # Tie-break to keep heap ordering deterministic for equal f.
                    counter += 1
                    heapq.heappush(open_set, (f, counter, neighbor))

        return None

    @staticmethod
    def _reconstruct_path(came_from: dict, current: tuple) -> list:
        """Rebuild path by walking parents from goal back to start."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path