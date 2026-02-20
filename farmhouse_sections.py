# ===================================================================
# MODERN RUSTIC FARMHOUSE -- BUILDING SECTIONS (2 KEY CUTS)
# FreeCAD Python Script (tested on FreeCAD 0.21+)
# ===================================================================
#
# Generates two architectural section views revealing the interior
# spatial experience of the farmhouse courtyard compound:
#
#   Section A: Longitudinal Section (E-W through Main Bar)
#              Cut at y ~= 100 (center of main bar), looking NORTH.
#              Shows the compression-release sequence:
#              low entry (7.5') -> kitchen (9.5') -> great room (22')
#
#   Section B: Cross Section (N-S through Wing Intersection)
#              Cut at x = 110, looking WEST.
#              Shows main bar gable, wing, courtyard, guest pavilion,
#              and the clerestory seam between main bar and wing roofs.
#
# Each section is drawn in 2D:
#   Horizontal axis = position along cut direction
#   Vertical axis   = height (Z)
#
# Usage: Paste entire script into FreeCAD's Python console,
#        or run via:  freecad -c farmhouse_sections.py
# Output: DXF file at ~/farmhouse_sections.dxf
#
# All dimensions specified in feet; converted to mm internally
# via farmhouse_params.py.
# ===================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farmhouse_params import *


# ===================================================================
# HELPER FUNCTIONS
# ===================================================================

def draw_at(x_off, y_off):
    """Return a function that translates (h, v) to document coordinates."""
    def pos(h, v):
        return (h + x_off, v + y_off)
    return pos


def make_label(text, x_ft, y_ft, group, layer_name="DIMS"):
    """Place a text label at (x, y) in feet."""
    t = Draft.make_text([text], v(x_ft, y_ft))
    t.Label = "Label_" + text.replace(" ", "_").replace("'", "").replace('"', '')
    group.addObject(t)
    apply_style(t, layer_name)
    try:
        t.ViewObject.FontSize = 600  # mm (about 2' at scale)
    except Exception:
        pass
    return t


def sect_line(x1, y1, x2, y2, label, group, layer_name):
    """Draw a single line segment in document feet coordinates."""
    vectors = [v(x1, y1), v(x2, y2)]
    wire = Draft.make_wire(vectors, closed=False, face=False)
    wire.Label = label
    group.addObject(wire)
    apply_style(wire, layer_name)
    return wire


def sect_open_wire(pts_ft, label, group, layer_name):
    """Create an open wire from (h, v) tuples already in document space."""
    vectors = [v(x, y) for x, y in pts_ft]
    wire = Draft.make_wire(vectors, closed=False, face=False)
    wire.Label = label
    group.addObject(wire)
    apply_style(wire, layer_name)
    return wire


def sect_closed_wire(pts_ft, label, group, layer_name):
    """Create a closed wire from (h, v) tuples already in document space."""
    vectors = [v(x, y) for x, y in pts_ft]
    wire = Draft.make_wire(vectors, closed=True, face=False)
    wire.Label = label
    group.addObject(wire)
    apply_style(wire, layer_name)
    return wire


def sect_rect(x1, y1, x2, y2, label, group, layer_name):
    """Draw a rectangle from two corners in document feet coordinates."""
    pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    return sect_closed_wire(pts, label, group, layer_name)


# ===================================================================
# DOCUMENT SETUP
# ===================================================================

doc = FreeCAD.newDocument("FarmhouseSections")
print("Document created: FarmhouseSections")

# -------------------------------------------------------------------
# Create layer groups
# -------------------------------------------------------------------
layer_names = ["SECTION_CUT", "SECTION_BG", "GLAZING", "STRUCTURE", "DIMS"]

layers = {}
for name in layer_names:
    layers[name] = doc.addObject("App::DocumentObjectGroup", name)
print("Layer groups created: " + ", ".join(layer_names))


# ===================================================================
# SECTION PLACEMENT OFFSETS (feet)
# ===================================================================

SEC_A_X_OFF, SEC_A_Y_OFF = 0, 0       # Section A at origin
SEC_B_X_OFF, SEC_B_Y_OFF = 0, -80     # Section B below Section A


