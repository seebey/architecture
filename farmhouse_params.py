# ===================================================================
# FARMHOUSE PARAMS -- Shared Parametric Definitions
# ===================================================================
#
# Modern Rustic Farmhouse Courtyard Compound ("The Clearing")
#
# This module defines every parametric variable, the coordinate
# system, unit conversion helpers, and layer styling used across
# all FreeCAD scripts in this project.
#
# COORDINATE SYSTEM
#   Origin:  SW corner of lot
#   X-axis:  East  (positive to the right)
#   Y-axis:  North (positive up)
#   Z-axis:  Up
#   Units:   All parameters are in FEET unless noted otherwise.
#            Internal FreeCAD geometry uses millimeters.
#
# COMPOUND LAYOUT
#   The compound is arranged around a central courtyard:
#   - Main House primary bar runs E-W (south side of courtyard)
#   - Main House wing extends N from the east end of the bar
#   - Guest Pavilion sits north of the courtyard
#   - Breezeway connects the wing to the guest pavilion
#   - Barn/Garage is rotated east of the main complex
#   - Courtyard is the enclosed space between buildings
#
# USAGE
#   All other scripts import from this module:
#       from farmhouse_params import *
#   or selectively:
#       from farmhouse_params import FT, v, MAIN_X1, make_rect
#
# ===================================================================

import math
import os

import FreeCAD
import Draft

# ===================================================================
# 1. UNIT CONVERSION
# ===================================================================

FT = 304.8  # 1 foot = 304.8 mm


def v(x_ft, y_ft, z_ft=0):
    """Convert (x, y, z) in feet to FreeCAD.Vector in mm."""
    return FreeCAD.Vector(x_ft * FT, y_ft * FT, z_ft * FT)


def ft_to_mm(val):
    """Convert a single value from feet to millimeters."""
    return val * FT


# ===================================================================
# 2. SITE PARAMETERS (feet)
# ===================================================================

LOT_WIDTH = 200   # ft (E-W)
LOT_DEPTH = 220   # ft (N-S)

# ===================================================================
# 3. BUILDING PLACEMENT COORDINATES (feet)
# ===================================================================
# Origin at SW corner of lot.  X = East, Y = North, Z = Up.

# --- Main House - Primary Bar (E-W) ---
MAIN_X1, MAIN_Y1 = 68, 85
MAIN_X2, MAIN_Y2 = 132, 115
MAIN_BAR_LENGTH = MAIN_X2 - MAIN_X1   # 64 ft
MAIN_BAR_WIDTH  = MAIN_Y2 - MAIN_Y1   # 30 ft
MAIN_BAR_PITCH  = 8 / 12              # 8:12

# --- Main House - Wing (N-S) ---
WING_X1, WING_Y1 = 108, 115
WING_X2, WING_Y2 = 132, 143
WING_LENGTH = WING_Y2 - WING_Y1       # 28 ft
WING_WIDTH  = WING_X2 - WING_X1       # 24 ft
WING_PITCH  = 8 / 12                  # 8:12

# --- Guest Pavilion ---
GUEST_X1, GUEST_Y1 = 60, 151
GUEST_X2, GUEST_Y2 = 100, 171
GUEST_LENGTH = GUEST_X2 - GUEST_X1    # 40 ft
GUEST_WIDTH  = GUEST_Y2 - GUEST_Y1    # 20 ft
GUEST_PITCH  = 8 / 12                 # 8:12

# --- Barn / Garage (center + rotation) ---
BARN_CX, BARN_CY = 155, 100
BARN_LENGTH   = 36                     # along Y before rotation
BARN_WIDTH    = 26                     # along X before rotation
BARN_PITCH    = 10 / 12               # 10:12
BARN_ROTATION = 10                     # degrees CCW

# --- Breezeway ---
BW_X1, BW_Y1 = 103, 143
BW_X2, BW_Y2 = 108, 151
BREEZEWAY_WIDTH  = BW_X2 - BW_X1      # 5 ft
BREEZEWAY_LENGTH = BW_Y2 - BW_Y1      # 8 ft
BREEZEWAY_PITCH  = 2 / 12             # 2:12
BREEZEWAY_HEIGHT = 8.0                # ft

# --- Courtyard ---
COURT_X1, COURT_Y1 = 60, 115
COURT_X2, COURT_Y2 = 108, 151
COURT_LENGTH = COURT_X2 - COURT_X1    # 48 ft
COURT_WIDTH  = COURT_Y2 - COURT_Y1    # 36 ft

