# ===================================================================
# MODERN RUSTIC FARMHOUSE -- FLOOR PLANS (GROUND + UPPER)
# FreeCAD Python Script (tested on FreeCAD 0.21+)
# ===================================================================
#
# Generates two floor plan views for the farmhouse courtyard compound:
#   - Ground Floor: all buildings with interior walls, room labels,
#                   windows, and stair indication
#   - Upper Floor:  offset 250' in Y, showing second-level rooms
#                   over the east half of main bar and wing
#
# Usage: Paste entire script into FreeCAD's Python console,
#        or run via:  freecad -c farmhouse_floor_plans.py
# Output: DXF file at ~/farmhouse_floor_plans.dxf
#
# All dimensions specified in feet; converted to mm internally
# via farmhouse_params.py.
# ===================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farmhouse_params import *

import math


# ===================================================================
# LOCAL PARAMETERS
# ===================================================================

UPPER_FLOOR_Y_OFFSET = 250  # ft, shift upper floor plan upward in document


# ===================================================================
# HELPER FUNCTIONS
# ===================================================================

def make_label(text, x_ft, y_ft, group):
    """Place a text label at (x, y) in feet."""
    t = Draft.make_text([text], v(x_ft, y_ft))
    t.Label = "Label_" + text.replace(" ", "_")
    group.addObject(t)
    try:
        t.ViewObject.FontSize = 600  # mm (about 2' at scale)
    except Exception:
        pass
    return t


# ===================================================================
# DOCUMENT SETUP
# ===================================================================

doc = FreeCAD.newDocument("FarmhouseFloorPlans")
print("Document created: FarmhouseFloorPlans")

# -------------------------------------------------------------------
# Create layer groups
# -------------------------------------------------------------------
layer_names = ["WALLS", "GLAZING", "STRUCTURE", "DIMS", "SITE"]

layers = {}
for name in layer_names:
    layers[name] = doc.addObject("App::DocumentObjectGroup", name)
print("Layer groups created: " + ", ".join(layer_names))


# ===================================================================
# GROUND FLOOR PLAN
# ===================================================================
print("")
print("--- GROUND FLOOR PLAN ---")

# -------------------------------------------------------------------
# 1. EXTERIOR WALLS
# -------------------------------------------------------------------

# Main house L-shaped outline (same 6-point polygon as site plan)
house_pts = [
    (MAIN_X1, MAIN_Y1),   # SW corner of bar (68, 85)
    (MAIN_X2, MAIN_Y1),   # SE corner of bar (132, 85)
    (MAIN_X2, WING_Y2),   # NE corner of wing (132, 143)
    (WING_X1, WING_Y2),   # NW corner of wing (108, 143)
    (WING_X1, MAIN_Y2),   # inside corner of L (108, 115)
    (MAIN_X1, MAIN_Y2),   # NW corner of bar (68, 115)
]
make_closed_wire(house_pts, "GF_Main_House", layers["WALLS"], "WALLS")
print("Main house outline created")

# Guest pavilion rectangle
make_rect(GUEST_X1, GUEST_Y1, GUEST_X2, GUEST_Y2,
          "GF_Guest_Pavilion", layers["WALLS"], "WALLS")
print("Guest pavilion outline created")

# Barn rectangle (rotated)
make_rotated_rect(BARN_CX, BARN_CY, BARN_LENGTH, BARN_WIDTH, BARN_ROTATION,
                  "GF_Barn", layers["WALLS"], "WALLS")
print("Barn outline created (rotated {}deg)".format(BARN_ROTATION))

# Breezeway rectangle
make_rect(BW_X1, BW_Y1, BW_X2, BW_Y2,
          "GF_Breezeway", layers["WALLS"], "WALLS")
print("Breezeway outline created")


# -------------------------------------------------------------------
# 2. INTERIOR WALLS -- MAIN BAR
# -------------------------------------------------------------------

# Wall between great room and kitchen at x = 92
make_line(92, MAIN_Y1, 92, MAIN_Y2,
          "GF_Wall_GreatRoom_Kitchen", layers["WALLS"], "WALLS")
