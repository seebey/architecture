# ===================================================================
# MODERN RUSTIC FARMHOUSE -- COURTYARD COMPOUND SITE PLAN
# FreeCAD Python Script (tested on FreeCAD 0.21+)
# ===================================================================
#
# Generates a complete 2D site plan for a modern rustic farmhouse
# courtyard compound on a 1-acre (200' x 220') rectangular lot.
#
# Layout: Three buildings arranged around a central courtyard:
#   - Main House (L-shaped: primary bar E-W + wing extending N)
#   - Guest Pavilion (north of courtyard)
#   - Barn / Garage (rotated, east of compound)
#   - Breezeway connecting wing to guest pavilion
#   - Corten canopy + fire wall in courtyard
#   - Arrival drive curving from east lot edge
#
# Usage: Paste entire script into FreeCAD's Python console,
#        or run via:  freecad -c farmhouse_site_plan.py
# Output: DXF file at ~/farmhouse_site_plan.dxf
#
# All dimensions specified in feet; converted to mm internally
# via farmhouse_params.py.
# ===================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farmhouse_params import *
import random


# ===================================================================
# LOCAL PARAMETERS
# ===================================================================

SETBACK_FRONT = 35   # south (street side)
SETBACK_SIDE  = 20   # east and west
SETBACK_REAR  = 30   # north

TREE_TARGET    = 75
TREE_SEED      = 42
TREE_RADIUS_MIN = 4
TREE_RADIUS_MAX = 8
TREE_MIN_GAP   = 4   # minimum gap between tree canopies


# ===================================================================
# TREE HELPER FUNCTIONS
# ===================================================================

def overlaps_exclusion(x, y, r, zones):
    """True if circle (x, y, r) overlaps any exclusion rectangle."""
    for x1, y1, x2, y2 in zones:
        if x + r > x1 and x - r < x2 and y + r > y1 and y - r < y2:
            return True
    return False


def too_close(x, y, r, placed, min_gap):
    """True if circle (x, y, r) is within min_gap of any placed tree."""
    for tx, ty, tr in placed:
        dist = ((x - tx) ** 2 + (y - ty) ** 2) ** 0.5
        if dist < r + tr + min_gap:
            return True
    return False


# ===================================================================
# TREE EXCLUSION ZONES (x1, y1, x2, y2 in feet)
# ===================================================================

EXCLUSION_ZONES = [
    (MAIN_X1 - 4, MAIN_Y1 - 4, MAIN_X2 + 4, MAIN_Y2 + 4),                  # main bar
    (WING_X1 - 4, WING_Y1, WING_X2 + 4, WING_Y2 + 4),                       # wing
    (GUEST_X1 - 4, GUEST_Y1 - GUEST_PORCH_DEPTH - 4,
     GUEST_X2 + 4, GUEST_Y2 + 4),                                            # guest + porch
    (COURT_X1 - 2, COURT_Y1, COURT_X2, COURT_Y2),                            # courtyard
    (BW_X1 - 2, BW_Y1 - 2, BW_X2 + 2, BW_Y2 + 2),                           # breezeway
    (130, 70, LOT_WIDTH, 115),                                                 # driveway corridor
]

# Add barn bounding box from barn_corners()
bc = barn_corners()
barn_xs = [c[0] for c in bc]
barn_ys = [c[1] for c in bc]
EXCLUSION_ZONES.append((min(barn_xs) - 4, min(barn_ys) - 4,
                         max(barn_xs) + 4, max(barn_ys) + 4))


# ===================================================================
# DOCUMENT SETUP
# ===================================================================

doc = FreeCAD.newDocument("FarmhouseSitePlan")
print("Document created: FarmhouseSitePlan")

# -------------------------------------------------------------------
# Create layer groups
# -------------------------------------------------------------------
layer_names = ["SITE", "MAIN_HOUSE", "GUEST", "BARN", "BREEZEWAY",
               "COURTYARD", "CANOPY", "DRIVEWAY", "TREES"]

layers = {}
for name in layer_names:
    layers[name] = doc.addObject("App::DocumentObjectGroup", name)
print("Layer groups created: " + ", ".join(layer_names))


# ===================================================================
# GEOMETRY GENERATION
# ===================================================================

