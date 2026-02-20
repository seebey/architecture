# ===================================================================
# MODERN RUSTIC FARMHOUSE -- ELEVATIONS (4 VIEWS)
# FreeCAD Python Script (tested on FreeCAD 0.21+)
# ===================================================================
#
# Generates four 2D elevation views of the farmhouse courtyard compound:
#   - West Elevation  (the "hero" view showing the Light Wall)
#   - South Elevation
#   - East Elevation
#   - North Elevation
#
# Each elevation is a projected 2D view drawn in a local (horizontal,
# vertical) coordinate space, placed at different X offsets so they
# do not overlap in the document.
#
# Usage: Paste entire script into FreeCAD's Python console,
#        or run via:  freecad -c farmhouse_elevations.py
# Output: DXF file at ~/farmhouse_elevations.dxf
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
    t.Label = "Label_" + text.replace(" ", "_")
    group.addObject(t)
    apply_style(t, layer_name)
    try:
        t.ViewObject.FontSize = 600  # mm (about 2' at scale)
    except Exception:
        pass
    return t


def elev_closed_wire(pts_ft, label, group, layer_name):
    """Create a closed wire from (h, v) tuples already in document space."""
    vectors = [v(x, y) for x, y in pts_ft]
    wire = Draft.make_wire(vectors, closed=True, face=False)
    wire.Label = label
    group.addObject(wire)
    apply_style(wire, layer_name)
    return wire


def elev_open_wire(pts_ft, label, group, layer_name):
    """Create an open wire from (h, v) tuples already in document space."""
    vectors = [v(x, y) for x, y in pts_ft]
    wire = Draft.make_wire(vectors, closed=False, face=False)
    wire.Label = label
    group.addObject(wire)
    apply_style(wire, layer_name)
    return wire


def elev_line(x1, y1, x2, y2, label, group, layer_name):
    """Draw a single line segment in document feet coordinates."""
    vectors = [v(x1, y1), v(x2, y2)]
    wire = Draft.make_wire(vectors, closed=False, face=False)
    wire.Label = label
    group.addObject(wire)
    apply_style(wire, layer_name)
    return wire


def elev_rect(x1, y1, x2, y2, label, group, layer_name):
    """Draw a rectangle from two corners in document feet coordinates."""
    pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    return elev_closed_wire(pts, label, group, layer_name)


# ===================================================================
# ELEVATION GRID OFFSETS (feet)
# ===================================================================

# Place the 4 elevations in a row with large X spacing
WEST_X_OFF,  WEST_Y_OFF  = 0,   0
SOUTH_X_OFF, SOUTH_Y_OFF = 250, 0
EAST_X_OFF,  EAST_Y_OFF  = 500, 0
NORTH_X_OFF, NORTH_Y_OFF = 750, 0


# ===================================================================
# BARN APPROXIMATE EXTENTS (for projected elevations)
# ===================================================================
# The barn is rotated 10 degrees. For elevation purposes, we project
# its bounding box onto cardinal axes. The barn center is at
# (BARN_CX=155, BARN_CY=100) with length=36 (Y) and width=26 (X).

bc = barn_corners()
BARN_X_MIN = min(c[0] for c in bc)
BARN_X_MAX = max(c[0] for c in bc)
BARN_Y_MIN = min(c[1] for c in bc)
BARN_Y_MAX = max(c[1] for c in bc)
BARN_PROJ_WIDTH_EW = BARN_X_MAX - BARN_X_MIN   # projected width E-W
BARN_PROJ_WIDTH_NS = BARN_Y_MAX - BARN_Y_MIN   # projected width N-S


# ===================================================================
# DOCUMENT SETUP
# ===================================================================

doc = FreeCAD.newDocument("FarmhouseElevations")
print("Document created: FarmhouseElevations")

# -------------------------------------------------------------------
# Create layer groups
# -------------------------------------------------------------------
layer_names = ["WALLS", "GLAZING", "ROOF", "DIMS", "SECTION_BG"]

layers = {}
for name in layer_names:
    layers[name] = doc.addObject("App::DocumentObjectGroup", name)
print("Layer groups created: " + ", ".join(layer_names))


# ===================================================================
# WEST ELEVATION (Looking East -- The Hero View)
# ===================================================================
#
# Horizontal axis = Y position (north-south), Vertical axis = Z.
# We see west faces of all buildings.
#
# Visible:
#   1. Main house primary bar -- gable end (west face, 30' wide)
#   2. Guest pavilion -- gable end (west face, 20' wide)
# ===================================================================

print("")
print("--- WEST ELEVATION ---")

P = draw_at(WEST_X_OFF, WEST_Y_OFF)

# --- Main Bar Gable End ---
# h_left = MAIN_Y1 = 85, h_right = MAIN_Y2 = 115, h_center = 100
mb_left = MAIN_Y1     # 85
mb_right = MAIN_Y2    # 115
mb_center = (mb_left + mb_right) / 2.0  # 100

