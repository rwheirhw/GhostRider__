"""
astar_router.py — A* Pathfinding Algorithm (Implemented from Scratch).

This module contains the AStarRouter class, which finds the optimal
(lowest-cost) path from a start cell to a goal cell on the GridEnvironment.

Key Concepts:
  • g(n) — the accumulated movement cost from the start node to node n.
  • h(n) — the heuristic estimate of the cost from node n to the goal
            (Manhattan distance, which is admissible on a 4-directional grid).
  • f(n) = g(n) + h(n) — the estimated total cost through node n.

The algorithm uses Python's built-in `heapq` (a min-heap) as the priority
queue.  No external pathfinding libraries are used.
"""

import heapq


class AStarRouter:
    """
    Implements the A* search algorithm for pathfinding on a 2D grid.

    The router queries the GridEnvironment for neighbor lists and movement
    costs, keeping the pathfinding logic completely decoupled from the
    environment representation.

    Attributes:
        grid_env : GridEnvironment
            Reference to the grid world (provides neighbors, costs).
    """

    def __init__(self, grid_env):
        """
        Initialise the router with a reference to the grid environment.

        Parameters:
            grid_env : GridEnvironment
                The grid object that exposes get_neighbors() and get_cost().
        """
        self.grid_env = grid_env

    # ------------------------------------------------------------------ #
    #  Heuristic Function  h(n)
    # ------------------------------------------------------------------ #
    @staticmethod
    def heuristic(a: tuple, b: tuple) -> int:
        """
        Compute the Manhattan distance between cells *a* and *b*.

        Manhattan distance is |Δrow| + |Δcol|.  It is an *admissible*
        heuristic for 4-directional grids because the shortest possible
        path can never be shorter than the straight-line grid distance.

        Parameters:
            a : (row, col)
            b : (row, col)

        Returns:
            int — the Manhattan distance.
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # ------------------------------------------------------------------ #
    #  Core A* Search
    # ------------------------------------------------------------------ #
    def find_path(self, start: tuple, goal: tuple) -> list | None:
        """
        Execute the A* search algorithm from *start* to *goal*.

        Algorithm outline:
          1. Initialise the open set (priority queue) with the start node.
          2. While the open set is not empty:
             a. Pop the node with the lowest f(n) = g(n) + h(n).
             b. If it is the goal, reconstruct and return the path.
             c. Otherwise, expand its neighbors:
                • Compute tentative g-score = g(current) + move_cost.
                • If this is better than any previously recorded g-score
                  for the neighbor, update and push to the open set.
          3. If the open set empties without reaching the goal, return None
             (no path exists — the agent is trapped).

        Parameters:
            start : (row, col) — the agent's current position.
            goal  : (row, col) — the safe-zone position.

        Returns:
            list of (row, col) from start to goal (inclusive), or
            None if no passable path exists.
        """
        # ---- Data structures ----
        # open_set is a min-heap of (f_score, counter, node).
        # The counter is a tie-breaker so that nodes with equal f are
        # popped in FIFO order, which guarantees deterministic behaviour
        # and avoids comparing tuples directly.
        counter = 0
        open_set: list = []
        heapq.heappush(open_set, (0, counter, start))

        # came_from[n] stores the parent of n on the cheapest known path
        came_from: dict = {}

        # g_score[n] = cost of the cheapest path from start to n found so far
        g_score: dict = {start: 0}

        # f_score[n] = g(n) + h(n) — stored for convenience
        f_score: dict = {start: self.heuristic(start, goal)}

        # closed_set tracks fully explored nodes (O(1) membership test)
        closed_set: set = set()

        # ---- Main loop ----
        while open_set:
            # Pop the node with the smallest f(n)
            current_f, _, current = heapq.heappop(open_set)

            # Skip if we already found a cheaper route to this node
            if current in closed_set:
                continue

            # Goal test — reconstruct and return the path
            if current == goal:
                return self._reconstruct_path(came_from, current)

            # Mark current as fully explored
            closed_set.add(current)

            # ---- Expand neighbors ----
            for neighbor in self.grid_env.get_neighbors(current):
                if neighbor in closed_set:
                    continue  # Already explored — skip

                # Compute tentative g-score for reaching this neighbor
                move_cost = self.grid_env.get_cost(neighbor)
                tentative_g = g_score[current] + move_cost

                # If this path to the neighbor is cheaper than any
                # previously found path, record it.
                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor, goal)
                    f_score[neighbor] = f

                    counter += 1
                    heapq.heappush(open_set, (f, counter, neighbor))

        # Open set is empty and goal was never reached — agent is trapped
        return None

    # ------------------------------------------------------------------ #
    #  Path Reconstruction
    # ------------------------------------------------------------------ #
    @staticmethod
    def _reconstruct_path(came_from: dict, current: tuple) -> list:
        """
        Backtrack through the came_from map to rebuild the full path
        from start to the goal.

        Parameters:
            came_from : dict mapping each node to its parent on the
                        cheapest path.
            current   : the goal node.

        Returns:
            list of (row, col) ordered from start to goal.
        """
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()  # Path was built goal→start; flip it
        return path