# ===================================================================
# SECTION A: LONGITUDINAL SECTION (E-W THROUGH MAIN BAR)
# ===================================================================
#
# Cut plane: runs E-W through the CENTER of the main bar at y = 100.
# Looking NORTH.
#
# Horizontal axis = X position (68 to 132+)
# Vertical axis   = Z height (-8 to 24)
#
# This section tells the story of COMPRESSION -> RELEASE:
#   low entry (7.5') -> kitchen (9.5') -> explosive double-height
#   great room (22')
# ===================================================================

print("")
print("=" * 60)
print("--- SECTION A: LONGITUDINAL (E-W THROUGH MAIN BAR) ---")
print("=" * 60)

P = draw_at(SEC_A_X_OFF, SEC_A_Y_OFF)

# === SECTION CUT elements (heavy lines) ===

# 1. Foundation / grade line at z=0
sect_line(*P(65, 0), *P(135, 0),
          "A_Grade", layers["SECTION_CUT"], "SECTION_CUT")
print("  Grade line")

# 2. West exterior wall: vertical at x=68, z=0 to eave height (12')
sect_line(*P(MAIN_X1, 0), *P(MAIN_X1, MAIN_EAVE_HEIGHT),
          "A_West_Wall", layers["SECTION_CUT"], "SECTION_CUT")
print("  West exterior wall")

# 3. East exterior wall: vertical at x=132, z=0 to eave height (12')
sect_line(*P(MAIN_X2, 0), *P(MAIN_X2, MAIN_EAVE_HEIGHT),
          "A_East_Wall", layers["SECTION_CUT"], "SECTION_CUT")
print("  East exterior wall")

# 4. Interior wall between great room and kitchen at x=92
sect_line(*P(92, 0), *P(92, MAIN_EAVE_HEIGHT),
          "A_GreatRoom_Kitchen_Wall", layers["SECTION_CUT"], "SECTION_CUT")
print("  Interior wall: great room / kitchen at x=92")

# 5. Interior wall between kitchen and entry at x=120
sect_line(*P(120, 0), *P(120, MAIN_EAVE_HEIGHT),
          "A_Kitchen_Entry_Wall", layers["SECTION_CUT"], "SECTION_CUT")
print("  Interior wall: kitchen / entry at x=120")

# 6. Second floor slab from x=92 to x=132 at z=FLOOR_TO_FLOOR (10.5')
sect_line(*P(92, FLOOR_TO_FLOOR), *P(MAIN_X2, FLOOR_TO_FLOOR),
          "A_Second_Floor_Slab", layers["SECTION_CUT"], "SECTION_CUT")
print("  Second floor slab at z={:.1f}'".format(FLOOR_TO_FLOOR))

# 7. Roof profile: cut is at ridge center (y=100), so roof is at
#    MAIN_RIDGE_HEIGHT (22'). Draw horizontal ridge beam line.
sect_line(*P(MAIN_X1, MAIN_RIDGE_HEIGHT), *P(MAIN_X2, MAIN_RIDGE_HEIGHT),
          "A_Ridge_Beam", layers["SECTION_CUT"], "SECTION_CUT")
print("  Ridge beam at z={:.0f}'".format(MAIN_RIDGE_HEIGHT))

# --- Below Grade: Wine Cellar ---

# 8-10. Wine cellar below the wing portion (x=108 to 132)
#       Floor at z = -WINE_CELLAR_CEILING (-7')
#       Cellar walls down from z=0 to z=-7

# Cellar west wall: vertical at x=108 from z=0 to z=-7
sect_line(*P(108, 0), *P(108, -WINE_CELLAR_CEILING),
          "A_Cellar_Wall_West", layers["SECTION_CUT"], "SECTION_CUT")
# Cellar east wall: vertical at x=132 from z=0 to z=-7
sect_line(*P(MAIN_X2, 0), *P(MAIN_X2, -WINE_CELLAR_CEILING),
          "A_Cellar_Wall_East", layers["SECTION_CUT"], "SECTION_CUT")