# Wall rectangle: grade to eave
elev_rect(*P(mb_left, 0), *P(mb_right, MAIN_EAVE_HEIGHT),
          "W_MainBar_Wall", layers["WALLS"], "WALLS")
print("  Main bar wall rectangle")

# Gable triangle: eave to ridge
elev_closed_wire([
    P(mb_left, MAIN_EAVE_HEIGHT),
    P(mb_center, MAIN_RIDGE_HEIGHT),
    P(mb_right, MAIN_EAVE_HEIGHT),
], "W_MainBar_Gable", layers["WALLS"], "WALLS")
print("  Main bar gable triangle")

# Roof overhang profile (full gable silhouette with eave + rake overhang)
elev_open_wire([
    P(mb_left - EAVE_OVERHANG, 0),
    P(mb_left - EAVE_OVERHANG, MAIN_EAVE_HEIGHT),
    P(mb_center, MAIN_RIDGE_HEIGHT + RAKE_OVERHANG * MAIN_BAR_PITCH),
    P(mb_right + EAVE_OVERHANG, MAIN_EAVE_HEIGHT),
    P(mb_right + EAVE_OVERHANG, 0),
], "W_MainBar_Roof_Profile", layers["ROOF"], "ROOF")
print("  Main bar roof overhang profile")

# THE LIGHT WALL -- full-height glazed gable
# Glazing triangle inset 1' from walls and 1' below ridge for framing
elev_closed_wire([
    P(mb_left + 1, 0),
    P(mb_right - 1, 0),
    P(mb_center, MAIN_RIDGE_HEIGHT - 1),
], "W_LightWall_Glazing", layers["GLAZING"], "GLAZING")
print("  Light Wall glazing (full gable)")

# Horizontal mullion lines across the Light Wall at floor levels
# Ground floor: line at 10.5' (floor-to-floor height)
elev_line(*P(mb_left + 1.5, FLOOR_TO_FLOOR), *P(mb_right - 1.5, FLOOR_TO_FLOOR),
          "W_LightWall_Mullion_1", layers["GLAZING"], "GLAZING")
print("  Light Wall horizontal mullion")


# --- Guest Pavilion West Gable End ---
# h positions: GUEST_Y1=151 to GUEST_Y2=171
gp_left = GUEST_Y1    # 151
gp_right = GUEST_Y2   # 171
gp_center = (gp_left + gp_right) / 2.0  # 161

# Wall rectangle: grade to eave
elev_rect(*P(gp_left, 0), *P(gp_right, GUEST_EAVE_HEIGHT),
          "W_Guest_Wall", layers["WALLS"], "WALLS")
print("  Guest pavilion wall rectangle")

# Gable triangle: eave to ridge
elev_closed_wire([
    P(gp_left, GUEST_EAVE_HEIGHT),
    P(gp_center, GUEST_RIDGE_HEIGHT),
    P(gp_right, GUEST_EAVE_HEIGHT),
], "W_Guest_Gable", layers["WALLS"], "WALLS")
print("  Guest pavilion gable triangle")

# Roof overhang
elev_open_wire([
    P(gp_left - EAVE_OVERHANG, 0),
    P(gp_left - EAVE_OVERHANG, GUEST_EAVE_HEIGHT),
    P(gp_center, GUEST_RIDGE_HEIGHT + RAKE_OVERHANG * GUEST_PITCH),
    P(gp_right + EAVE_OVERHANG, GUEST_EAVE_HEIGHT),
    P(gp_right + EAVE_OVERHANG, 0),
], "W_Guest_Roof_Profile", layers["ROOF"], "ROOF")
print("  Guest pavilion roof overhang")

# Guest pavilion windows on west gable -- two small windows
# Window 1: centered at h = gp_center - 5, sill at 3', head at 7', 4' wide
gw1_h = gp_center - 5
elev_rect(*P(gw1_h - 2, 3), *P(gw1_h + 2, 7),
          "W_Guest_Win1", layers["GLAZING"], "GLAZING")
# Window 2: centered at h = gp_center + 5
gw2_h = gp_center + 5
elev_rect(*P(gw2_h - 2, 3), *P(gw2_h + 2, 7),
          "W_Guest_Win2", layers["GLAZING"], "GLAZING")
print("  Guest pavilion windows (2)")


# --- Grade Line ---
grade_left = min(mb_left, gp_left) - 10
grade_right = max(mb_right, gp_right) + 10
grade_line = elev_line(*P(grade_left, 0), *P(grade_right, 0),
                       "W_Grade", layers["SECTION_BG"], "SECTION_BG")
try:
    grade_line.ViewObject.LineWidth = 0.75
except Exception:
    pass
print("  Grade line")

# --- Label ---
make_label("WEST ELEVATION", WEST_X_OFF + (grade_left + grade_right) / 2 - 10,
           WEST_Y_OFF - 5, layers["DIMS"])
