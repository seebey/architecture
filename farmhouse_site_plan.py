# ═══════════════════════════════════════════════════════════════════
# MODERN RUSTIC FARMHOUSE — SITE PLAN GENERATOR
# FreeCAD Python Script (tested on FreeCAD 0.21+)
# ═══════════════════════════════════════════════════════════════════
#
# Generates a complete 2D site plan for a modern rustic farmhouse
# on a 1-acre (200' x 220') rectangular lot.
#
# Layout: L-shaped main house with wrap-around porch, detached
# garage, courtyard pool, and perimeter tree buffer.
#
# Usage: Paste entire script into FreeCAD's Python console.
# Output: DXF file at ~/farmhouse_site_plan.dxf
#
# All dimensions specified in feet; converted to mm internally.
# ═══════════════════════════════════════════════════════════════════

import FreeCAD
import Draft
import random
import os

# ───────────────────────────────────────────────────
# UNIT CONVERSION
# ───────────────────────────────────────────────────
FT = 304.8  # 1 foot = 304.8 millimeters


def v(x_ft, y_ft):
    """Convert (x, y) in feet to a FreeCAD.Vector in mm."""
    return FreeCAD.Vector(x_ft * FT, y_ft * FT, 0)


# ───────────────────────────────────────────────────
# OUTPUT CONFIGURATION
# ───────────────────────────────────────────────────
OUTPUT_DIR = os.path.expanduser("~")
DXF_FILENAME = "farmhouse_site_plan.dxf"
DXF_PATH = os.path.join(OUTPUT_DIR, DXF_FILENAME)

# ───────────────────────────────────────────────────
# SITE PARAMETERS (all values in feet)
# ───────────────────────────────────────────────────
LOT_WIDTH = 200
LOT_DEPTH = 220

SETBACK_FRONT = 35   # south (street side)
SETBACK_SIDE = 20    # east and west
SETBACK_REAR = 30    # north

TREE_TARGET = 75
TREE_SEED = 42
TREE_RADIUS_MIN = 4
TREE_RADIUS_MAX = 8
TREE_MIN_GAP = 4     # minimum gap between tree canopies

# ───────────────────────────────────────────────────
# BUILDING COORDINATES (feet)
# ───────────────────────────────────────────────────
# Main bar: 64' x 30', runs east-west
MB_X1, MB_Y1 = 52, 75
MB_X2, MB_Y2 = 116, 105

# Wing: 24' x 28', extends north from east end of main bar
WG_X1, WG_Y1 = 92, 105
WG_X2, WG_Y2 = 116, 133

# Wrap-around porch: 8' deep on south and west of main bar
PORCH_DEPTH = 8
PORCH_S_Y = MB_Y1 - PORCH_DEPTH   # 67
PORCH_W_X = MB_X1 - PORCH_DEPTH   # 44

# Rear patio: 8' deep, inside the L courtyard
PATIO_X1, PATIO_Y1 = MB_X1, MB_Y2       # 52, 105
PATIO_X2, PATIO_Y2 = WG_X1, MB_Y2 + 8   # 92, 113

# Garage: 24' x 28', detached northeast
GAR_X1, GAR_Y1 = 136, 88
GAR_X2, GAR_Y2 = 160, 116

# Pool: 32' x 16', in courtyard
POOL_X1, POOL_Y1 = 54, 113
POOL_X2, POOL_Y2 = 86, 129

# Pool deck: 6' surround
DECK_PAD = 6
DECK_X1 = POOL_X1 - DECK_PAD   # 48
DECK_Y1 = POOL_Y1 - DECK_PAD   # 107
DECK_X2 = POOL_X2 + DECK_PAD   # 92
DECK_Y2 = POOL_Y2 + DECK_PAD   # 135

# Front walkway: 6' wide, centered on main bar
WALK_CX = (MB_X1 + MB_X2) / 2   # 84
WALK_HW = 3                      # half-width
WALK_X1 = WALK_CX - WALK_HW     # 81
WALK_X2 = WALK_CX + WALK_HW     # 87
WALK_Y1 = 0                      # starts at street
WALK_Y2 = PORCH_S_Y             # ends at porch (67)