print("Interior wall: great room / kitchen at x=92")

# Wall between kitchen and entry at x = 120
make_line(120, MAIN_Y1, 120, MAIN_Y2,
          "GF_Wall_Kitchen_Entry", layers["WALLS"], "WALLS")
print("Interior wall: kitchen / entry at x=120")

# Entry door on east face: indicate as gap in east wall (centered, 4' wide)
# The east wall of the entry runs from (132, 85) to (132, 115)
# Center of east wall at y = 100, gap from y=98 to y=102
# Draw east wall as two segments with gap
make_line(132, MAIN_Y1, 132, 98,
          "GF_Entry_East_Wall_S", layers["WALLS"], "WALLS")
make_line(132, 102, 132, MAIN_Y2,
          "GF_Entry_East_Wall_N", layers["WALLS"], "WALLS")
print("Entry door gap on east wall (4' wide centered)")


# -------------------------------------------------------------------
# 3. INTERIOR WALLS -- WING (LIBRARY / STAIR)
# -------------------------------------------------------------------

# Stair in SW corner of wing: 4' x 10' rectangle
# x = 108 to 112, y = 115 to 125
make_rect(108, 115, 112, 125,
          "GF_Stair_Outline", layers["WALLS"], "WALLS")

# Stair diagonal lines indicating stairs (treads)
# Draw diagonal from SW to NE of stair rectangle
make_line(108, 115, 112, 125,
          "GF_Stair_Diag1", layers["STRUCTURE"], "STRUCTURE")
make_line(112, 115, 108, 125,
          "GF_Stair_Diag2", layers["STRUCTURE"], "STRUCTURE")
print("Stair indicated in wing SW corner (4' x 10')")


# -------------------------------------------------------------------
# 4. INTERIOR WALLS -- GUEST PAVILION
# -------------------------------------------------------------------

# Central dividing wall at x = 80 (splits into two 20'x20' bedrooms)
make_line(80, GUEST_Y1, 80, GUEST_Y2,
          "GF_Guest_Central_Wall", layers["WALLS"], "WALLS")
print("Guest pavilion: central dividing wall at x=80")

# West bathroom: x = 60 to 70, y = 163 to 171 (10' x 8')
make_line(60, 163, 70, 163,
          "GF_Guest_WBath_S", layers["WALLS"], "WALLS")
make_line(70, 163, 70, 171,
          "GF_Guest_WBath_E", layers["WALLS"], "WALLS")
print("Guest pavilion: west bathroom walls (10' x 8')")

# East bathroom: x = 80 to 90, y = 163 to 171 (10' x 8')
make_line(80, 163, 90, 163,
          "GF_Guest_EBath_S", layers["WALLS"], "WALLS")
make_line(90, 163, 90, 171,
          "GF_Guest_EBath_E", layers["WALLS"], "WALLS")
print("Guest pavilion: east bathroom walls (10' x 8')")


# -------------------------------------------------------------------
# 5. INTERIOR WALLS -- BARN
# -------------------------------------------------------------------

# Barn interior wall at 24' from south end (separating garage from workshop)
# The barn's long axis is Y (before rotation), so the wall runs E-W
# at y_offset = -BARN_LENGTH/2 + 24 = +6 from center
rad = math.radians(BARN_ROTATION)
cos_a = math.cos(rad)
sin_a = math.sin(rad)

# Wall endpoints (relative to center, before rotation)
wall_dy = -BARN_LENGTH / 2 + 24  # = +6 from center
wall_x1_rel, wall_y1_rel = -BARN_WIDTH / 2, wall_dy
wall_x2_rel, wall_y2_rel = BARN_WIDTH / 2, wall_dy

# Rotate and translate
bw_x1 = BARN_CX + wall_x1_rel * cos_a - wall_y1_rel * sin_a
bw_y1 = BARN_CY + wall_x1_rel * sin_a + wall_y1_rel * cos_a
bw_x2 = BARN_CX + wall_x2_rel * cos_a - wall_y2_rel * sin_a
bw_y2 = BARN_CY + wall_x2_rel * sin_a + wall_y2_rel * cos_a
make_line(bw_x1, bw_y1, bw_x2, bw_y2,
          "Barn_Interior_Wall", layers["WALLS"], "WALLS")