print("  Label placed")


# ===================================================================
# SOUTH ELEVATION (Looking North)
# ===================================================================
#
# Horizontal axis = X position (east-west), Vertical axis = Z.
# We see south faces of buildings.
#
# Visible:
#   1. Main house primary bar -- long south face (64' wide)
#   2. Wing -- gable end rising behind main bar (east side)
#   3. Barn -- to the far right, approximate profile
# ===================================================================

print("")
print("--- SOUTH ELEVATION ---")

P = draw_at(SOUTH_X_OFF, SOUTH_Y_OFF)

# --- Main Bar South Wall ---
# x runs from MAIN_X1=68 to MAIN_X2=132
# South wall is a rectangle from grade to eave height 12'

elev_rect(*P(MAIN_X1, 0), *P(MAIN_X2, MAIN_EAVE_HEIGHT),
          "S_MainBar_Wall", layers["WALLS"], "WALLS")
print("  Main bar south wall")

# Roof profile: ridge runs E-W at center of bar width (not visible as
# ridge from south), but we see the eave line and gable rakes at each end.
# West gable rake: from (MAIN_X1, MAIN_EAVE_HEIGHT) up to ridge peak
# at (MAIN_X1, MAIN_RIDGE_HEIGHT) -- but the ridge is at the center of
# the bar width (Y direction), so from the south we only see the eave
# and the rake edges at each gable end.
# The roof slopes upward from eave to ridge. From the south, we see
# the south slope as an eave line and the rake triangles on each end.
# The gable end rakes are visible as diagonal lines from eave to ridge
# at the building ends.

# Roof overhang profile -- south face shows eave line with overhangs
# and gable rakes at the ends
# Left (west) gable rake
elev_open_wire([
    P(MAIN_X1 - RAKE_OVERHANG, MAIN_EAVE_HEIGHT),
    P(MAIN_X1 - RAKE_OVERHANG, MAIN_RIDGE_HEIGHT + RAKE_OVERHANG * MAIN_BAR_PITCH),
], "S_MainBar_Rake_W", layers["ROOF"], "ROOF")
# Right (east) gable rake
elev_open_wire([
    P(MAIN_X2 + RAKE_OVERHANG, MAIN_EAVE_HEIGHT),
    P(MAIN_X2 + RAKE_OVERHANG, MAIN_RIDGE_HEIGHT + RAKE_OVERHANG * MAIN_BAR_PITCH),
], "S_MainBar_Rake_E", layers["ROOF"], "ROOF")

# Eave overhang line across the full south face
# The eave projects EAVE_OVERHANG (4') beyond the south wall face,
# shown as a horizontal line at eave height
elev_line(*P(MAIN_X1 - RAKE_OVERHANG, MAIN_EAVE_HEIGHT),
          *P(MAIN_X2 + RAKE_OVERHANG, MAIN_EAVE_HEIGHT),
          "S_MainBar_Eave_Line", layers["ROOF"], "ROOF")

# Ridge line (visible behind, dashed or lighter -- drawn as roof layer)
elev_line(*P(MAIN_X1 - RAKE_OVERHANG, MAIN_RIDGE_HEIGHT + RAKE_OVERHANG * MAIN_BAR_PITCH),
          *P(MAIN_X2 + RAKE_OVERHANG, MAIN_RIDGE_HEIGHT + RAKE_OVERHANG * MAIN_BAR_PITCH),
          "S_MainBar_Ridge_Line", layers["ROOF"], "ROOF")
print("  Main bar roof profile")


# --- Kitchen Ribbon Windows ---
# 20' wide x 4' tall, sill at 3', from x=95 to x=115
elev_rect(*P(95, 3), *P(115, 7),
          "S_Kitchen_Ribbon", layers["GLAZING"], "GLAZING")
print("  Kitchen ribbon windows")

# --- Great Room south windows (lower level) ---
# Two windows on the south face of the great room (x=68 to 92)
# Standard windows: 4' wide x 4' tall, sill at 3'
elev_rect(*P(72, 3), *P(76, 7),
          "S_GreatRoom_Win1", layers["GLAZING"], "GLAZING")
elev_rect(*P(80, 3), *P(84, 7),
          "S_GreatRoom_Win2", layers["GLAZING"], "GLAZING")
print("  Great room south windows (2)")

# --- Entry area windows ---
# Standard window on entry south face
elev_rect(*P(123, 3), *P(127, 7),
          "S_Entry_Win", layers["GLAZING"], "GLAZING")
print("  Entry window")


# --- Wing Gable End (visible behind main bar, rising above) ---
# The wing extends north from x=108 to x=132, ridge runs N-S.
# From the south, we see the gable end: 24' wide, eave at 12', ridge at 20'
# The wing gable appears behind/above the main bar
wing_s_left = WING_X1   # 108
wing_s_right = WING_X2  # 132
wing_s_center = (wing_s_left + wing_s_right) / 2.0  # 120