# ===================================================================
# 4. STRUCTURAL PARAMETERS (feet unless noted)
# ===================================================================

BAY_SPACING_MAIN  = 12                # ft
BAY_SPACING_GUEST = 10                # ft
BAY_SPACING_BARN  = 12                # ft
WALL_THICKNESS    = 10 / 12           # ft (10 inches)
FLOOR_TO_FLOOR    = 10.5              # ft

# ===================================================================
# 5. VERTICAL DIMENSIONS (feet)
# ===================================================================

ENTRY_CEILING        = 7.5
KITCHEN_CEILING      = 9.5
GREAT_ROOM_RIDGE     = 22.0
LIBRARY_CEILING      = 9.0
PRIMARY_SUITE_RIDGE  = 10.5
GUEST_CEILING        = 8.5
WINE_CELLAR_CEILING  = 7.0
BARN_STUDIO_RIDGE    = 12.0

# ===================================================================
# 6. DERIVED HEIGHTS (feet)
# ===================================================================
# Computed from eave height + (half-width * pitch).

MAIN_EAVE_HEIGHT  = 12.0
MAIN_RIDGE_HEIGHT = MAIN_EAVE_HEIGHT + (MAIN_BAR_WIDTH / 2) * MAIN_BAR_PITCH
# = 12.0 + 15*0.667 = 22.0

WING_EAVE_HEIGHT  = 12.0
WING_RIDGE_HEIGHT = WING_EAVE_HEIGHT + (WING_WIDTH / 2) * WING_PITCH
# = 12.0 + 12*0.667 = 20.0

GUEST_EAVE_HEIGHT  = 8.5
GUEST_RIDGE_HEIGHT = GUEST_EAVE_HEIGHT + (GUEST_WIDTH / 2) * GUEST_PITCH
# = 8.5 + 10*0.667 ~= 15.17

BARN_EAVE_HEIGHT  = 10.0
BARN_RIDGE_HEIGHT = BARN_EAVE_HEIGHT + (BARN_WIDTH / 2) * BARN_PITCH
# = 10.0 + 13*0.833 ~= 20.83

# ===================================================================
# 7. ROOF PARAMETERS (feet)
# ===================================================================

EAVE_OVERHANG = 4.0
RAKE_OVERHANG = 2.0

# ===================================================================
# 8. PORCH / CANOPY / OUTDOOR (feet)
# ===================================================================

GUEST_PORCH_DEPTH    = 6.0
CANOPY_DEPTH         = 10.0
FIRE_WALL_HEIGHT     = 8.0
FIRE_WALL_WIDTH      = 12.0
FIRE_WALL_THICKNESS  = 1.0

# ===================================================================
# 9. LAYER STYLES  (color: RGB 0-1 tuple, width: px)
# ===================================================================

LAYER_STYLE = {
    "SITE":        {"color": (0.00, 0.00, 0.00), "width": 1.5},
    "MAIN_HOUSE":  {"color": (0.15, 0.15, 0.50), "width": 2.5},
    "GUEST":       {"color": (0.20, 0.20, 0.55), "width": 2.0},
    "BARN":        {"color": (0.35, 0.35, 0.35), "width": 2.0},
    "BREEZEWAY":   {"color": (0.50, 0.30, 0.15), "width": 1.5},
    "COURTYARD":   {"color": (0.45, 0.45, 0.40), "width": 1.0},
    "CANOPY":      {"color": (0.55, 0.30, 0.10), "width": 1.5},
    "DRIVEWAY":    {"color": (0.45, 0.45, 0.45), "width": 1.0},
    "TREES":       {"color": (0.10, 0.50, 0.10), "width": 0.75},
    "WALLS":       {"color": (0.10, 0.10, 0.10), "width": 2.0},
    "GLAZING":     {"color": (0.00, 0.60, 0.85), "width": 1.0},
    "STRUCTURE":   {"color": (0.60, 0.30, 0.10), "width": 1.5},
    "ROOF":        {"color": (0.55, 0.30, 0.10), "width": 1.5},
    "DIMS":        {"color": (0.40, 0.40, 0.40), "width": 0.5},
    "SECTION_CUT": {"color": (0.00, 0.00, 0.00), "width": 3.0},
    "SECTION_BG":  {"color": (0.50, 0.50, 0.50), "width": 1.0},
}

# ===================================================================
# 10. OUTPUT CONFIGURATION
# ===================================================================

OUTPUT_DIR = os.path.expanduser("~")

# ===================================================================
# 11. HELPER FUNCTIONS
# ===================================================================