# -------------------------------------------------------------------
# 1. LOT BOUNDARY -- 200' x 220'
# -------------------------------------------------------------------
make_rect(0, 0, LOT_WIDTH, LOT_DEPTH,
          "Lot_Boundary", layers["SITE"], "SITE")
print("Lot boundary created: {}' x {}'".format(LOT_WIDTH, LOT_DEPTH))

# -------------------------------------------------------------------
# 2. SETBACK LINES (dashed, lighter styling, on SITE layer)
# -------------------------------------------------------------------
setback_wire = make_rect(
    SETBACK_SIDE, SETBACK_FRONT,
    LOT_WIDTH - SETBACK_SIDE, LOT_DEPTH - SETBACK_REAR,
    "Setback_Lines", layers["SITE"], "SITE"
)
try:
    setback_wire.ViewObject.DrawStyle = "Dashed"
    setback_wire.ViewObject.LineWidth = 0.5
    setback_wire.ViewObject.LineColor = (0.6, 0.6, 0.6)
except Exception:
    pass
print("Setback lines created: front={}', sides={}', rear={}'".format(
    SETBACK_FRONT, SETBACK_SIDE, SETBACK_REAR))

# -------------------------------------------------------------------
# 3. MAIN HOUSE FOOTPRINT -- L-shaped polygon
#    Primary bar (64' x 30') + wing (24' x 28')
# -------------------------------------------------------------------
house_pts = [
    (MAIN_X1, MAIN_Y1),   # SW corner of bar (68, 85)
    (MAIN_X2, MAIN_Y1),   # SE corner of bar (132, 85)
    (MAIN_X2, WING_Y2),   # NE corner of wing (132, 143)
    (WING_X1, WING_Y2),   # NW corner of wing (108, 143)
    (WING_X1, MAIN_Y2),   # inside corner of L (108, 115)
    (MAIN_X1, MAIN_Y2),   # NW corner of bar (68, 115)
]
make_closed_wire(house_pts, "Main_House", layers["MAIN_HOUSE"], "MAIN_HOUSE")
print("Main house footprint created: L-shaped (bar {}' x {}' + wing {}' x {}')".format(
    MAIN_BAR_LENGTH, MAIN_BAR_WIDTH, WING_WIDTH, WING_LENGTH))

# -------------------------------------------------------------------
# 4. GUEST PAVILION FOOTPRINT -- 40' x 20' rectangle
# -------------------------------------------------------------------
make_rect(GUEST_X1, GUEST_Y1, GUEST_X2, GUEST_Y2,
          "Guest_Pavilion", layers["GUEST"], "GUEST")
print("Guest pavilion created: {}' x {}'".format(GUEST_LENGTH, GUEST_WIDTH))

# -------------------------------------------------------------------
# 5. BARN FOOTPRINT -- rotated rectangle
# -------------------------------------------------------------------
make_rotated_rect(BARN_CX, BARN_CY, BARN_LENGTH, BARN_WIDTH, BARN_ROTATION,
                  "Barn", layers["BARN"], "BARN")
print("Barn created: {}' x {}', rotated {}deg CCW at ({}, {})".format(
    BARN_LENGTH, BARN_WIDTH, BARN_ROTATION, BARN_CX, BARN_CY))

# -------------------------------------------------------------------
# 6. BREEZEWAY FOOTPRINT -- 5' x 8' connecting wing to guest
# -------------------------------------------------------------------
make_rect(BW_X1, BW_Y1, BW_X2, BW_Y2,
          "Breezeway", layers["BREEZEWAY"], "BREEZEWAY")
print("Breezeway created: {}' x {}'".format(BREEZEWAY_WIDTH, BREEZEWAY_LENGTH))

# -------------------------------------------------------------------
# 7. COURTYARD PAVING ZONE -- rectangular paving area
#    Three sides defined by buildings, west side open (conceptual)
# -------------------------------------------------------------------
court_pts = [
    (COURT_X2, COURT_Y1),   # SE corner (at wing/main intersection)
    (COURT_X2, COURT_Y2),   # NE corner (at breezeway)
    (COURT_X1, COURT_Y2),   # NW corner (near guest pavilion)
    (COURT_X1, COURT_Y1),   # SW corner
]
make_closed_wire(court_pts, "Courtyard_Paving", layers["COURTYARD"], "COURTYARD")
print("Courtyard paving created: {}' x {}'".format(COURT_LENGTH, COURT_WIDTH))