# Wing gable triangle (visible above main bar eave line)
elev_closed_wire([
    P(wing_s_left, WING_EAVE_HEIGHT),
    P(wing_s_center, WING_RIDGE_HEIGHT),
    P(wing_s_right, WING_EAVE_HEIGHT),
], "S_Wing_Gable", layers["WALLS"], "WALLS")
print("  Wing gable (behind main bar)")

# Wing roof overhang on gable end
elev_open_wire([
    P(wing_s_left - RAKE_OVERHANG, WING_EAVE_HEIGHT),
    P(wing_s_center, WING_RIDGE_HEIGHT + RAKE_OVERHANG * WING_PITCH),
    P(wing_s_right + RAKE_OVERHANG, WING_EAVE_HEIGHT),
], "S_Wing_Roof_Profile", layers["ROOF"], "ROOF")
print("  Wing roof overhang")


# --- Barn Profile (approximate, to the right) ---
# Barn center at x=155, projected width ~26'. From the south we see
# the barn's south face. Because it's rotated 10 degrees, the projection
# is approximate.
barn_s_left = BARN_X_MIN
barn_s_right = BARN_X_MAX
barn_s_center = BARN_CX

# Wall rectangle
elev_rect(*P(barn_s_left, 0), *P(barn_s_right, BARN_EAVE_HEIGHT),
          "S_Barn_Wall", layers["WALLS"], "WALLS")
# Gable triangle
elev_closed_wire([
    P(barn_s_left, BARN_EAVE_HEIGHT),
    P(barn_s_center, BARN_RIDGE_HEIGHT),
    P(barn_s_right, BARN_EAVE_HEIGHT),
], "S_Barn_Gable", layers["WALLS"], "WALLS")
# Roof overhang
elev_open_wire([
    P(barn_s_left - EAVE_OVERHANG, BARN_EAVE_HEIGHT),
    P(barn_s_center, BARN_RIDGE_HEIGHT + RAKE_OVERHANG * BARN_PITCH),
    P(barn_s_right + EAVE_OVERHANG, BARN_EAVE_HEIGHT),
], "S_Barn_Roof_Profile", layers["ROOF"], "ROOF")
# Barn garage door (10' wide x 8' tall, centered)
elev_rect(*P(barn_s_center - 5, 0), *P(barn_s_center + 5, 8),
          "S_Barn_GarageDoor", layers["GLAZING"], "GLAZING")
print("  Barn profile with garage door")


# --- Grade Line ---
grade_left = MAIN_X1 - 10
grade_right = BARN_X_MAX + 10
grade_line = elev_line(*P(grade_left, 0), *P(grade_right, 0),
                       "S_Grade", layers["SECTION_BG"], "SECTION_BG")
try:
    grade_line.ViewObject.LineWidth = 0.75
except Exception:
    pass
print("  Grade line")

# --- Label ---
make_label("SOUTH ELEVATION",
           SOUTH_X_OFF + (grade_left + grade_right) / 2 - 10,
           SOUTH_Y_OFF - 5, layers["DIMS"])
print("  Label placed")


# ===================================================================
# EAST ELEVATION (Looking West)
# ===================================================================
#
# Horizontal axis = Y position (reversed -- south is on the right),
# Vertical axis = Z.
# We see east faces of buildings.
#
# Visible:
#   1. Wing gable end (east face): 24' wide (y=115 to y=143)
#   2. Main bar east face (entry side): partially behind wing
#   3. Barn: to the right (south)
# ===================================================================

print("")
print("--- EAST ELEVATION ---")

P = draw_at(EAST_X_OFF, EAST_Y_OFF)

# Looking west, Y axis is reversed: what's at higher Y (north) appears
# on the left, lower Y (south) on the right.
# We use a horizontal mapping: h = max_y - y + offset to reverse.
# For simplicity, we lay out buildings at their Y positions but reversed.
# Use a reference: h = 200 - y (flip around lot center)

def east_h(y):
    """Convert Y position to horizontal position in east elevation (reversed)."""
    return 200 - y


# --- Wing Gable End (east face) ---
# Wing: y = WING_Y1(115) to WING_Y2(143), 28' tall extent
# Width in this view = WING_WIDTH = 24' (x direction), but the wing
# runs N-S, so from the east we see the gable end: 28' wide (Y extent)
# with ridge running N-S at center x.
# Actually from the east, we see the LONG face of the wing (28' long),
# with the gable roof profile above. The wing ridge runs N-S, so from
# east we see the eave line at 12' and roof slope up to ridge at 20'.
# The gable ends are at the north and south ends of the wing.

# Wing east wall -- full rectangle
w_e_left = east_h(WING_Y2)    # north end -> left in reversed view
w_e_right = east_h(WING_Y1)   # south end -> right
w_e_center = (w_e_left + w_e_right) / 2.0