# Cellar floor: horizontal at z=-7 from x=108 to x=132
sect_line(*P(108, -WINE_CELLAR_CEILING), *P(MAIN_X2, -WINE_CELLAR_CEILING),
          "A_Cellar_Floor", layers["SECTION_CUT"], "SECTION_CUT")
print("  Wine cellar: floor at z=-{:.0f}'".format(WINE_CELLAR_CEILING))


# === SECTION BACKGROUND elements (lighter lines) ===

# 11. North exterior wall outline (behind the cut)
#     Drawn as lighter vertical lines at the same x extent
sect_line(*P(MAIN_X1, 0), *P(MAIN_X1, MAIN_EAVE_HEIGHT),
          "A_North_Wall_West_BG", layers["SECTION_BG"], "SECTION_BG")
sect_line(*P(MAIN_X2, 0), *P(MAIN_X2, MAIN_EAVE_HEIGHT),
          "A_North_Wall_East_BG", layers["SECTION_BG"], "SECTION_BG")

# 12. Roof underside / north slope: Since we're looking north and the cut
#     is at the ridge center, we see the underside of the north roof slope
#     going away from us. For the section, the roof slopes are in the Y
#     direction and appear as horizontal lines (ridge beam already drawn).
#     Draw the eave overhang extensions beyond walls.
sect_line(*P(MAIN_X1 - EAVE_OVERHANG, MAIN_EAVE_HEIGHT),
          *P(MAIN_X1, MAIN_EAVE_HEIGHT),
          "A_Eave_Overhang_West", layers["SECTION_BG"], "SECTION_BG")
sect_line(*P(MAIN_X2, MAIN_EAVE_HEIGHT),
          *P(MAIN_X2 + EAVE_OVERHANG, MAIN_EAVE_HEIGHT),
          "A_Eave_Overhang_East", layers["SECTION_BG"], "SECTION_BG")
# Connect eave to ridge at the walls (roof slope profile from inside)
sect_line(*P(MAIN_X1, MAIN_EAVE_HEIGHT), *P(MAIN_X1, MAIN_RIDGE_HEIGHT),
          "A_Roof_Slope_West_BG", layers["SECTION_BG"], "SECTION_BG")
sect_line(*P(MAIN_X2, MAIN_EAVE_HEIGHT), *P(MAIN_X2, MAIN_RIDGE_HEIGHT),
          "A_Roof_Slope_East_BG", layers["SECTION_BG"], "SECTION_BG")
print("  Background: north wall, eave overhangs, roof slopes")

# 13. Ceiling heights (SECTION_BG) -- the key spatial story
#     Entry vestibule ceiling at z=7.5' from x=120 to x=132
sect_line(*P(120, ENTRY_CEILING), *P(MAIN_X2, ENTRY_CEILING),
          "A_Entry_Ceiling", layers["SECTION_BG"], "SECTION_BG")
print("  Entry ceiling at z={:.1f}'".format(ENTRY_CEILING))

#     Kitchen ceiling at z=9.5' from x=92 to x=120
sect_line(*P(92, KITCHEN_CEILING), *P(120, KITCHEN_CEILING),
          "A_Kitchen_Ceiling", layers["SECTION_BG"], "SECTION_BG")
print("  Kitchen ceiling at z={:.1f}'".format(KITCHEN_CEILING))

#     Great room: OPEN to ridge (no ceiling line -- soars to z=22')
print("  Great room: open to ridge at z={:.0f}' (no ceiling line)".format(
    MAIN_RIDGE_HEIGHT))

# 14. Interior balcony at x=88 to 92, z=10.5' overlooking great room
sect_line(*P(88, FLOOR_TO_FLOOR), *P(92, FLOOR_TO_FLOOR),
          "A_Balcony", layers["SECTION_BG"], "SECTION_BG")
# Balcony railing: vertical at x=88 from z=10.5 to z=13.5 (3' railing)
sect_line(*P(88, FLOOR_TO_FLOOR), *P(88, FLOOR_TO_FLOOR + 3),
          "A_Balcony_Railing", layers["SECTION_BG"], "SECTION_BG")
print("  Interior balcony at z={:.1f}'".format(FLOOR_TO_FLOOR))

