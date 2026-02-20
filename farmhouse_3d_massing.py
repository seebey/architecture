# ===================================================================
# MODERN RUSTIC FARMHOUSE -- 3D MASSING MODEL
# FreeCAD Python Script (tested on FreeCAD 0.21+)
# ===================================================================
#
# Generates solid 3D geometry for the farmhouse compound using
# FreeCAD's Part workbench.  Each building volume is modeled as a
# rectangular box (walls to eave height) fused with a triangular
# prism (gable roof).  The barn is rotated 10 degrees CCW after
# construction.
#
# Exports to STEP format for interoperability with other CAD tools.
#
# Layout:
#   - Main House (L-shaped: primary bar E-W + wing N, fused)
#   - Guest Pavilion (E-W gable)
#   - Barn / Garage (N-S gable, rotated 10 deg CCW)
#   - Breezeway (flat roof box)
#   - Ground plane
#
# Usage: freecad -c farmhouse_3d_massing.py
# Output: STEP file at ~/farmhouse_massing.step
#
# All dimensions specified in feet; converted to mm internally
# via farmhouse_params.py.
# ===================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from farmhouse_params import *

import Part

# ===================================================================
# DOCUMENT SETUP
# ===================================================================

doc = FreeCAD.newDocument("FarmhouseMassing")

structure_group = doc.addObject("App::DocumentObjectGroup", "Structure")
roof_group = doc.addObject("App::DocumentObjectGroup", "Roof")
site_group = doc.addObject("App::DocumentObjectGroup", "Site")

# ===================================================================
# MAIN HOUSE - PRIMARY BAR (E-W gable)
# ===================================================================
# The bar runs east-west.  The gable ridge runs east-west (along the
# bar's length).  The triangular cross-section is in the Y-Z plane.

bar_box = Part.makeBox(
    ft_to_mm(MAIN_BAR_LENGTH),   # X = 64'
    ft_to_mm(MAIN_BAR_WIDTH),    # Y = 30'
    ft_to_mm(MAIN_EAVE_HEIGHT)   # Z = 12'
)
bar_box.translate(v(MAIN_X1, MAIN_Y1, 0))

# Gable prism: triangular cross-section extruded along X (bar length)
# Triangle vertices (in the Y-Z plane at x = MAIN_X1):
p1 = v(MAIN_X1, MAIN_Y1, MAIN_EAVE_HEIGHT)          # south eave
p2 = v(MAIN_X1, MAIN_Y2, MAIN_EAVE_HEIGHT)           # north eave
p3 = v(MAIN_X1, (MAIN_Y1 + MAIN_Y2) / 2, MAIN_RIDGE_HEIGHT)  # ridge

gable_wire = Part.makePolygon([p1, p2, p3, p1])
gable_face = Part.Face(Part.Wire(gable_wire.Edges))
gable_prism = gable_face.extrude(FreeCAD.Vector(ft_to_mm(MAIN_BAR_LENGTH), 0, 0))

main_bar_solid = bar_box.fuse(gable_prism)

# ===================================================================
# MAIN HOUSE - WING (N-S gable)
# ===================================================================
# The wing runs north-south.  The gable ridge runs north-south.
# The triangular cross-section is in the X-Z plane.

wing_box = Part.makeBox(
    ft_to_mm(WING_WIDTH),        # X = 24'
    ft_to_mm(WING_LENGTH),       # Y = 28'
    ft_to_mm(WING_EAVE_HEIGHT)   # Z = 12'
)
wing_box.translate(v(WING_X1, WING_Y1, 0))

# Wing gable: triangle in X-Z plane at y = WING_Y1
wp1 = v(WING_X1, WING_Y1, WING_EAVE_HEIGHT)
wp2 = v(WING_X2, WING_Y1, WING_EAVE_HEIGHT)
wp3 = v((WING_X1 + WING_X2) / 2, WING_Y1, WING_RIDGE_HEIGHT)

wing_gable_wire = Part.makePolygon([wp1, wp2, wp3, wp1])
wing_gable_face = Part.Face(Part.Wire(wing_gable_wire.Edges))
wing_gable = wing_gable_face.extrude(FreeCAD.Vector(0, ft_to_mm(WING_LENGTH), 0))

wing_solid = wing_box.fuse(wing_gable)

# ===================================================================
# FUSE MAIN BAR + WING INTO SINGLE SOLID
# ===================================================================

main_house = main_bar_solid.fuse(wing_solid)
main_house_obj = doc.addObject("Part::Feature", "MainHouse")
main_house_obj.Shape = main_house
structure_group.addObject(main_house_obj)

# ===================================================================
# GUEST PAVILION (E-W gable)
# ===================================================================