# -------------------------------------------------------------------
# 8. CORTEN CANOPY -- extends from main bar north face into courtyard
#    24' wide (great room width) x 10' deep
# -------------------------------------------------------------------
canopy_x1 = MAIN_X1                    # aligned with great room west end
canopy_x2 = MAIN_X1 + 24               # 24' wide (width of great room)
canopy_y1 = MAIN_Y2                    # main bar north face
canopy_y2 = MAIN_Y2 + CANOPY_DEPTH    # extends into courtyard
make_rect(canopy_x1, canopy_y1, canopy_x2, canopy_y2,
          "Corten_Canopy", layers["CANOPY"], "CANOPY")
print("Corten canopy created: {}' x {}' extending into courtyard".format(
    canopy_x2 - canopy_x1, CANOPY_DEPTH))

# -------------------------------------------------------------------
# 9. FIRE WALL -- freestanding concrete wall in south courtyard
#    12' wide x 1' thick, centered E-W
# -------------------------------------------------------------------
fw_cx = (COURT_X1 + COURT_X2) / 2     # centered E-W in courtyard
fw_y = COURT_Y1 + 10                  # 10' north of main bar
make_rect(fw_cx - FIRE_WALL_WIDTH / 2, fw_y,
          fw_cx + FIRE_WALL_WIDTH / 2, fw_y + FIRE_WALL_THICKNESS,
          "Fire_Wall", layers["CANOPY"], "CANOPY")
print("Fire wall created: {}' x {}' at courtyard center".format(
    FIRE_WALL_WIDTH, FIRE_WALL_THICKNESS))

# -------------------------------------------------------------------
# 10. ARRIVAL DRIVE -- open polyline from east lot edge to main house
#     Gentle curve through barn area
# -------------------------------------------------------------------
drive_pts = [
    (LOT_WIDTH, 80),                                    # entry from east lot edge
    (185, 85),                                           # gentle curve begins
    (170, 92),
    (BARN_CX + 15, BARN_CY - 5),                       # approaches barn
    (BARN_CX - 5, BARN_CY - 15),                       # past barn
    (140, 90),
    (MAIN_X2 + 5, (MAIN_Y1 + MAIN_Y2) / 2),           # arrives at main house entry
]
drive_vectors = [v(x, y) for x, y in drive_pts]
drive = Draft.make_wire(drive_vectors, closed=False, face=False)
drive.Label = "Arrival_Drive"
layers["DRIVEWAY"].addObject(drive)
apply_style(drive, "DRIVEWAY")
print("Arrival drive created: {} points, east lot edge to main house entry".format(
    len(drive_pts)))

# -------------------------------------------------------------------
# 11. GUEST PAVILION SOUTH PORCH -- 6' deep covered porch
# -------------------------------------------------------------------
make_rect(GUEST_X1, GUEST_Y1 - GUEST_PORCH_DEPTH, GUEST_X2, GUEST_Y1,
          "Guest_South_Porch", layers["COURTYARD"], "COURTYARD")
print("Guest south porch created: {}' x {}'".format(
    GUEST_LENGTH, GUEST_PORCH_DEPTH))


# ===================================================================
# TREE PLACEMENT
# ===================================================================

print("Placing trees...")
random.seed(TREE_SEED)
placed_trees = []

# Phase 1: Perimeter buffer trees (~40% of target)
# Concentrated within 30' of lot edges for privacy screening
perimeter_target = int(TREE_TARGET * 0.4)
attempts = 0
while len(placed_trees) < perimeter_target and attempts < 5000:
    r = random.uniform(TREE_RADIUS_MIN, TREE_RADIUS_MAX)
    # Pick a random edge and generate position near it
    edge = random.choice(["N", "S", "E", "W"])
    if edge == "N":
        x = random.uniform(r + 3, LOT_WIDTH - r - 3)
        y = random.uniform(LOT_DEPTH - 30, LOT_DEPTH - r - 3)
    elif edge == "S":
        x = random.uniform(r + 3, LOT_WIDTH - r - 3)
        y = random.uniform(r + 3, 30)
    elif edge == "E":
        x = random.uniform(LOT_WIDTH - 30, LOT_WIDTH - r - 3)
        y = random.uniform(r + 3, LOT_DEPTH - r - 3)
    else:
        x = random.uniform(r + 3, 30)
        y = random.uniform(r + 3, LOT_DEPTH - r - 3)

    if overlaps_exclusion(x, y, r, EXCLUSION_ZONES):
        attempts += 1
        continue
    if too_close(x, y, r, placed_trees, TREE_MIN_GAP):
        attempts += 1
        continue

    placed_trees.append((x, y, r))
    attempts = 0