# 15. Stair indication
#     Main stair: from grade (z=0) at x=108 up to second floor (z=10.5) at x=112
sect_open_wire([
    P(108, 0),
    P(112, FLOOR_TO_FLOOR),
], "A_Stair_Up", layers["SECTION_BG"], "SECTION_BG")
#     Wine cellar stair: from grade (z=0) at x=108 down to cellar (z=-7) at x=110
sect_open_wire([
    P(108, 0),
    P(110, -WINE_CELLAR_CEILING),
], "A_Stair_Down", layers["SECTION_BG"], "SECTION_BG")
print("  Stair indication (up + down to cellar)")

# 16. Glulam columns at 12' spacing (STRUCTURE layer)
#     Columns at x = 68, 80, 92, 104, 116, 132
column_positions = [68, 80, 92, 104, 116, 132]
for i, cx in enumerate(column_positions):
    # Columns from grade to eave (or ridge for interior supports)
    col_top = MAIN_EAVE_HEIGHT
    sect_line(*P(cx, 0), *P(cx, col_top),
              "A_Column_{}".format(i), layers["STRUCTURE"], "STRUCTURE")
print("  Glulam columns at 12' spacing: x = " +
      ", ".join(str(x) for x in column_positions))


# === LABELS (DIMS layer) ===

# Room height labels
make_label("ENTRY 7'-6\"", *P(123, ENTRY_CEILING + 0.5),
           layers["DIMS"])
make_label("KITCHEN 9'-6\"", *P(100, KITCHEN_CEILING + 0.5),
           layers["DIMS"])
make_label("GREAT ROOM 22'-0\"", *P(73, MAIN_RIDGE_HEIGHT + 1),
           layers["DIMS"])
make_label("WINE CELLAR", *P(115, -WINE_CELLAR_CEILING + 2),
           layers["DIMS"])
make_label("BALCONY", *P(85, FLOOR_TO_FLOOR + 1.5),
           layers["DIMS"])

# Section title
make_label("SECTION A: LONGITUDINAL (E-W)",
           SEC_A_X_OFF + 80, SEC_A_Y_OFF - 12,
           layers["DIMS"])
print("  Labels placed")

print("")
print("  Section A complete: Compression -> Release sequence")
print("    Entry {:.1f}' -> Kitchen {:.1f}' -> Great Room {:.0f}'".format(
    ENTRY_CEILING, KITCHEN_CEILING, MAIN_RIDGE_HEIGHT))


# ===================================================================
# SECTION B: CROSS SECTION (N-S THROUGH WING INTERSECTION)
# ===================================================================
#
# Cut plane: runs N-S at x = 110 (through the wing, x=108 to 132).
# Looking WEST.
#
# Horizontal axis = Y position (80 to 175)
# Vertical axis   = Z height (-8 to 24)
#
# This section shows:
#   - Main bar in cross-section (gable profile)
#   - Wing in cross-section (near west edge, roof at ~13.3')
#   - Clerestory seam between main bar and wing roofs
#   - Courtyard space (open air)
#   - Guest pavilion cross-section (gable profile)
#   - Breezeway connection
# ===================================================================

print("")
print("=" * 60)
print("--- SECTION B: CROSS SECTION (N-S THROUGH WING) ---")
print("=" * 60)

P = draw_at(SEC_B_X_OFF, SEC_B_Y_OFF)

# === SECTION CUT elements (heavy lines) ===

# 1. Grade line from y=80 to y=175 at z=0
sect_line(*P(80, 0), *P(175, 0),
          "B_Grade", layers["SECTION_CUT"], "SECTION_CUT")
print("  Grade line")

# 2. Main bar cross section (y=85 to 115)
#    Full gable profile visible in cross-section

# South wall: vertical at y=85 from z=0 to eave (12')
sect_line(*P(MAIN_Y1, 0), *P(MAIN_Y1, MAIN_EAVE_HEIGHT),
          "B_Main_South_Wall", layers["SECTION_CUT"], "SECTION_CUT")

# North wall: vertical at y=115 from z=0 to eave (12')
sect_line(*P(MAIN_Y2, 0), *P(MAIN_Y2, MAIN_EAVE_HEIGHT),
          "B_Main_North_Wall", layers["SECTION_CUT"], "SECTION_CUT")