guest_box = Part.makeBox(
    ft_to_mm(GUEST_LENGTH),       # X = 40'
    ft_to_mm(GUEST_WIDTH),        # Y = 20'
    ft_to_mm(GUEST_EAVE_HEIGHT)   # Z = 8.5'
)
guest_box.translate(v(GUEST_X1, GUEST_Y1, 0))

# Guest gable in Y-Z plane at x = GUEST_X1
gp1 = v(GUEST_X1, GUEST_Y1, GUEST_EAVE_HEIGHT)
gp2 = v(GUEST_X1, GUEST_Y2, GUEST_EAVE_HEIGHT)
gp3 = v(GUEST_X1, (GUEST_Y1 + GUEST_Y2) / 2, GUEST_RIDGE_HEIGHT)

guest_gable_wire = Part.makePolygon([gp1, gp2, gp3, gp1])
guest_gable_face = Part.Face(Part.Wire(guest_gable_wire.Edges))
guest_gable = guest_gable_face.extrude(FreeCAD.Vector(ft_to_mm(GUEST_LENGTH), 0, 0))

guest_solid = guest_box.fuse(guest_gable)
guest_obj = doc.addObject("Part::Feature", "GuestPavilion")
guest_obj.Shape = guest_solid
structure_group.addObject(guest_obj)

# ===================================================================
# BARN / GARAGE (N-S gable, rotated 10 deg CCW)
# ===================================================================
# Build barn centered at origin, then rotate and translate to final
# position.  The ridge runs N-S (along Y).

barn_box = Part.makeBox(
    ft_to_mm(BARN_WIDTH),         # X = 26'
    ft_to_mm(BARN_LENGTH),        # Y = 36'
    ft_to_mm(BARN_EAVE_HEIGHT)    # Z = 10'
)
# Center the box at origin
barn_box.translate(FreeCAD.Vector(
    -ft_to_mm(BARN_WIDTH / 2),
    -ft_to_mm(BARN_LENGTH / 2),
    0
))

# Barn gable: ridge runs N-S (along Y).  Triangle in X-Z plane at
# y = -BARN_LENGTH/2, extruded along Y.
bp1 = FreeCAD.Vector(
    -ft_to_mm(BARN_WIDTH / 2),
    -ft_to_mm(BARN_LENGTH / 2),
    ft_to_mm(BARN_EAVE_HEIGHT)
)
bp2 = FreeCAD.Vector(
    ft_to_mm(BARN_WIDTH / 2),
    -ft_to_mm(BARN_LENGTH / 2),
    ft_to_mm(BARN_EAVE_HEIGHT)
)
bp3 = FreeCAD.Vector(
    0,
    -ft_to_mm(BARN_LENGTH / 2),
    ft_to_mm(BARN_RIDGE_HEIGHT)
)

barn_gable_wire = Part.makePolygon([bp1, bp2, bp3, bp1])
barn_gable_face = Part.Face(Part.Wire(barn_gable_wire.Edges))
barn_gable = barn_gable_face.extrude(FreeCAD.Vector(0, ft_to_mm(BARN_LENGTH), 0))

barn_solid = barn_box.fuse(barn_gable)

# Rotate 10 deg CCW about Z axis at origin
barn_solid.rotate(
    FreeCAD.Vector(0, 0, 0),
    FreeCAD.Vector(0, 0, 1),
    BARN_ROTATION
)

# Translate to final position (BARN_CX, BARN_CY)
barn_solid.translate(v(BARN_CX, BARN_CY, 0))

barn_obj = doc.addObject("Part::Feature", "Barn")
barn_obj.Shape = barn_solid
structure_group.addObject(barn_obj)

# ===================================================================
# BREEZEWAY (flat roof box)
# ===================================================================

bw_box = Part.makeBox(
    ft_to_mm(BREEZEWAY_WIDTH),    # X = 5'
    ft_to_mm(BREEZEWAY_LENGTH),   # Y = 8'
    ft_to_mm(BREEZEWAY_HEIGHT)    # Z = 8'
)
bw_box.translate(v(BW_X1, BW_Y1, 0))

bw_obj = doc.addObject("Part::Feature", "Breezeway")
bw_obj.Shape = bw_box
structure_group.addObject(bw_obj)

# ===================================================================
# GROUND PLANE
# ===================================================================

ground = Part.makeBox(
    ft_to_mm(LOT_WIDTH),    # 200'
    ft_to_mm(LOT_DEPTH),    # 220'
    ft_to_mm(0.5)           # 6" thick slab
)
ground.translate(FreeCAD.Vector(0, 0, -ft_to_mm(0.5)))  # below grade

ground_obj = doc.addObject("Part::Feature", "GroundPlane")
ground_obj.Shape = ground
site_group.addObject(ground_obj)

# ===================================================================
# FINALIZE
# ===================================================================

doc.recompute()

try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
    FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
except Exception:
    pass

export_step(doc, "farmhouse_massing.step")