elev_rect(*P(w_e_left, 0), *P(w_e_right, WING_EAVE_HEIGHT),
          "E_Wing_Wall", layers["WALLS"], "WALLS")
print("  Wing east wall")

# Wing roof from east: we see the east slope as a rectangle from eave
# line up. The ridge is at the center of the width (X), not visible
# as a peak from this view. But we see the gable triangles at each end.
# Eave line with overhang
elev_line(*P(w_e_left - RAKE_OVERHANG, WING_EAVE_HEIGHT),
          *P(w_e_right + RAKE_OVERHANG, WING_EAVE_HEIGHT),
          "E_Wing_Eave", layers["ROOF"], "ROOF")

# Ridge line (behind, at ridge height)
elev_line(*P(w_e_left - RAKE_OVERHANG, WING_RIDGE_HEIGHT + RAKE_OVERHANG * WING_PITCH),
          *P(w_e_right + RAKE_OVERHANG, WING_RIDGE_HEIGHT + RAKE_OVERHANG * WING_PITCH),
          "E_Wing_Ridge", layers["ROOF"], "ROOF")

# Gable rake at south end (right side)
elev_open_wire([
    P(w_e_right + RAKE_OVERHANG, WING_EAVE_HEIGHT),
    P(w_e_right + RAKE_OVERHANG, WING_RIDGE_HEIGHT + RAKE_OVERHANG * WING_PITCH),
], "E_Wing_Rake_S", layers["ROOF"], "ROOF")

# Gable rake at north end (left side)
elev_open_wire([
    P(w_e_left - RAKE_OVERHANG, WING_EAVE_HEIGHT),
    P(w_e_left - RAKE_OVERHANG, WING_RIDGE_HEIGHT + RAKE_OVERHANG * WING_PITCH),
], "E_Wing_Rake_N", layers["ROOF"], "ROOF")
print("  Wing roof profile")

# Wing east windows -- library window
# Library east window: from floor plan, y=120 to y=138
lib_win_top = east_h(120)
lib_win_bot = east_h(138)
elev_rect(*P(lib_win_bot, 3), *P(lib_win_top, 7),
          "E_Wing_LibraryWin", layers["GLAZING"], "GLAZING")
print("  Library east window")

# Upper floor horizontal slot window (primary suite): 8' wide x 2' tall, at 14'
# This is on the main bar east face, visible below/behind the wing
# The primary suite is at y = 85 to 115 upper level
slot_left = east_h(104)
slot_right = east_h(96)
elev_rect(*P(slot_left, 14), *P(slot_right, 16),
          "E_PrimarySuite_SlotWin", layers["GLAZING"], "GLAZING")
print("  Primary suite slot window")


# --- Main Bar East Face (entry side, partially behind wing) ---
# The main bar east face: y = MAIN_Y1(85) to MAIN_Y2(115)
# The wing covers y=115 to 143, so the main bar is at y=85 to 115
# which is to the RIGHT of the wing in this reversed view.
mb_e_left = east_h(MAIN_Y2)   # 85 in reversed
mb_e_right = east_h(MAIN_Y1)  # 115 in reversed
mb_e_center = (mb_e_left + mb_e_right) / 2.0

# Main bar east wall (entry facade)
# Only the portion not covered by the wing is fully visible.
# The wing joins at y=115, and the main bar goes to y=85.
# In reversed coords, wing is to the LEFT and main bar extends RIGHT.
# Since the wing is in front (same x plane or further east), draw
# the main bar wall:
elev_rect(*P(mb_e_left, 0), *P(mb_e_right, MAIN_EAVE_HEIGHT),
          "E_MainBar_Wall", layers["WALLS"], "WALLS")

# Main bar gable profile from east
# The ridge runs E-W, so from the east we see the GABLE END
# Width = MAIN_BAR_WIDTH = 30 (y = 85 to 115)
elev_closed_wire([
    P(mb_e_left, MAIN_EAVE_HEIGHT),
    P(mb_e_center, MAIN_RIDGE_HEIGHT),
    P(mb_e_right, MAIN_EAVE_HEIGHT),
], "E_MainBar_Gable", layers["WALLS"], "WALLS")
print("  Main bar east gable")

# Main bar roof overhang from east
elev_open_wire([
    P(mb_e_left - EAVE_OVERHANG, MAIN_EAVE_HEIGHT),
    P(mb_e_center, MAIN_RIDGE_HEIGHT + RAKE_OVERHANG * MAIN_BAR_PITCH),
    P(mb_e_right + EAVE_OVERHANG, MAIN_EAVE_HEIGHT),
], "E_MainBar_Roof_Profile", layers["ROOF"], "ROOF")
print("  Main bar east roof overhang")