# Gable roof profile:
#   South slope: from (y=85, z=12') up to (y=100, z=22')
#   North slope: from (y=100, z=22') down to (y=115, z=12')
main_center_y = (MAIN_Y1 + MAIN_Y2) / 2.0  # 100
sect_open_wire([
    P(MAIN_Y1, MAIN_EAVE_HEIGHT),
    P(main_center_y, MAIN_RIDGE_HEIGHT),
    P(MAIN_Y2, MAIN_EAVE_HEIGHT),
], "B_Main_Gable_Roof", layers["SECTION_CUT"], "SECTION_CUT")

# Eave overhangs on main bar
sect_line(*P(MAIN_Y1 - EAVE_OVERHANG, MAIN_EAVE_HEIGHT),
          *P(MAIN_Y1, MAIN_EAVE_HEIGHT),
          "B_Main_Eave_South", layers["SECTION_CUT"], "SECTION_CUT")
sect_line(*P(MAIN_Y2, MAIN_EAVE_HEIGHT),
          *P(MAIN_Y2 + EAVE_OVERHANG, MAIN_EAVE_HEIGHT),
          "B_Main_Eave_North", layers["SECTION_CUT"], "SECTION_CUT")
# Eave overhang fascia lines (vertical drops at overhang ends)
sect_line(*P(MAIN_Y1 - EAVE_OVERHANG, MAIN_EAVE_HEIGHT),
          *P(MAIN_Y1 - EAVE_OVERHANG, MAIN_EAVE_HEIGHT - 1),
          "B_Main_Fascia_South", layers["SECTION_CUT"], "SECTION_CUT")

# Second floor slab at z=10.5 from y=85 to y=115
sect_line(*P(MAIN_Y1, FLOOR_TO_FLOOR), *P(MAIN_Y2, FLOOR_TO_FLOOR),
          "B_Main_Second_Floor", layers["SECTION_CUT"], "SECTION_CUT")

# Floor slab at z=0 (already drawn as grade line)
print("  Main bar cross section: gable, eave {:.0f}', ridge {:.0f}'".format(
    MAIN_EAVE_HEIGHT, MAIN_RIDGE_HEIGHT))


# 3. Wing cross section (y=115 to 143)
#    The wing ridge runs N-S. Cut at x=110, which is 2' inside
#    the wing from its west wall (x=108). Looking west, we see
#    the wing as a rectangular section with roof at height:
#    z = WING_EAVE_HEIGHT + (x - WING_X1) * WING_PITCH
#      = 12 + 2 * (8/12) = 13.33'
wing_roof_at_cut = WING_EAVE_HEIGHT + (110 - WING_X1) * WING_PITCH

# Wing shares north wall of main bar at y=115 (already drawn)

# Wing north wall at y=143
sect_line(*P(WING_Y2, 0), *P(WING_Y2, WING_EAVE_HEIGHT),
          "B_Wing_North_Wall", layers["SECTION_CUT"], "SECTION_CUT")

# Wing roof line at z = 13.33' (horizontal, cutting parallel to ridge)
sect_line(*P(MAIN_Y2, wing_roof_at_cut), *P(WING_Y2, wing_roof_at_cut),
          "B_Wing_Roof_Line", layers["SECTION_CUT"], "SECTION_CUT")

# Wing wall above main bar eave to wing roof intersection
sect_line(*P(MAIN_Y2, MAIN_EAVE_HEIGHT), *P(MAIN_Y2, wing_roof_at_cut),
          "B_Wing_Wall_South_Upper", layers["SECTION_CUT"], "SECTION_CUT")

# Wing eave overhang on north side
sect_line(*P(WING_Y2, WING_EAVE_HEIGHT),
          *P(WING_Y2 + EAVE_OVERHANG, WING_EAVE_HEIGHT),
          "B_Wing_Eave_North", layers["SECTION_CUT"], "SECTION_CUT")

print("  Wing cross section: roof at z={:.1f}' (2' inside west wall)".format(
    wing_roof_at_cut))