# Driveway: 14' lane + 32'x13' parking pad
DRV_LANE_X1, DRV_LANE_X2 = 141, 155   # 14' wide lane
DRV_PAD_X1, DRV_PAD_X2 = 130, 162     # 32' wide pad
DRV_PAD_Y = 75                         # where pad begins
DRV_PAD_TOP = GAR_Y1                   # pad top at garage face (88)

# ───────────────────────────────────────────────────
# VISUAL STYLE (line_color RGB 0-1, line_width in px)
# ───────────────────────────────────────────────────
LAYER_STYLE = {
    "LOT":       {"color": (0.00, 0.00, 0.00), "width": 2.0},
    "BUILDING":  {"color": (0.15, 0.15, 0.50), "width": 2.5},
    "PORCH":     {"color": (0.55, 0.35, 0.15), "width": 1.5},
    "GARAGE":    {"color": (0.35, 0.35, 0.35), "width": 2.0},
    "POOL":      {"color": (0.00, 0.45, 0.85), "width": 1.5},
    "HARDSCAPE": {"color": (0.60, 0.55, 0.45), "width": 1.0},
    "DRIVEWAY":  {"color": (0.45, 0.45, 0.45), "width": 1.0},
    "TREES":     {"color": (0.10, 0.50, 0.10), "width": 0.75},
}