# Entry door: 4' wide x 7' tall, centered on east wall
# Center of east wall at y=100 -> east_h(100) = 100
entry_h = east_h(100)
elev_rect(*P(entry_h - 2, 0), *P(entry_h + 2, 7),
          "E_EntryDoor", layers["GLAZING"], "GLAZING")
print("  Entry door")

# Standard windows flanking entry
elev_rect(*P(east_h(93) - 2, 3), *P(east_h(93) + 2, 7),
          "E_Entry_Win_S", layers["GLAZING"], "GLAZING")
elev_rect(*P(east_h(107) - 2, 3), *P(east_h(107) + 2, 7),
          "E_Entry_Win_N", layers["GLAZING"], "GLAZING")
print("  Entry flanking windows")


# --- Barn (to the south/right in east elevation) ---
# From the east, we see the barn's east face.
# Barn projected Y extent: BARN_Y_MIN to BARN_Y_MAX
barn_e_left = east_h(BARN_Y_MAX)
barn_e_right = east_h(BARN_Y_MIN)
barn_e_center = east_h(BARN_CY)

# Wall rectangle
elev_rect(*P(barn_e_left, 0), *P(barn_e_right, BARN_EAVE_HEIGHT),
          "E_Barn_Wall", layers["WALLS"], "WALLS")
# Gable
elev_closed_wire([
    P(barn_e_left, BARN_EAVE_HEIGHT),
    P(barn_e_center, BARN_RIDGE_HEIGHT),
    P(barn_e_right, BARN_EAVE_HEIGHT),
], "E_Barn_Gable", layers["WALLS"], "WALLS")
# Roof overhang
elev_open_wire([
    P(barn_e_left - EAVE_OVERHANG, BARN_EAVE_HEIGHT),
    P(barn_e_center, BARN_RIDGE_HEIGHT + RAKE_OVERHANG * BARN_PITCH),
    P(barn_e_right + EAVE_OVERHANG, BARN_EAVE_HEIGHT),
], "E_Barn_Roof_Profile", layers["ROOF"], "ROOF")
print("  Barn profile")

# Barn workshop door on east face
barn_door_h = east_h(BARN_CY + 6)
elev_rect(*P(barn_door_h - 2, 0), *P(barn_door_h + 2, 7),
          "E_Barn_Door", layers["GLAZING"], "GLAZING")
print("  Barn workshop door")


# --- Grade Line ---
all_h = [w_e_left, w_e_right, mb_e_left, mb_e_right,
         barn_e_left, barn_e_right]
grade_left = min(all_h) - 10
grade_right = max(all_h) + 10
grade_line = elev_line(*P(grade_left, 0), *P(grade_right, 0),
                       "E_Grade", layers["SECTION_BG"], "SECTION_BG")
try:
    grade_line.ViewObject.LineWidth = 0.75
except Exception:
    pass
print("  Grade line")

# --- Label ---
make_label("EAST ELEVATION",
           EAST_X_OFF + (grade_left + grade_right) / 2 - 10,
           EAST_Y_OFF - 5, layers["DIMS"])
print("  Label placed")


# ===================================================================
# NORTH ELEVATION (Looking South)
# ===================================================================
#
# Horizontal axis = X position (reversed -- east on the left),
# Vertical axis = Z.
# We see north faces of buildings.
#
# Visible:
#   1. Guest pavilion -- long north face (40' wide, mostly solid)
#   2. Wing -- visible behind guest pavilion, taller
#   3. Barn -- visible to the left (east side in reversed view)
# ===================================================================

print("")
print("--- NORTH ELEVATION ---")

P = draw_at(NORTH_X_OFF, NORTH_Y_OFF)

# Looking south, X axis is reversed: east is on the left.
def north_h(x):
    """Convert X position to horizontal position in north elevation (reversed)."""
    return 200 - x


# --- Guest Pavilion North Wall ---
# Guest: x = GUEST_X1(60) to GUEST_X2(100), 40' wide
# Ridge runs E-W, so from the north we see the long face with the
# roof slope rising behind it.

gp_n_left = north_h(GUEST_X2)    # east end -> left in reversed
gp_n_right = north_h(GUEST_X1)   # west end -> right

elev_rect(*P(gp_n_left, 0), *P(gp_n_right, GUEST_EAVE_HEIGHT),
          "N_Guest_Wall", layers["WALLS"], "WALLS")
print("  Guest pavilion north wall")

# Guest roof: eave line and ridge behind
# The ridge runs E-W at center of width (Y direction)
# From the north we see the north slope eave and the gable rakes at ends
elev_line(*P(gp_n_left - RAKE_OVERHANG, GUEST_EAVE_HEIGHT),
          *P(gp_n_right + RAKE_OVERHANG, GUEST_EAVE_HEIGHT),
          "N_Guest_Eave", layers["ROOF"], "ROOF")