# Wine cellar below wing (y=115 to y=143)
sect_line(*P(MAIN_Y2, 0), *P(MAIN_Y2, -WINE_CELLAR_CEILING),
          "B_Cellar_Wall_South", layers["SECTION_CUT"], "SECTION_CUT")
sect_line(*P(WING_Y2, 0), *P(WING_Y2, -WINE_CELLAR_CEILING),
          "B_Cellar_Wall_North", layers["SECTION_CUT"], "SECTION_CUT")
sect_line(*P(MAIN_Y2, -WINE_CELLAR_CEILING),
          *P(WING_Y2, -WINE_CELLAR_CEILING),
          "B_Cellar_Floor", layers["SECTION_CUT"], "SECTION_CUT")
print("  Wine cellar below wing: floor at z=-{:.0f}'".format(
    WINE_CELLAR_CEILING))


# 4. Guest pavilion cross section (y=151 to 171)
#    Gable profile: ridge runs E-W, so cross section shows gable.
guest_center_y = (GUEST_Y1 + GUEST_Y2) / 2.0  # 161

# South wall at y=151
sect_line(*P(GUEST_Y1, 0), *P(GUEST_Y1, GUEST_EAVE_HEIGHT),
          "B_Guest_South_Wall", layers["SECTION_CUT"], "SECTION_CUT")

# North wall at y=171
sect_line(*P(GUEST_Y2, 0), *P(GUEST_Y2, GUEST_EAVE_HEIGHT),
          "B_Guest_North_Wall", layers["SECTION_CUT"], "SECTION_CUT")

# Gable roof profile
sect_open_wire([
    P(GUEST_Y1, GUEST_EAVE_HEIGHT),
    P(guest_center_y, GUEST_RIDGE_HEIGHT),
    P(GUEST_Y2, GUEST_EAVE_HEIGHT),
], "B_Guest_Gable_Roof", layers["SECTION_CUT"], "SECTION_CUT")

# Guest eave overhangs
sect_line(*P(GUEST_Y1 - EAVE_OVERHANG, GUEST_EAVE_HEIGHT),
          *P(GUEST_Y1, GUEST_EAVE_HEIGHT),
          "B_Guest_Eave_South", layers["SECTION_CUT"], "SECTION_CUT")
sect_line(*P(GUEST_Y2, GUEST_EAVE_HEIGHT),
          *P(GUEST_Y2 + EAVE_OVERHANG, GUEST_EAVE_HEIGHT),
          "B_Guest_Eave_North", layers["SECTION_CUT"], "SECTION_CUT")

# Guest porch: overhang from y=145 to y=151 at z=8.5' (porch roof)
sect_line(*P(145, GUEST_EAVE_HEIGHT), *P(GUEST_Y1, GUEST_EAVE_HEIGHT),
          "B_Guest_Porch_Roof", layers["SECTION_CUT"], "SECTION_CUT")
# Porch post
sect_line(*P(145, 0), *P(145, GUEST_EAVE_HEIGHT),
          "B_Guest_Porch_Post", layers["STRUCTURE"], "STRUCTURE")

print("  Guest pavilion: gable, eave {:.1f}', ridge {:.1f}'".format(
    GUEST_EAVE_HEIGHT, GUEST_RIDGE_HEIGHT))
print("  Guest porch overhang from y=145 to y=151")


# 5. Breezeway between wing and guest (y=143 to 151)
#    Short flat-roofed connection at z=BREEZEWAY_HEIGHT (8')
sect_line(*P(WING_Y2, BREEZEWAY_HEIGHT), *P(GUEST_Y1, BREEZEWAY_HEIGHT),
          "B_Breezeway_Roof", layers["SECTION_CUT"], "SECTION_CUT")
# Breezeway supports (lightweight posts)
sect_line(*P(WING_Y2, 0), *P(WING_Y2, BREEZEWAY_HEIGHT),
          "B_Breezeway_Post_South", layers["STRUCTURE"], "STRUCTURE")
sect_line(*P(GUEST_Y1, 0), *P(GUEST_Y1, BREEZEWAY_HEIGHT),
          "B_Breezeway_Post_North", layers["STRUCTURE"], "STRUCTURE")