def apply_style(obj, layer_name):
    """Set line color and width on an object from LAYER_STYLE."""
    style = LAYER_STYLE.get(layer_name)
    if not style:
        return
    try:
        vo = obj.ViewObject
        if vo:
            vo.LineColor = style["color"]
            vo.LineWidth = style["width"]
    except Exception:
        pass


def make_closed_wire(points_ft, label, group, layer_name):
    """
    Create a closed Draft Wire from (x, y) tuples in feet.
    Adds the wire to *group* and applies the layer style.
    """
    vectors = [v(x, y) for x, y in points_ft]
    wire = Draft.make_wire(vectors, closed=True, face=False)
    wire.Label = label
    group.addObject(wire)
    apply_style(wire, layer_name)
    return wire


def make_rect(x1, y1, x2, y2, label, group, layer_name):
    """
    Create a closed rectangular wire from two corner coordinates
    (x1, y1) and (x2, y2), specified in feet.
    """
    pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    return make_closed_wire(pts, label, group, layer_name)


def make_line(x1, y1, x2, y2, label, group, layer_name):
    """
    Create a single open line segment (Draft Wire, closed=False)
    from (x1, y1) to (x2, y2) in feet.
    """
    vectors = [v(x1, y1), v(x2, y2)]
    wire = Draft.make_wire(vectors, closed=False, face=False)
    wire.Label = label
    group.addObject(wire)
    apply_style(wire, layer_name)
    return wire


def _rotated_corners(cx, cy, length, width, angle_deg):
    """
    Return 4 corner points of a rectangle rotated about (cx, cy).

    Before rotation the rectangle is axis-aligned:
      - Length is measured along Y
      - Width  is measured along X
    Corners are rotated *angle_deg* CCW about (cx, cy).
    Returns list of (x_ft, y_ft) tuples.
    """
    half_w = width / 2.0
    half_l = length / 2.0

    raw_corners = [
        (-half_w, -half_l),
        ( half_w, -half_l),
        ( half_w,  half_l),
        (-half_w,  half_l),
    ]

    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    return [(cx + dx * cos_a - dy * sin_a,
             cy + dx * sin_a + dy * cos_a) for dx, dy in raw_corners]


def make_rotated_rect(cx, cy, length, width, angle_deg, label, group, layer_name):
    """Create a rectangle rotated about its center (cx, cy) in feet."""
    pts = _rotated_corners(cx, cy, length, width, angle_deg)
    return make_closed_wire(pts, label, group, layer_name)


def barn_corners():
    """
    Return the 4 corner points of the barn after rotation, as a list
    of (x_ft, y_ft) tuples.
    """
    return _rotated_corners(BARN_CX, BARN_CY, BARN_LENGTH, BARN_WIDTH, BARN_ROTATION)


def make_tree(cx_ft, cy_ft, radius_ft, label, group):
    """
    Create a Draft Circle representing a tree canopy, centered at
    (cx_ft, cy_ft) with the given radius, all in feet.
    """
    circle = Draft.make_circle(radius_ft * FT)
    circle.Placement.Base = v(cx_ft, cy_ft)
    circle.Label = label
    group.addObject(circle)
    apply_style(circle, "TREES")
    return circle


def export_dxf(doc, filename):
    """
    Export all geometry objects in *doc* to a DXF file.
    Filters out DocumentObjectGroup containers.
    The file is written to OUTPUT_DIR/filename.
    """
    try:
        import importDXF
    except ImportError:
        print("DXF export failed: importDXF module not available.")
        return None

    filepath = os.path.join(OUTPUT_DIR, filename)
    export_objs = [
        o for o in doc.Objects
        if not o.isDerivedFrom("App::DocumentObjectGroup")
    ]
    try:
        importDXF.export(export_objs, filepath)
        print("DXF exported: {}".format(filepath))
    except Exception as e:
        print("DXF export failed: {}".format(e))
    return filepath


def export_step(doc, filename):
    """
    Export all Part shapes with Volume > 0 from *doc* to a STEP file.
    The file is written to OUTPUT_DIR/filename.
    """
    import Part

    filepath = os.path.join(OUTPUT_DIR, filename)
    export_objs = []
    for o in doc.Objects:
        try:
            if hasattr(o, "Shape") and o.Shape.Volume > 0:
                export_objs.append(o)
        except Exception:
            continue

    if export_objs:
        Part.export(export_objs, filepath)
        print("STEP exported: {} ({} objects)".format(filepath, len(export_objs)))
    else:
        print("STEP export: no objects with volume found.")
    return filepath