# Ridge line
elev_line(*P(gp_n_left - RAKE_OVERHANG, GUEST_RIDGE_HEIGHT + RAKE_OVERHANG * GUEST_PITCH),
          *P(gp_n_right + RAKE_OVERHANG, GUEST_RIDGE_HEIGHT + RAKE_OVERHANG * GUEST_PITCH),
          "N_Guest_Ridge", layers["ROOF"], "ROOF")

# Gable rakes at each end
elev_open_wire([
    P(gp_n_left - RAKE_OVERHANG, GUEST_EAVE_HEIGHT),
    P(gp_n_left - RAKE_OVERHANG, GUEST_RIDGE_HEIGHT + RAKE_OVERHANG * GUEST_PITCH),
], "N_Guest_Rake_E", layers["ROOF"], "ROOF")
elev_open_wire([
    P(gp_n_right + RAKE_OVERHANG, GUEST_EAVE_HEIGHT),
    P(gp_n_right + RAKE_OVERHANG, GUEST_RIDGE_HEIGHT + RAKE_OVERHANG * GUEST_PITCH),
], "N_Guest_Rake_W", layers["ROOF"], "ROOF")
print("  Guest pavilion roof profile")

# Guest north face -- mostly solid (charred wood), minimal windows
# One small window on each bedroom
gp_n_center = (gp_n_left + gp_n_right) / 2.0
elev_rect(*P(gp_n_center - 12, 3), *P(gp_n_center - 8, 7),
          "N_Guest_Win1", layers["GLAZING"], "GLAZING")
elev_rect(*P(gp_n_center + 8, 3), *P(gp_n_center + 12, 7),
          "N_Guest_Win2", layers["GLAZING"], "GLAZING")
print("  Guest north windows (minimal, 2)")


# --- Wing (visible behind guest, taller) ---
# Wing: x = WING_X1(108) to WING_X2(132), eave at 12', ridge at 20'
# Ridge runs N-S. From the north we see the gable end.
w_n_left = north_h(WING_X2)   # 68
w_n_right = north_h(WING_X1)  # 92
w_n_center = (w_n_left + w_n_right) / 2.0

# Wing north gable (visible above guest pavilion)
# The wing is behind (further south), so its wall base may be partially
# hidden by the guest pavilion. Draw the full profile.
elev_rect(*P(w_n_left, 0), *P(w_n_right, WING_EAVE_HEIGHT),
          "N_Wing_Wall", layers["WALLS"], "WALLS")

elev_closed_wire([
    P(w_n_left, WING_EAVE_HEIGHT),
    P(w_n_center, WING_RIDGE_HEIGHT),
    P(w_n_right, WING_EAVE_HEIGHT),
], "N_Wing_Gable", layers["WALLS"], "WALLS")

# Wing roof overhang
elev_open_wire([
    P(w_n_left - RAKE_OVERHANG, WING_EAVE_HEIGHT),
    P(w_n_center, WING_RIDGE_HEIGHT + RAKE_OVERHANG * WING_PITCH),
    P(w_n_right + RAKE_OVERHANG, WING_EAVE_HEIGHT),
], "N_Wing_Roof_Profile", layers["ROOF"], "ROOF")
print("  Wing gable (behind guest)")


# --- Main Bar (partially visible behind wing/guest) ---
# Main bar ridge runs E-W, from the north we see the long north face
# It's at y=115, behind the wing (y=115-143) and guest (y=151-171)
# Parts of the main bar roof visible between/behind other buildings
# The main bar extends from x=68 to x=132.
# In reversed view: north_h(132)=68 to north_h(68)=132
mb_n_left = north_h(MAIN_X2)   # 68
mb_n_right = north_h(MAIN_X1)  # 132

# Main bar eave and ridge visible above lower buildings
# Only draw the roof lines that peek above the wing
elev_line(*P(mb_n_right, MAIN_EAVE_HEIGHT),
          *P(mb_n_right + RAKE_OVERHANG, MAIN_EAVE_HEIGHT),
          "N_MainBar_Eave_W_Visible", layers["ROOF"], "ROOF")
elev_line(*P(mb_n_right, MAIN_RIDGE_HEIGHT + RAKE_OVERHANG * MAIN_BAR_PITCH),
          *P(mb_n_right + RAKE_OVERHANG, MAIN_RIDGE_HEIGHT + RAKE_OVERHANG * MAIN_BAR_PITCH),
          "N_MainBar_Ridge_W_Visible", layers["ROOF"], "ROOF")
# West gable rake visible
elev_open_wire([
    P(mb_n_right + RAKE_OVERHANG, MAIN_EAVE_HEIGHT),
    P(mb_n_right + RAKE_OVERHANG, MAIN_RIDGE_HEIGHT + RAKE_OVERHANG * MAIN_BAR_PITCH),
], "N_MainBar_Rake_W", layers["ROOF"], "ROOF")
print("  Main bar roof (partially visible)")


