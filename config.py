"""
config.py — Central Configuration for the Dynamic Wildfire Evacuation Router.

All tunable simulation parameters, grid dimensions, movement costs,
fire-spread mechanics, and color palette are defined here so that the
entire simulation can be adjusted from a single file.
"""

# ──────────────────────────────────────────────
#  Grid Dimensions
# ──────────────────────────────────────────────
GRID_ROWS = 40          # Number of rows in the grid
GRID_COLS = 40          # Number of columns in the grid
CELL_SIZE = 16          # Pixel width/height of each rendered cell

# ──────────────────────────────────────────────
#  Map Generation
# ──────────────────────────────────────────────
OBSTACLE_DENSITY = 0.15 # Fraction of cells turned into static obstacles
FIRE_SEEDS = 3          # Number of initial fire ignition points

# ──────────────────────────────────────────────
#  Fire Spread Mechanics
# ──────────────────────────────────────────────
FIRE_SPREAD_INTERVAL = 3   # Fire expands every N agent steps
FIRE_SPREAD_PROB = 0.4     # Probability a neighboring cell catches fire

# ──────────────────────────────────────────────
#  Movement Costs (for A* g(n) calculation)
# ──────────────────────────────────────────────
CLEAR_COST = 1             # Cost to move into a clear cell
HIGH_RISK_COST = 50        # Cost to move into a fire-adjacent cell
INF_COST = float("inf")    # Fire and obstacles are impassable

# ──────────────────────────────────────────────
#  Cell State Codes
# ──────────────────────────────────────────────
CLEAR = 0
OBSTACLE = 1
FIRE = 2
HIGH_RISK = 3

# ──────────────────────────────────────────────
#  Simulation Speed
# ──────────────────────────────────────────────
FPS = 8                    # Frames (agent steps) per second
MIN_FPS = 2
MAX_FPS = 30

# ──────────────────────────────────────────────
#  Status Panel
# ──────────────────────────────────────────────
PANEL_HEIGHT = 60          # Pixels reserved at the bottom for HUD info

# ──────────────────────────────────────────────
#  Color Palette  (R, G, B)
# ──────────────────────────────────────────────
COLOR_CLEAR       = (235, 235, 230)    # Warm off-white for walkable cells
COLOR_OBSTACLE    = ( 55,  55,  60)    # Dark charcoal for walls/buildings
COLOR_FIRE_A      = (230,  60,  30)    # Primary fire orange-red
COLOR_FIRE_B      = (255, 120,  20)    # Secondary fire (animated glow)
COLOR_HIGH_RISK   = (255, 200,  50)    # Amber warning for fire-adjacent
COLOR_START       = ( 30, 180, 100)    # Green marker for start
COLOR_END         = ( 40, 120, 220)    # Blue marker for safe zone
COLOR_AGENT       = (  0, 230, 180)    # Cyan-teal for the agent
COLOR_PATH        = (100, 100, 255)    # Soft blue for planned path
COLOR_REPLAN_FLASH= (255, 255, 100)    # Yellow flash on replan
COLOR_GRID_LINE   = (200, 200, 195)    # Subtle grid lines
COLOR_PANEL_BG    = ( 30,  30,  35)    # Dark HUD background
COLOR_TEXT         = (220, 220, 220)   # Light text for HUD
COLOR_TRAPPED_BG  = (180,  20,  20)   # Red overlay for trapped state
COLOR_SUCCESS_BG  = ( 20, 160,  80)   # Green overlay for success state
