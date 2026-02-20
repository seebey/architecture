# ===================================================================
# MODERN RUSTIC FARMHOUSE -- STRUCTURAL FRAMING LAYOUT
# FreeCAD Python Script (tested on FreeCAD 0.21+)
# ===================================================================
#
# Generates a 2D structural framing plan view showing:
#   - Column grids (crosses at grid intersections)
#   - Beam lines (continuous lines connecting columns)
#   - Ridge beams (centerline beams along each roof ridge)
#   - Concrete shear walls (thick rectangles at key partitions)
#   - Foundation outlines for all buildings
#   - Grid labels (column letters, row numbers)
#
# Buildings:
#   - Main House (L-shaped: primary bar E-W + wing extending N)
#   - Guest Pavilion (north of courtyard)
#   - Barn / Garage (rotated 10 deg CCW)
#   - Breezeway (HSS steel columns at corners)
#
# Usage: Paste entire script into FreeCAD's Python console,
#        or run via:  freecad -c farmhouse_structural.py
# Output: DXF file at ~/farmhouse_structural.dxf
#
# All dimensions specified in feet; converted to mm internally
# via farmhouse_params.py.
# ===================================================================

import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farmhouse_params import *


# ===================================================================
# DOCUMENT SETUP
# ===================================================================

doc = FreeCAD.newDocument("FarmhouseStructural")
print("Document created: FarmhouseStructural")

# -------------------------------------------------------------------
# Create layer groups
# -------------------------------------------------------------------
layer_names = ["STRUCTURE", "WALLS", "DIMS", "SITE"]

layers = {}
for name in layer_names:
    layers[name] = doc.addObject("App::DocumentObjectGroup", name)
print("Layer groups created: " + ", ".join(layer_names))


# ===================================================================
# STRUCTURAL GRID -- MAIN HOUSE (Primary Bar, E-W)
# ===================================================================
# Bar runs from x=68 to x=132 (64').
# Bay spacing = 12' with last bay widened to 16' for entry vestibule.
# Column lines: x = 68, 80, 92, 104, 116, 132
# Bays: 12, 12, 12, 12, 16

print("Drawing main house structural grid...")

main_col_x = [68, 80, 92, 104, 116, 132]
main_col_y = [MAIN_Y1, MAIN_Y2]  # [85, 115]

# --- Columns (drawn as crosses with 2' arm length) ---
for x in main_col_x:
    for y in main_col_y:
        make_line(x - 1, y, x + 1, y,
                  "Col_{0}_{1}_H".format(x, y), layers["STRUCTURE"], "STRUCTURE")
        make_line(x, y - 1, x, y + 1,
                  "Col_{0}_{1}_V".format(x, y), layers["STRUCTURE"], "STRUCTURE")

print("  Main bar columns: {} x {} = {} columns".format(
    len(main_col_x), len(main_col_y), len(main_col_x) * len(main_col_y)))

# --- Beam lines (continuous lines connecting columns) ---
# South beam line
make_line(68, MAIN_Y1, 132, MAIN_Y1,
          "Beam_MainBar_S", layers["STRUCTURE"], "STRUCTURE")
# North beam line
make_line(68, MAIN_Y2, 132, MAIN_Y2,
          "Beam_MainBar_N", layers["STRUCTURE"], "STRUCTURE")

print("  Main bar beam lines: south y={}, north y={}".format(MAIN_Y1, MAIN_Y2))

# --- Ridge beam (centerline of main bar) ---
ridge_y = (MAIN_Y1 + MAIN_Y2) / 2.0  # = 100
make_line(68, ridge_y, 132, ridge_y,
          "RidgeBeam_MainBar", layers["STRUCTURE"], "STRUCTURE")

print("  Main bar ridge beam: y={}".format(ridge_y))

# --- Steel ridge beam zone (great room, x=68 to x=92) ---
# The great room needs a steel ridge because of the 24' clear span
# at double height. Mark with a separate, labeled line.
steel_ridge = make_line(68, ridge_y, 92, ridge_y,
                        "SteelRidge_GreatRoom", layers["STRUCTURE"], "STRUCTURE")
try:
    steel_ridge.ViewObject.LineWidth = 4.0
    steel_ridge.ViewObject.LineColor = (0.80, 0.15, 0.10)
except Exception:
    pass

print("  Steel ridge beam zone: x=68 to x=92 (great room, 24' clear span)")

# --- Concrete shear walls (WALLS layer, heavy lines) ---