print("  Breezeway: flat roof at z={:.0f}'".format(BREEZEWAY_HEIGHT))


# 6. Courtyard space (y=115 to y=143): open air, no structure above grade.
#    The gap between main bar north eave and breezeway/wing shows courtyard.
print("  Courtyard: open air between y=115 and y=143 (wing shares wall)")
print("    (visible gap between main bar and guest pavilion)")


# 7. Clerestory indication: where the main bar's north roof slope
#    descends from ridge (z=22 at y=100) to eave (z=12 at y=115) and
#    meets the wing roof (z=13.3 at y=115).
#    Draw glazing rectangle at the junction (y=115, z=12 to z=14)
sect_rect(*P(MAIN_Y2 - 0.5, MAIN_EAVE_HEIGHT),
          *P(MAIN_Y2 + 0.5, MAIN_EAVE_HEIGHT + 2),
          "B_Clerestory_Glazing", layers["GLAZING"], "GLAZING")
print("  Clerestory glazing at junction (y=115, z=12 to 14)")


# === SECTION BACKGROUND elements (lighter lines) ===

# Ceiling heights within main bar (seen beyond cut)
# At x=110, we're in the kitchen/entry zone. Show ceiling lines
# behind the cut plane as seen looking west.

# Main bar interior: entry ceiling at z=7.5' (seen beyond)
sect_line(*P(MAIN_Y1 + 1, ENTRY_CEILING), *P(MAIN_Y2 - 1, ENTRY_CEILING),
          "B_Entry_Ceiling_BG", layers["SECTION_BG"], "SECTION_BG")

# Floor line inside main bar
sect_line(*P(MAIN_Y1, 0), *P(MAIN_Y2, 0),
          "B_Main_Floor_BG", layers["SECTION_BG"], "SECTION_BG")

# Wing interior floor
sect_line(*P(MAIN_Y2, 0), *P(WING_Y2, 0),
          "B_Wing_Floor_BG", layers["SECTION_BG"], "SECTION_BG")

# Guest interior floor
sect_line(*P(GUEST_Y1, 0), *P(GUEST_Y2, 0),
          "B_Guest_Floor_BG", layers["SECTION_BG"], "SECTION_BG")

# Library ceiling in wing at z=9.0'
sect_line(*P(MAIN_Y2 + 1, LIBRARY_CEILING), *P(WING_Y2 - 1, LIBRARY_CEILING),
          "B_Library_Ceiling_BG", layers["SECTION_BG"], "SECTION_BG")

# Guest ceiling at z=8.5'
sect_line(*P(GUEST_Y1 + 1, GUEST_CEILING), *P(GUEST_Y2 - 1, GUEST_CEILING),
          "B_Guest_Ceiling_BG", layers["SECTION_BG"], "SECTION_BG")

# Main bar: the north roof slope descending from ridge to eave
# visible beyond the cut as the underside of the roof structure
sect_line(*P(main_center_y, MAIN_RIDGE_HEIGHT),
          *P(MAIN_Y2, MAIN_EAVE_HEIGHT),
          "B_Main_North_Slope_BG", layers["SECTION_BG"], "SECTION_BG")
# And the south roof slope
sect_line(*P(main_center_y, MAIN_RIDGE_HEIGHT),
          *P(MAIN_Y1, MAIN_EAVE_HEIGHT),
          "B_Main_South_Slope_BG", layers["SECTION_BG"], "SECTION_BG")
print("  Background: ceilings, roof slopes, floors")


# === STRUCTURE elements ===

# Structural columns visible in section B
# Main bar columns along the cut at y positions
main_col_positions = [MAIN_Y1, main_center_y, MAIN_Y2]
for i, cy in enumerate(main_col_positions):
    sect_line(*P(cy, 0), *P(cy, MAIN_EAVE_HEIGHT),
              "B_Main_Col_{}".format(i), layers["STRUCTURE"], "STRUCTURE")