print("Barn interior wall: garage / workshop divider")


# -------------------------------------------------------------------
# 6. WINDOWS (GLAZING LAYER)
# -------------------------------------------------------------------

# Great room west gable: full width glazing line at x = 68
make_line(68, MAIN_Y1 + 2, 68, MAIN_Y2 - 2,
          "GF_Win_GreatRoom_West", layers["GLAZING"], "GLAZING")
print("Window: great room west gable glazing")

# Kitchen south windows: line segment at y = MAIN_Y1, from x = 95 to 115
make_line(95, MAIN_Y1, 115, MAIN_Y1,
          "GF_Win_Kitchen_South", layers["GLAZING"], "GLAZING")
print("Window: kitchen south windows")

# Library east window: line at x = 132, from y = 120 to 138
make_line(132, 120, 132, 138,
          "GF_Win_Library_East", layers["GLAZING"], "GLAZING")
print("Window: library east window")


# -------------------------------------------------------------------
# 7. ROOM LABELS -- GROUND FLOOR
# -------------------------------------------------------------------

# Great Room: x = 68 to 92, y = 85 to 115 -> center (80, 100)
make_label("GREAT ROOM", 80, 100, layers["DIMS"])

# Kitchen: x = 92 to 120 (west half ~92-106), y = 85 to 115
# center of kitchen area roughly at (100, 95)
make_label("KITCHEN", 100, 93, layers["DIMS"])

# Dining: east part of kitchen/dining zone, roughly at (106, 105)
make_label("DINING", 106, 105, layers["DIMS"])

# Entry: x = 120 to 132, y = 85 to 115 -> center (126, 100)
make_label("ENTRY", 126, 100, layers["DIMS"])

# Library: wing ground floor x = 108 to 132, y = 115 to 143 -> center (120, 129)
make_label("LIBRARY", 120, 130, layers["DIMS"])

# Guest BR 1 (west): x = 60 to 80, y = 151 to 171 -> center (70, 158)
make_label("GUEST BR 1", 65, 158, layers["DIMS"])

# Guest BR 2 (east): x = 80 to 100, y = 151 to 171 -> center (90, 158)
make_label("GUEST BR 2", 85, 158, layers["DIMS"])

# Garage (south portion of barn) and Workshop (north portion)
# Barn center is (155, 100). Garage is south 24', workshop north 12'
# Garage center approx: (155, 100 - 6) = (155, 94)
# Workshop center approx: (155, 100 + 9) = (155, 109)
make_label("GARAGE", 153, 92, layers["DIMS"])
make_label("WORKSHOP", 153, 109, layers["DIMS"])

# Studio loft label in barn
make_label("STUDIO LOFT (ABOVE)", 149, 103, layers["DIMS"])

# Courtyard center: x = (60+108)/2 = 84, y = (115+151)/2 = 133
make_label("COURTYARD", 78, 133, layers["DIMS"])

print("Ground floor room labels placed")


# ===================================================================
# UPPER FLOOR PLAN
# ===================================================================
print("")
print("--- UPPER FLOOR PLAN ---")

uy = UPPER_FLOOR_Y_OFFSET  # add to all y coordinates

# -------------------------------------------------------------------
# 1. UPPER FLOOR OUTLINE (L-shaped, no great room)
# -------------------------------------------------------------------

upper_pts = [
    (92, MAIN_Y1 + uy),       # SW
    (MAIN_X2, MAIN_Y1 + uy),  # SE
    (MAIN_X2, WING_Y2 + uy),  # NE (wing)
    (WING_X1, WING_Y2 + uy),  # NW (wing)
    (WING_X1, MAIN_Y2 + uy),  # inside corner
    (92, MAIN_Y2 + uy),       # NW of upper bar
]
make_closed_wire(upper_pts, "UF_Outline", layers["WALLS"], "WALLS")
print("Upper floor outline created (L-shape, no great room)")