# Great room east wall (partition between great room and kitchen): x = 92
make_rect(92 - WALL_THICKNESS / 2.0, MAIN_Y1,
          92 + WALL_THICKNESS / 2.0, MAIN_Y2,
          "ShearWall_GreatRoom", layers["WALLS"], "WALLS")

# Entry vestibule east wall (wall between kitchen and entry): x = 120
make_rect(120 - WALL_THICKNESS / 2.0, MAIN_Y1,
          120 + WALL_THICKNESS / 2.0, MAIN_Y2,
          "ShearWall_Entry", layers["WALLS"], "WALLS")

print("  Shear walls: x=92 (great room), x=120 (entry vestibule)")


# ===================================================================
# STRUCTURAL GRID -- WING (N-S)
# ===================================================================
# Wing runs from y=115 to y=143 (28').
# Two 14' bays: y = 115, 129, 143.
# Column lines at x = WING_X1 = 108 and x = WING_X2 = 132.

print("Drawing wing structural grid...")

wing_col_y = [115, 129, 143]
wing_col_x = [WING_X1, WING_X2]  # [108, 132]

# --- Wing columns ---
for x in wing_col_x:
    for y in wing_col_y:
        make_line(x - 1, y, x + 1, y,
                  "Col_Wing_{0}_{1}_H".format(x, y), layers["STRUCTURE"], "STRUCTURE")
        make_line(x, y - 1, x, y + 1,
                  "Col_Wing_{0}_{1}_V".format(x, y), layers["STRUCTURE"], "STRUCTURE")

print("  Wing columns: {} x {} = {} columns".format(
    len(wing_col_x), len(wing_col_y), len(wing_col_x) * len(wing_col_y)))

# --- Wing beam lines ---
make_line(WING_X1, 115, WING_X1, 143,
          "Beam_Wing_W", layers["STRUCTURE"], "STRUCTURE")
make_line(WING_X2, 115, WING_X2, 143,
          "Beam_Wing_E", layers["STRUCTURE"], "STRUCTURE")

print("  Wing beam lines: west x={}, east x={}".format(WING_X1, WING_X2))

# --- Wing ridge beam ---
wing_ridge_x = (WING_X1 + WING_X2) / 2.0  # = 120
make_line(wing_ridge_x, 115, wing_ridge_x, 143,
          "RidgeBeam_Wing", layers["STRUCTURE"], "STRUCTURE")

print("  Wing ridge beam: x={}".format(wing_ridge_x))


# ===================================================================
# STRUCTURAL GRID -- GUEST PAVILION
# ===================================================================
# Bay spacing = 10'. Guest runs from x=60 to x=100 (40').
# Column lines: x = 60, 70, 80, 90, 100 (four 10' bays).
# Column lines at y = GUEST_Y1 = 151 and y = GUEST_Y2 = 171.

print("Drawing guest pavilion structural grid...")

guest_col_x = [60, 70, 80, 90, 100]
guest_col_y = [GUEST_Y1, GUEST_Y2]  # [151, 171]

# --- Guest columns ---
for x in guest_col_x:
    for y in guest_col_y:
        make_line(x - 1, y, x + 1, y,
                  "Col_Guest_{0}_{1}_H".format(x, y), layers["STRUCTURE"], "STRUCTURE")
        make_line(x, y - 1, x, y + 1,
                  "Col_Guest_{0}_{1}_V".format(x, y), layers["STRUCTURE"], "STRUCTURE")

print("  Guest columns: {} x {} = {} columns".format(
    len(guest_col_x), len(guest_col_y), len(guest_col_x) * len(guest_col_y)))

# --- Guest beam lines ---
make_line(60, GUEST_Y1, 100, GUEST_Y1,
          "Beam_Guest_S", layers["STRUCTURE"], "STRUCTURE")
make_line(60, GUEST_Y2, 100, GUEST_Y2,
          "Beam_Guest_N", layers["STRUCTURE"], "STRUCTURE")

print("  Guest beam lines: south y={}, north y={}".format(GUEST_Y1, GUEST_Y2))

# --- Guest ridge beam ---
guest_ridge_y = (GUEST_Y1 + GUEST_Y2) / 2.0  # = 161
make_line(60, guest_ridge_y, 100, guest_ridge_y,
          "RidgeBeam_Guest", layers["STRUCTURE"], "STRUCTURE")

print("  Guest ridge beam: y={}".format(guest_ridge_y))


# ===================================================================
# STRUCTURAL GRID -- BARN
# ===================================================================
# Bay spacing = 12'. Barn is 36' long (N-S before rotation), 26' wide.
# Column lines along length: every 12' = 3 bays.
# Rotated 10 deg CCW about (BARN_CX, BARN_CY).

