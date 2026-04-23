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
PANEL_HEIGHT = 80          # Pixels reserved at the bottom for HUD info

# ──────────────────────────────────────────────
#  Color Palette  (R, G, B)
# ──────────────────────────────────────────────
COLOR_CLEAR       = ( 25,  26,  30)    # Deep midnight blue for empty space
COLOR_OBSTACLE    = ( 44,  45,  56)    # Lighter grayish-blue for walls (stands out vs clear)
COLOR_FIRE_A      = (255,  55,  85)    # Neon pinkish-red
COLOR_FIRE_B      = (255, 145,   0)    # Neon orange glow
COLOR_HIGH_RISK   = ( 90,  60,  30)    # Subtle warm warning glow
COLOR_START       = (  0, 220, 140)    # Bright teal-green jump start
COLOR_END         = ( 50, 160, 255)    # Bright neon blue safe zone
COLOR_AGENT       = (255, 255, 255)    # Bright white agent core
COLOR_PATH        = (  0, 180, 255)    # Cyberpunk light blue path dots
COLOR_REPLAN_FLASH= (255, 230,  50)    # Neon yellow flash
COLOR_GRID_LINE   = ( 35,  36,  42)    # Very subtle, slightly above CLEAR
COLOR_PANEL_BG    = ( 15,  16,  20)    # Jet black HUD background
COLOR_TEXT         = (200, 210, 220)   # Crisp light gray text
COLOR_TRAPPED_BG  = (220,  30,  50)    # Strong red overlay
COLOR_SUCCESS_BG  = ( 30, 200, 100)    # Strong green overlay