perimeter_placed = len(placed_trees)

# Phase 2: Interior scatter trees (remaining count)
# Distributed across the full lot for shade and landscape interest
attempts = 0
while len(placed_trees) < TREE_TARGET and attempts < 5000:
    r = random.uniform(TREE_RADIUS_MIN, TREE_RADIUS_MAX)
    x = random.uniform(r + 3, LOT_WIDTH - r - 3)
    y = random.uniform(r + 3, LOT_DEPTH - r - 3)

    if overlaps_exclusion(x, y, r, EXCLUSION_ZONES):
        attempts += 1
        continue
    if too_close(x, y, r, placed_trees, TREE_MIN_GAP):
        attempts += 1
        continue

    placed_trees.append((x, y, r))
    attempts = 0

# Create Draft Circle objects for each tree
for i, (tx, ty, tr) in enumerate(placed_trees):
    make_tree(tx, ty, tr, "Tree_{:03d}".format(i + 1), layers["TREES"])

print("Trees placed: {} total ({} perimeter, {} interior)".format(
    len(placed_trees), perimeter_placed, len(placed_trees) - perimeter_placed))


# ===================================================================
# RECOMPUTE AND FIT VIEW
# ===================================================================

doc.recompute()
print("Document recomputed.")

# Try to fit view
try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
    FreeCADGui.ActiveDocument.ActiveView.viewTop()
    print("View set to top-down, fit to extents.")
except Exception:
    pass


# ===================================================================
# DXF EXPORT
# ===================================================================

export_dxf(doc, "farmhouse_site_plan.dxf")


# ===================================================================
# SUMMARY
# ===================================================================

print("")
print("=" * 55)
print("COURTYARD COMPOUND SITE PLAN SUMMARY")
print("=" * 55)
print("Lot:            {}' x {}' (1 acre)".format(LOT_WIDTH, LOT_DEPTH))
print("Setbacks:       front={}', sides={}', rear={}'".format(
    SETBACK_FRONT, SETBACK_SIDE, SETBACK_REAR))
print("")
print("BUILDINGS:")
print("  Main House:   L-shaped (bar {}' x {}' + wing {}' x {}')".format(
    MAIN_BAR_LENGTH, MAIN_BAR_WIDTH, WING_WIDTH, WING_LENGTH))
print("                at ({}, {}) to ({}, {})".format(
    MAIN_X1, MAIN_Y1, MAIN_X2, WING_Y2))
print("  Guest Pav:    {}' x {}' at ({}, {})".format(
    GUEST_LENGTH, GUEST_WIDTH, GUEST_X1, GUEST_Y1))
print("  Barn/Garage:  {}' x {}' rotated {}deg at ({}, {})".format(
    BARN_LENGTH, BARN_WIDTH, BARN_ROTATION, BARN_CX, BARN_CY))
print("  Breezeway:    {}' x {}' at ({}, {})".format(
    BREEZEWAY_WIDTH, BREEZEWAY_LENGTH, BW_X1, BW_Y1))
print("")
print("COURTYARD:")
print("  Paving:       {}' x {}'".format(COURT_LENGTH, COURT_WIDTH))
print("  Canopy:       {}' x {}'".format(canopy_x2 - canopy_x1, CANOPY_DEPTH))
print("  Fire Wall:    {}' x {}'".format(FIRE_WALL_WIDTH, FIRE_WALL_THICKNESS))
print("  Guest Porch:  {}' x {}'".format(GUEST_LENGTH, GUEST_PORCH_DEPTH))
print("")
print("LANDSCAPE:")
print("  Trees:        {} placed ({} perimeter, {} interior)".format(
    len(placed_trees), perimeter_placed, len(placed_trees) - perimeter_placed))
print("  Drive:        {} point arrival curve from east".format(len(drive_pts)))
print("")
print("Layers:         {}".format(", ".join(layer_names)))
print("Export:         ~/farmhouse_site_plan.dxf")
print("=" * 55)
print("Script complete.")