# ───────────────────────────────────────────────────
# TREE EXCLUSION ZONES (x1, y1, x2, y2 in feet)
# ───────────────────────────────────────────────────
EXCLUSION_ZONES = [
    (PORCH_W_X - 2, PORCH_S_Y - 2, MB_X2 + 2, PATIO_Y2 + 2),  # house + porch + patio
    (WG_X1 - 4, WG_Y1 - 2, WG_X2 + 2, WG_Y2 + 4),             # wing
    (DECK_X1 - 4, DECK_Y1 - 4, DECK_X2 + 4, DECK_Y2 + 4),     # pool deck
    (GAR_X1 - 4, GAR_Y1 - 4, GAR_X2 + 4, GAR_Y2 + 4),         # garage
    (DRV_PAD_X1 - 4, 0, DRV_PAD_X2 + 4, DRV_PAD_TOP + 4),     # driveway
    (WALK_X1 - 4, 0, WALK_X2 + 4, WALK_Y2 + 4),                # front walkway
]


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def apply_style(obj, layer_name):
    """Set line color and width on an object's ViewObject."""
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
    Add to group and apply layer style.
    """
    vectors = [v(x, y) for x, y in points_ft]
    wire = Draft.make_wire(vectors, closed=True, face=False)
    wire.Label = label
    group.addObject(wire)
    apply_style(wire, layer_name)
    return wire


def make_rect(x1, y1, x2, y2, label, group, layer_name):
    """Convenience: closed rectangular wire from two corner coords in feet."""
    pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    return make_closed_wire(pts, label, group, layer_name)


def make_tree(cx_ft, cy_ft, radius_ft, label, group):
    """Create a Draft Circle (tree canopy) at the given center in feet."""
    circle = Draft.make_circle(radius_ft * FT)
    circle.Placement.Base = v(cx_ft, cy_ft)
    circle.Label = label
    group.addObject(circle)
    apply_style(circle, "TREES")
    return circle


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


# ═══════════════════════════════════════════════════════════════════
# DOCUMENT SETUP
# ═══════════════════════════════════════════════════════════════════

doc = FreeCAD.newDocument("FarmhouseSitePlan")
print("Document created: FarmhouseSitePlan")

# ───────────────────────────────────────────────────
# Create layer groups
# ───────────────────────────────────────────────────
layers = {}
for name in LAYER_STYLE:
    layers[name] = doc.addObject("App::DocumentObjectGroup", name)
print("Layer groups created: " + ", ".join(LAYER_STYLE.keys()))


# ═══════════════════════════════════════════════════════════════════
# GEOMETRY GENERATION
# ═══════════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────
# 1. LOT BOUNDARY — 200' x 220'
# ───────────────────────────────────────────────────
make_rect(0, 0, LOT_WIDTH, LOT_DEPTH,
          "Lot_Boundary", layers["LOT"], "LOT")
print("Lot boundary created: {}' x {}'".format(LOT_WIDTH, LOT_DEPTH))

# ───────────────────────────────────────────────────
# 2. SETBACK LINES (dashed reference, on LOT layer)
# ───────────────────────────────────────────────────
setback_wire = make_rect(
    SETBACK_SIDE, SETBACK_FRONT,
    LOT_WIDTH - SETBACK_SIDE, LOT_DEPTH - SETBACK_REAR,
    "Setback_Lines", layers["LOT"], "LOT"
)
try:
    setback_wire.ViewObject.DrawStyle = "Dashed"
    setback_wire.ViewObject.LineWidth = 0.5
    setback_wire.ViewObject.LineColor = (0.6, 0.6, 0.6)
except Exception:
    pass
print("Setback lines created: front={}', sides={}', rear={}'".format(
    SETBACK_FRONT, SETBACK_SIDE, SETBACK_REAR))

# ───────────────────────────────────────────────────
# 3. BUILDING FOOTPRINT — L-shaped farmhouse
#    Main bar: 64' x 30'  |  Wing: 24' x 28'
#    Total footprint: ~2,592 SF
#    Estimated total area (2 story): ~4,512 SF
# ───────────────────────────────────────────────────
building_pts = [
    (MB_X1, MB_Y1),   # 52,  75  — SW corner main bar
    (MB_X2, MB_Y1),   # 116, 75  — SE corner main bar
    (MB_X2, WG_Y2),   # 116, 133 — NE corner wing
    (WG_X1, WG_Y2),   # 92,  133 — NW corner wing
    (WG_X1, MB_Y2),   # 92,  105 — inside corner of L
    (MB_X1, MB_Y2),   # 52,  105 — NW corner main bar
]
make_closed_wire(building_pts, "House_Footprint", layers["BUILDING"], "BUILDING")
print("Building footprint created: L-shaped, ~2,592 SF")

# ───────────────────────────────────────────────────
# 4. PORCH — Wrap-around (south + west of main bar)
#    8' deep on both faces
# ───────────────────────────────────────────────────
porch_wrap_pts = [
    (PORCH_W_X, PORCH_S_Y),  # 44, 67  — SW outer corner
    (MB_X2,     PORCH_S_Y),  # 116, 67 — SE of south porch
    (MB_X2,     MB_Y1),      # 116, 75 — meets building SE
    (MB_X1,     MB_Y1),      # 52, 75  — meets building SW
    (MB_X1,     MB_Y2),      # 52, 105 — meets building NW
    (PORCH_W_X, MB_Y2),      # 44, 105 — NW of west porch
]
make_closed_wire(porch_wrap_pts, "Porch_WrapAround", layers["PORCH"], "PORCH")
print("Wrap-around porch created: 8' deep, south + west")

# ───────────────────────────────────────────────────
# 5. PORCH — Rear covered patio (courtyard, inside L)
#    40' x 8', connects to pool deck area
# ───────────────────────────────────────────────────
make_rect(PATIO_X1, PATIO_Y1, PATIO_X2, PATIO_Y2,
          "Porch_RearPatio", layers["PORCH"], "PORCH")
print("Rear patio created: {}' x {}'".format(
    PATIO_X2 - PATIO_X1, PATIO_Y2 - PATIO_Y1))

# ───────────────────────────────────────────────────
# 6. GARAGE — Detached, 24' x 28'
#    Northeast of house, aligned with driveway
# ───────────────────────────────────────────────────
make_rect(GAR_X1, GAR_Y1, GAR_X2, GAR_Y2,
          "Garage", layers["GARAGE"], "GARAGE")
print("Garage created: {}' x {}', detached NE".format(
    GAR_X2 - GAR_X1, GAR_Y2 - GAR_Y1))

# ───────────────────────────────────────────────────
# 7. POOL — 32' x 16', courtyard placement
# ───────────────────────────────────────────────────
make_rect(POOL_X1, POOL_Y1, POOL_X2, POOL_Y2,
          "Pool", layers["POOL"], "POOL")
print("Pool created: {}' x {}'".format(
    POOL_X2 - POOL_X1, POOL_Y2 - POOL_Y1))

# ───────────────────────────────────────────────────
# 8. HARDSCAPE — Pool deck (6' surround)
# ───────────────────────────────────────────────────
make_rect(DECK_X1, DECK_Y1, DECK_X2, DECK_Y2,
          "Pool_Deck", layers["HARDSCAPE"], "HARDSCAPE")
print("Pool deck created: {}' x {}' (6' surround)".format(
    DECK_X2 - DECK_X1, DECK_Y2 - DECK_Y1))

# ───────────────────────────────────────────────────
# 9. HARDSCAPE — Front walkway (6' wide)
# ───────────────────────────────────────────────────
make_rect(WALK_X1, WALK_Y1, WALK_X2, WALK_Y2,
          "Front_Walkway", layers["HARDSCAPE"], "HARDSCAPE")
print("Front walkway created: {}' wide, {}' long".format(
    WALK_X2 - WALK_X1, WALK_Y2 - WALK_Y1))

# ───────────────────────────────────────────────────
# 10. DRIVEWAY — 14' lane + parking pad
#     Lane: 14' wide from street to y=75'
#     Pad:  32' x 13' widens in front of garage
# ───────────────────────────────────────────────────
driveway_pts = [
    (DRV_LANE_X1, 0),           # 141, 0   — SW at street
    (DRV_LANE_X2, 0),           # 155, 0   — SE at street
    (DRV_LANE_X2, DRV_PAD_Y),   # 155, 75  — lane meets pad (E)
    (DRV_PAD_X2,  DRV_PAD_Y),   # 162, 75  — pad SE
    (DRV_PAD_X2,  DRV_PAD_TOP), # 162, 88  — pad NE (at garage)
    (DRV_PAD_X1,  DRV_PAD_TOP), # 130, 88  — pad NW
    (DRV_PAD_X1,  DRV_PAD_Y),   # 130, 75  — pad SW
    (DRV_LANE_X1, DRV_PAD_Y),   # 141, 75  — lane meets pad (W)
]
make_closed_wire(driveway_pts, "Driveway", layers["DRIVEWAY"], "DRIVEWAY")
print("Driveway created: 14' lane + 32' x 13' parking pad")


# ═══════════════════════════════════════════════════════════════════
# TREE PLACEMENT
# ═══════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════
# RECOMPUTE AND FIT VIEW
# ═══════════════════════════════════════════════════════════════════

doc.recompute()
print("Document recomputed.")

# Fit the view to show the entire site plan
try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
    FreeCADGui.ActiveDocument.ActiveView.viewTop()
    print("View set to top-down, fit to extents.")
except Exception:
    print("GUI not available — skipping view adjustment.")


# ═══════════════════════════════════════════════════════════════════
# DXF EXPORT
# ═══════════════════════════════════════════════════════════════════

try:
    import importDXF

    # Collect all geometry objects (exclude group containers)
    export_objs = [
        o for o in doc.Objects
        if not o.isDerivedFrom("App::DocumentObjectGroup")
    ]

    importDXF.export(export_objs, DXF_PATH)
    print("=" * 50)
    print("DXF exported successfully!")
    print("File: {}".format(DXF_PATH))
    print("=" * 50)

except Exception as e:
    print("=" * 50)
    print("Automatic DXF export failed: {}".format(e))
    print("")
    print("Manual export steps:")
    print("  1. Select all objects in the Model tree")
    print("  2. File > Export...")
    print("  3. Choose 'Autodesk DXF 2D (*.dxf)' format")
    print("  4. Save to desired location")
    print("=" * 50)


# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════

print("")
print("SITE PLAN SUMMARY")
print("-" * 40)
print("Lot:          {}' x {}' (1 acre)".format(LOT_WIDTH, LOT_DEPTH))
print("House:        L-shaped, ~2,592 SF footprint")
print("              ~4,512 SF total (2 stories)")
print("Porch:        8' wrap-around (S+W) + 8' rear patio")
print("Garage:       24' x 28' detached (NE)")
print("Pool:         32' x 16' with 6' deck surround")
print("Driveway:     14' lane + 32' x 13' parking pad")
print("Trees:        {} placed".format(len(placed_trees)))
print("Layers:       {}".format(", ".join(LAYER_STYLE.keys())))
print("-" * 40)
print("Script complete.")