# -------------------------------------------------------------------
# 2. GREAT ROOM VOID (dashed rectangle)
# -------------------------------------------------------------------

# Dashed rectangle from x=68 to 92, MAIN_Y1 to MAIN_Y2 (with Y offset)
void_wire = make_rect(68, MAIN_Y1 + uy, 92, MAIN_Y2 + uy,
                      "UF_GreatRoom_Void", layers["WALLS"], "WALLS")
try:
    void_wire.ViewObject.DrawStyle = "Dashed"
    void_wire.ViewObject.LineWidth = 1.0
except Exception:
    pass
print("Great room void indicated (dashed outline)")


# -------------------------------------------------------------------
# 3. UPPER FLOOR INTERIOR WALLS
# -------------------------------------------------------------------

# Wall at bottom of primary suite / top of main bar east section
# Primary Suite: x = 108 to 132, y = 85 to 115 (upper)
# The wing wall at y=115 is already part of the outline L-shape,
# but we need to extend a wall from x=92 to x=108 at y=115
# (this is the hallway/wing boundary -- already in outline at inside corner)

# Wall between hallway (x=92-108) and primary suite (x=108-132) at x=108
# from y = 85 to y = 115
make_line(108, MAIN_Y1 + uy, 108, MAIN_Y2 + uy,
          "UF_Wall_Hallway_Primary", layers["WALLS"], "WALLS")
print("Upper floor wall: hallway / primary suite at x=108")

# Primary Suite ensuite bath in SE corner: x = 122 to 132, y = 85 to 97
make_line(122, MAIN_Y1 + uy, 122, 97 + uy,
          "UF_PrimaryBath_W", layers["WALLS"], "WALLS")
make_line(122, 97 + uy, MAIN_X2, 97 + uy,
          "UF_PrimaryBath_N", layers["WALLS"], "WALLS")
print("Upper floor: primary suite ensuite bath walls (10' x 12')")

# Bedroom 3 / Study: x = 108 to 132, y = 115 to 125 (upper)
# Wall at y = 125 (between bedroom 3 and bedroom 2)
make_line(WING_X1, 125 + uy, WING_X2, 125 + uy,
          "UF_Wall_Bed3_Bed2", layers["WALLS"], "WALLS")
print("Upper floor wall: bedroom 3 / bedroom 2 at y=125")

# Wall at y = 115 between wing rooms and main bar is already
# part of the outline (inside corner). But we need the wall segment
# from x=108 to x=132 at y=115 to separate wing upper from hallway.
# The outline already has the inside corner at (108, 115+uy),
# and the hallway/primary wall at x=108 handles the separation.

# Bedroom 2 bath in NE corner: x = 122 to 132, y = 135 to 143
make_line(122, 135 + uy, 122, WING_Y2 + uy,
          "UF_Bed2Bath_W", layers["WALLS"], "WALLS")
make_line(122, 135 + uy, WING_X2, 135 + uy,
          "UF_Bed2Bath_S", layers["WALLS"], "WALLS")
print("Upper floor: bedroom 2 bath walls (10' x 8')")

# Stair landing: x = 108 to 112, y = 115 to 125 (same position as ground)
make_rect(108, 115 + uy, 112, 125 + uy,
          "UF_Stair_Landing", layers["WALLS"], "WALLS")
# Stair diagonal indicators
make_line(108, 115 + uy, 112, 125 + uy,
          "UF_Stair_Diag1", layers["STRUCTURE"], "STRUCTURE")
make_line(112, 115 + uy, 108, 125 + uy,
          "UF_Stair_Diag2", layers["STRUCTURE"], "STRUCTURE")
print("Upper floor: stair landing indicated")


# -------------------------------------------------------------------
# 4. INTERIOR BALCONY
# -------------------------------------------------------------------

# Interior Balcony: x = 88 to 92, y = 90 to 110 (4' x 20')
# Overlooks great room. Open side at x = 88 drawn dashed.
make_line(88, 90 + uy, 88, 110 + uy,
          "UF_Balcony_Open", layers["WALLS"], "WALLS")