print("Drawing barn structural grid...")

rad = math.radians(BARN_ROTATION)
cos_a = math.cos(rad)
sin_a = math.sin(rad)


def barn_pt(local_x, local_y):
    """Transform barn-local coords to world coords."""
    rx = BARN_CX + local_x * cos_a - local_y * sin_a
    ry = BARN_CY + local_x * sin_a + local_y * cos_a
    return (rx, ry)


# Barn column positions (local coords, centered at origin)
barn_col_y_local = [-18, -6, 6, 18]   # every 12' along 36' length
barn_col_x_local = [-13, 13]          # at each side of 26' width

# --- Barn columns ---
for lx in barn_col_x_local:
    for ly in barn_col_y_local:
        wx, wy = barn_pt(lx, ly)
        make_line(wx - 1, wy, wx + 1, wy,
                  "Col_Barn_{0}_{1}_H".format(lx, ly), layers["STRUCTURE"], "STRUCTURE")
        make_line(wx, wy - 1, wx, wy + 1,
                  "Col_Barn_{0}_{1}_V".format(lx, ly), layers["STRUCTURE"], "STRUCTURE")

print("  Barn columns: {} x {} = {} columns".format(
    len(barn_col_x_local), len(barn_col_y_local),
    len(barn_col_x_local) * len(barn_col_y_local)))

# --- Barn beam lines (connect columns along each wall) ---
for lx in barn_col_x_local:
    p1 = barn_pt(lx, -18)
    p2 = barn_pt(lx, 18)
    make_line(p1[0], p1[1], p2[0], p2[1],
              "Beam_Barn_{0}".format(lx), layers["STRUCTURE"], "STRUCTURE")

print("  Barn beam lines: two side beams along rotated walls")

# --- Barn ridge beam (along center, lx=0) ---
r1 = barn_pt(0, -18)
r2 = barn_pt(0, 18)
make_line(r1[0], r1[1], r2[0], r2[1],
          "RidgeBeam_Barn", layers["STRUCTURE"], "STRUCTURE")

print("  Barn ridge beam: center of rotated barn")


# ===================================================================
# BREEZEWAY STRUCTURE
# ===================================================================
# HSS steel columns at four corners (smaller crosses, 0.5' arm length).

print("Drawing breezeway structure...")

bw_corners = [(BW_X1, BW_Y1), (BW_X2, BW_Y1), (BW_X1, BW_Y2), (BW_X2, BW_Y2)]
for i, (x, y) in enumerate(bw_corners):
    make_line(x - 0.5, y, x + 0.5, y,
              "Col_BW_{0}_H".format(i), layers["STRUCTURE"], "STRUCTURE")
    make_line(x, y - 0.5, x, y + 0.5,
              "Col_BW_{0}_V".format(i), layers["STRUCTURE"], "STRUCTURE")

print("  Breezeway HSS columns: {} corners".format(len(bw_corners)))


# ===================================================================
# FOUNDATION OUTLINES (SITE layer)
# ===================================================================
# Lighter weight outlines showing the perimeter of each building's
# foundation / slab on grade.

print("Drawing foundation outlines...")

# --- Main house L-shape foundation ---
house_fdn_pts = [
    (MAIN_X1, MAIN_Y1),   # SW corner of bar (68, 85)
    (MAIN_X2, MAIN_Y1),   # SE corner of bar (132, 85)
    (MAIN_X2, WING_Y2),   # NE corner of wing (132, 143)
    (WING_X1, WING_Y2),   # NW corner of wing (108, 143)
    (WING_X1, MAIN_Y2),   # inside corner of L (108, 115)
    (MAIN_X1, MAIN_Y2),   # NW corner of bar (68, 115)
]
make_closed_wire(house_fdn_pts, "Foundation_MainHouse", layers["SITE"], "SITE")
print("  Main house foundation: L-shaped")

# --- Guest pavilion foundation ---
make_rect(GUEST_X1, GUEST_Y1, GUEST_X2, GUEST_Y2,
          "Foundation_Guest", layers["SITE"], "SITE")
print("  Guest pavilion foundation: rectangle")

# --- Barn foundation (rotated rectangle) ---
make_rotated_rect(BARN_CX, BARN_CY, BARN_LENGTH, BARN_WIDTH, BARN_ROTATION,
                  "Foundation_Barn", layers["SITE"], "SITE")
print("  Barn foundation: rotated rectangle")