# --- Barn (to the east/left in north elevation) ---
barn_n_left = north_h(BARN_X_MAX)
barn_n_right = north_h(BARN_X_MIN)
barn_n_center = north_h(BARN_CX)

# Wall rectangle
elev_rect(*P(barn_n_left, 0), *P(barn_n_right, BARN_EAVE_HEIGHT),
          "N_Barn_Wall", layers["WALLS"], "WALLS")
# Gable
elev_closed_wire([
    P(barn_n_left, BARN_EAVE_HEIGHT),
    P(barn_n_center, BARN_RIDGE_HEIGHT),
    P(barn_n_right, BARN_EAVE_HEIGHT),
], "N_Barn_Gable", layers["WALLS"], "WALLS")
# Roof overhang
elev_open_wire([
    P(barn_n_left - EAVE_OVERHANG, BARN_EAVE_HEIGHT),
    P(barn_n_center, BARN_RIDGE_HEIGHT + RAKE_OVERHANG * BARN_PITCH),
    P(barn_n_right + EAVE_OVERHANG, BARN_EAVE_HEIGHT),
], "N_Barn_Roof_Profile", layers["ROOF"], "ROOF")

# Barn window on north face
elev_rect(*P(barn_n_center - 2, 3), *P(barn_n_center + 2, 7),
          "N_Barn_Win", layers["GLAZING"], "GLAZING")
print("  Barn profile with window")


# --- Breezeway (between wing and guest) ---
# Breezeway: x = BW_X1(103) to BW_X2(108), flat roof at 8'
bw_n_left = north_h(BW_X2)    # 92
bw_n_right = north_h(BW_X1)   # 97
elev_rect(*P(bw_n_left, 0), *P(bw_n_right, BREEZEWAY_HEIGHT),
          "N_Breezeway", layers["WALLS"], "WALLS")
print("  Breezeway")


# --- Grade Line ---
all_h = [gp_n_left, gp_n_right, w_n_left, w_n_right,
         barn_n_left, barn_n_right, mb_n_left, mb_n_right]
grade_left = min(all_h) - 10
grade_right = max(all_h) + 10
grade_line = elev_line(*P(grade_left, 0), *P(grade_right, 0),
                       "N_Grade", layers["SECTION_BG"], "SECTION_BG")
try:
    grade_line.ViewObject.LineWidth = 0.75
except Exception:
    pass
print("  Grade line")

# --- Label ---
make_label("NORTH ELEVATION",
           NORTH_X_OFF + (grade_left + grade_right) / 2 - 10,
           NORTH_Y_OFF - 5, layers["DIMS"])
print("  Label placed")


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

export_dxf(doc, "farmhouse_elevations.dxf")


# ===================================================================
# SUMMARY
# ===================================================================

print("")
print("=" * 60)
print("FARMHOUSE ELEVATIONS SUMMARY")
print("=" * 60)
print("")
print("WEST ELEVATION (offset x={}, y={}):".format(WEST_X_OFF, WEST_Y_OFF))
print("  Main Bar:    gable end (30' wide), eave {:.0f}', ridge {:.0f}'".format(
    MAIN_EAVE_HEIGHT, MAIN_RIDGE_HEIGHT))
print("  Light Wall:  full-height glazed gable (hero feature)")
print("  Guest Pav:   gable end (20' wide), eave {:.1f}', ridge {:.1f}'".format(
    GUEST_EAVE_HEIGHT, GUEST_RIDGE_HEIGHT))
print("")
print("SOUTH ELEVATION (offset x={}, y={}):".format(SOUTH_X_OFF, SOUTH_Y_OFF))
print("  Main Bar:    south face (64' wide), eave {:.0f}'".format(MAIN_EAVE_HEIGHT))
print("  Wing:        gable end (24' wide) behind main bar")
print("  Barn:        approximate profile with garage door")
print("  Windows:     kitchen ribbon, great room, entry")
print("")
print("EAST ELEVATION (offset x={}, y={}):".format(EAST_X_OFF, EAST_Y_OFF))
print("  Wing:        east face (28' long), eave {:.0f}', ridge {:.0f}'".format(
    WING_EAVE_HEIGHT, WING_RIDGE_HEIGHT))
print("  Main Bar:    east gable (entry side) with entry door")
print("  Barn:        profile with workshop door")
print("  Windows:     library, primary suite slot, entry flanking")
print("")
print("NORTH ELEVATION (offset x={}, y={}):".format(NORTH_X_OFF, NORTH_Y_OFF))
print("  Guest Pav:   north face (40' wide), mostly solid")
print("  Wing:        gable end (behind guest)")
print("  Main Bar:    roof partially visible")
print("  Barn:        profile with window")
print("  Breezeway:   flat roof at {:.0f}'".format(BREEZEWAY_HEIGHT))
print("")
print("Layers: " + ", ".join(layer_names))
print("Export: ~/farmhouse_elevations.dxf")
print("=" * 60)
print("Script complete.")