# Wing columns
wing_col_positions = [MAIN_Y2, (MAIN_Y2 + WING_Y2) / 2.0, WING_Y2]
for i, cy in enumerate(wing_col_positions):
    sect_line(*P(cy, 0), *P(cy, WING_EAVE_HEIGHT),
              "B_Wing_Col_{}".format(i), layers["STRUCTURE"], "STRUCTURE")

# Guest columns
guest_col_positions = [GUEST_Y1, guest_center_y, GUEST_Y2]
for i, cy in enumerate(guest_col_positions):
    sect_line(*P(cy, 0), *P(cy, GUEST_EAVE_HEIGHT),
              "B_Guest_Col_{}".format(i), layers["STRUCTURE"], "STRUCTURE")
print("  Structural columns")


# === LABELS (DIMS layer) ===

make_label("MAIN BAR", *P(main_center_y - 5, MAIN_RIDGE_HEIGHT - 5),
           layers["DIMS"])
make_label("WING / LIBRARY", *P((MAIN_Y2 + WING_Y2) / 2.0 - 5, wing_roof_at_cut - 3),
           layers["DIMS"])
make_label("COURTYARD", *P((WING_Y2 + GUEST_Y1) / 2.0 - 4, 3),
           layers["DIMS"])
make_label("GUEST PAVILION", *P(guest_center_y - 6, GUEST_RIDGE_HEIGHT - 3),
           layers["DIMS"])
make_label("CLERESTORY", *P(MAIN_Y2 + 1, MAIN_EAVE_HEIGHT + 3),
           layers["DIMS"])
make_label("WINE CELLAR", *P((MAIN_Y2 + WING_Y2) / 2.0 - 4,
                              -WINE_CELLAR_CEILING + 2),
           layers["DIMS"])

# Section title
make_label("SECTION B: CROSS SECTION (N-S)",
           SEC_B_X_OFF + 110, SEC_B_Y_OFF - 12,
           layers["DIMS"])
print("  Labels placed")

print("")
print("  Section B complete: Main bar, wing, courtyard, guest pavilion")
print("    Clerestory at junction, wine cellar below")


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

export_dxf(doc, "farmhouse_sections.dxf")


# ===================================================================
# SUMMARY
# ===================================================================

print("")
print("=" * 60)
print("FARMHOUSE SECTIONS SUMMARY")
print("=" * 60)
print("")
print("SECTION A: LONGITUDINAL (E-W) at y=100 looking NORTH")
print("  Offset: ({}, {})".format(SEC_A_X_OFF, SEC_A_Y_OFF))
print("  Cut through main bar: x={} to x={}".format(MAIN_X1, MAIN_X2))
print("  Spatial sequence (compression -> release):")
print("    Entry vestibule: {:.1f}' ceiling".format(ENTRY_CEILING))
print("    Kitchen:         {:.1f}' ceiling".format(KITCHEN_CEILING))
print("    Great Room:      {:.0f}' open to ridge".format(MAIN_RIDGE_HEIGHT))
print("  Wine cellar:       {:.0f}' below grade".format(WINE_CELLAR_CEILING))
print("  Balcony:           at {:.1f}' overlooking great room".format(FLOOR_TO_FLOOR))
print("  Stair:             grade to 2nd floor + down to cellar")
print("")
print("SECTION B: CROSS SECTION (N-S) at x=110 looking WEST")
print("  Offset: ({}, {})".format(SEC_B_X_OFF, SEC_B_Y_OFF))
print("  Main bar:          gable profile, ridge at {:.0f}'".format(MAIN_RIDGE_HEIGHT))
print("  Wing:              roof at {:.1f}' (2' inside west wall)".format(wing_roof_at_cut))
print("  Clerestory:        2' glazing ribbon at junction")
print("  Courtyard:         open air between buildings")
print("  Guest pavilion:    gable profile, ridge at {:.1f}'".format(GUEST_RIDGE_HEIGHT))
print("  Breezeway:         flat roof at {:.0f}'".format(BREEZEWAY_HEIGHT))
print("  Wine cellar:       {:.0f}' below grade".format(WINE_CELLAR_CEILING))
print("")
print("Layers: " + ", ".join(layer_names))
print("Export: ~/farmhouse_sections.dxf")
print("=" * 60)
print("Script complete.")