make_line(88, 90 + uy, 92, 90 + uy,
          "UF_Balcony_S", layers["WALLS"], "WALLS")
make_line(88, 110 + uy, 92, 110 + uy,
          "UF_Balcony_N", layers["WALLS"], "WALLS")

# Set dashed style on the open side (x = 88 line)
try:
    balcony_open = doc.getObject("UF_Balcony_Open")
    if balcony_open:
        balcony_open.ViewObject.DrawStyle = "Dashed"
        balcony_open.ViewObject.LineWidth = 1.0
except Exception:
    pass
print("Upper floor: interior balcony (4' x 20') with dashed open side")


# -------------------------------------------------------------------
# 5. ROOM LABELS -- UPPER FLOOR
# -------------------------------------------------------------------

# Primary Suite: x = 108 to 132, y = 85 to 115 -> center (120, 100)
make_label("PRIMARY SUITE", 114, 103 + uy, layers["DIMS"])

# Ensuite: (122 to 132, 85 to 97) -> center (127, 91)
make_label("ENSUITE", 125, 90 + uy, layers["DIMS"])

# Bedroom 2: x = 108 to 132, y = 125 to 143 -> center (120, 134)
make_label("BEDROOM 2", 115, 131 + uy, layers["DIMS"])

# Bedroom 2 bath: (122-132, 135-143) -> center (127, 139)
make_label("BATH", 125, 138 + uy, layers["DIMS"])

# Bedroom 3 / Study: x = 108 to 132, y = 115 to 125 -> center (120, 120)
make_label("BED 3 / STUDY", 115, 119 + uy, layers["DIMS"])

# Hallway: x = 92 to 108, y = 85 to 115 -> center (100, 100)
make_label("HALLWAY", 97, 100 + uy, layers["DIMS"])

# Interior Balcony label
make_label("BALCONY", 88, 100 + uy, layers["DIMS"])

# Great room void label
make_label("VOID (GREAT RM)", 73, 100 + uy, layers["DIMS"])

print("Upper floor room labels placed")


# ===================================================================
# RECOMPUTE AND FIT VIEW
# ===================================================================

doc.recompute()
print("")
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

export_dxf(doc, "farmhouse_floor_plans.dxf")


# ===================================================================
# SUMMARY
# ===================================================================

print("")
print("=" * 60)
print("FARMHOUSE FLOOR PLANS SUMMARY")
print("=" * 60)
print("")
print("GROUND FLOOR:")
print("  Main Bar (64' x 30'):")
print("    Great Room:     24' x 30'  (x=68..92)")
print("    Kitchen/Dining: 28' x 30'  (x=92..120)")
print("    Entry Vestibule:12' x 30'  (x=120..132)")
print("  Wing (24' x 28'):")
print("    Library:        full wing footprint")
print("    Stair:          4' x 10'   (SW corner)")
print("  Guest Pavilion (40' x 20'):")
print("    Guest BR 1:     20' x 20'  (west)")
print("    Guest BR 2:     20' x 20'  (east)")
print("    Bathrooms:      10' x 8'   (each, north)")
print("  Barn (36' x 26', rotated 10deg):")
print("    Garage:         26' x 24'  (south)")
print("    Workshop:       26' x 12'  (north)")
print("")
print("UPPER FLOOR (offset {}' in Y):".format(UPPER_FLOOR_Y_OFFSET))
print("  Primary Suite:    24' x 30'  (x=108..132, y=85..115)")
print("    Ensuite Bath:   10' x 12'  (SE corner)")
print("  Bedroom 2:        24' x 18'  (x=108..132, y=125..143)")
print("    Bath:           10' x 8'   (NE corner)")
print("  Bed 3 / Study:    24' x 10'  (x=108..132, y=115..125)")
print("  Hallway:          16' x 30'  (x=92..108)")
print("  Interior Balcony: 4' x 20'   (overlooks great room)")
print("  Great Room Void:  24' x 30'  (dashed, open to below)")
print("")
print("Layers: " + ", ".join(layer_names))
print("Export: ~/farmhouse_floor_plans.dxf")
print("=" * 60)
print("Script complete.")