# --- Breezeway foundation ---
make_rect(BW_X1, BW_Y1, BW_X2, BW_Y2,
          "Foundation_Breezeway", layers["SITE"], "SITE")
print("  Breezeway foundation: rectangle")


# ===================================================================
# GRID LABELS (DIMS layer)
# ===================================================================
# Label column lines for the main bar grid:
#   - Letters A-F for x positions (column lines)
#   - Numbers 1-2 for y positions (row lines)

print("Drawing grid labels...")

grid_letters = ["A", "B", "C", "D", "E", "F"]
label_offset_y = 3.0  # feet below south beam line for column labels

for i, x in enumerate(main_col_x):
    label = grid_letters[i]
    txt = Draft.make_text([label], v(x - 0.5, MAIN_Y1 - label_offset_y))
    txt.Label = "GridLabel_{0}".format(label)
    layers["DIMS"].addObject(txt)
    apply_style(txt, "DIMS")

grid_numbers = ["1", "2"]
label_offset_x = 3.0  # feet west of west column line for row labels

for i, y in enumerate(main_col_y):
    label = grid_numbers[i]
    txt = Draft.make_text([label], v(main_col_x[0] - label_offset_x, y - 0.5))
    txt.Label = "GridLabel_{0}".format(label)
    layers["DIMS"].addObject(txt)
    apply_style(txt, "DIMS")

print("  Grid labels: {} column lines (A-F), {} row lines (1-2)".format(
    len(grid_letters), len(grid_numbers)))


# ===================================================================
# RECOMPUTE AND FIT VIEW
# ===================================================================

doc.recompute()
print("Document recomputed.")

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

export_dxf(doc, "farmhouse_structural.dxf")


# ===================================================================
# SUMMARY
# ===================================================================

print("")
print("=" * 60)
print("STRUCTURAL FRAMING LAYOUT SUMMARY")
print("=" * 60)
print("")
print("MAIN HOUSE (Primary Bar, E-W):")
print("  Column grid:    {} cols x {} rows = {} columns".format(
    len(main_col_x), len(main_col_y), len(main_col_x) * len(main_col_y)))
print("  Column lines:   x = {}".format(main_col_x))
print("  Bay spacing:    12, 12, 12, 12, 16 ft")
print("  Beam lines:     south y={}, north y={}".format(MAIN_Y1, MAIN_Y2))
print("  Ridge beam:     y={} (glulam)".format(ridge_y))
print("  Steel ridge:    x=68 to x=92 (great room, 24' clear span)")
print("  Shear walls:    x=92 (great room E), x=120 (entry)")
print("")
print("WING (N-S):")
print("  Column grid:    {} cols x {} rows = {} columns".format(
    len(wing_col_x), len(wing_col_y), len(wing_col_x) * len(wing_col_y)))
print("  Column lines:   y = {}".format(wing_col_y))
print("  Bay spacing:    14, 14 ft")
print("  Beam lines:     west x={}, east x={}".format(WING_X1, WING_X2))
print("  Ridge beam:     x={}".format(wing_ridge_x))
print("")
print("GUEST PAVILION:")
print("  Column grid:    {} cols x {} rows = {} columns".format(
    len(guest_col_x), len(guest_col_y), len(guest_col_x) * len(guest_col_y)))
print("  Column lines:   x = {}".format(guest_col_x))
print("  Bay spacing:    10, 10, 10, 10 ft")
print("  Beam lines:     south y={}, north y={}".format(GUEST_Y1, GUEST_Y2))
print("  Ridge beam:     y={}".format(guest_ridge_y))
print("")
print("BARN (rotated {}deg CCW):".format(BARN_ROTATION))
print("  Column grid:    {} cols x {} rows = {} columns".format(
    len(barn_col_x_local), len(barn_col_y_local),
    len(barn_col_x_local) * len(barn_col_y_local)))
print("  Bay spacing:    12, 12, 12 ft (along length)")
print("  Center:         ({}, {}), rotation {}deg".format(
    BARN_CX, BARN_CY, BARN_ROTATION))
print("")
print("BREEZEWAY:")
print("  HSS columns:    {} corner columns".format(len(bw_corners)))
print("")
print("FOUNDATIONS:")
print("  Main house:     L-shaped outline")
print("  Guest pavilion: rectangle")
print("  Barn:           rotated rectangle")
print("  Breezeway:      rectangle")
print("")
print("Layers:           {}".format(", ".join(layer_names)))
print("Export:           ~/farmhouse_structural.dxf")
print("=" * 60)
print("Script complete.")
