# Farmhouse CAD Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate production-ready parametric FreeCAD scripts producing a complete architectural drawing set (site plan, floor plans, elevations, sections, 3D massing) for "The Clearing" courtyard compound, with DXF and STEP exports.

**Architecture:** A shared parameters module defines all dimensions, coordinates, and styling. Each drawing type is a standalone FreeCAD Python script that imports the shared module. Scripts use Draft workbench for 2D and Part workbench for 3D. All geometry is parametrically driven -- changing a variable in the params module regenerates every drawing.

**Tech Stack:** Python 3, FreeCAD 0.21+ (Draft, Part, Arch workbenches), DXF export via `importDXF`, STEP export via `Part.export`.

---

## Coordinate System

- **Origin (0, 0, 0):** Southwest corner of lot
- **X axis:** East (positive)
- **Y axis:** North (positive)
- **Z axis:** Up (positive)
- **Units:** All parameters in feet, converted to millimeters internally (1 ft = 304.8 mm)

## Compound Placement on Lot (200' x 220')

```
# Arrival from east. View opening to west/south.
#
#  N (y+)
#  ^
#  |
#  |   [Guest Pavilion]  ···breezeway···  [Wing]
#  |        40x20                          24x28
#  |                                        |
#  |      < COURTYARD >                    |
#  |       open west                       |
#  |                         [Main Bar 64x30]------
#  |
#  |                              [Barn 36x26, rotated 10°]
#  |
#  +---------------------------------------------> E (x+)
#        (street / arrival from east)
```

### Key Reference Points (feet)

```
Main Bar SW:     (68,  85)    NE: (132, 115)    64' x 30'
Wing SW:         (108, 115)   NE: (132, 143)    24' x 28'
Guest SW:        (60,  151)   NE: (100, 171)    40' x 20'
Barn center:     (155, 100)   36' x 26', rotated 10° CCW
Breezeway SW:    (103, 143)   NE: (108, 151)    5' x 8'
Courtyard zone:  (60,  115)   NE: (108, 151)    48' x 36'
```

---

## Task 1: Create Shared Parameters Module

**Files:**
- Create: `farmhouse_params.py`

**Step 1: Write the parameters module**

This module defines every parametric variable, the coordinate system, unit conversion, helper functions, and layer styling. All other scripts import from it.

```python
# farmhouse_params.py
"""
Shared parametric definitions for "The Clearing" farmhouse compound.
All dimensions in feet. Converted to mm for FreeCAD internally.
"""
import FreeCAD
import math

# ── Unit Conversion ──
FT = 304.8  # 1 foot = 304.8 mm

def v(x_ft, y_ft, z_ft=0):
    """Convert (x, y, z) in feet to FreeCAD.Vector in mm."""
    return FreeCAD.Vector(x_ft * FT, y_ft * FT, z_ft * FT)

def ft_to_mm(val):
    """Convert feet to mm."""
    return val * FT

# ── Site ──
LOT_WIDTH = 200   # ft (E-W)
LOT_DEPTH = 220   # ft (N-S)

# ── Main House: Primary Bar (E-W) ──
MAIN_X1, MAIN_Y1 = 68, 85
MAIN_X2, MAIN_Y2 = 132, 115
MAIN_BAR_LENGTH = MAIN_X2 - MAIN_X1  # 64 ft
MAIN_BAR_WIDTH = MAIN_Y2 - MAIN_Y1   # 30 ft
MAIN_BAR_PITCH = 8 / 12

# ── Main House: Wing (N-S) ──
WING_X1, WING_Y1 = 108, 115
WING_X2, WING_Y2 = 132, 143
WING_LENGTH = WING_Y2 - WING_Y1  # 28 ft
WING_WIDTH = WING_X2 - WING_X1   # 24 ft
WING_PITCH = 8 / 12

# ── Guest Pavilion ──
GUEST_X1, GUEST_Y1 = 60, 151
GUEST_X2, GUEST_Y2 = 100, 171
GUEST_LENGTH = GUEST_X2 - GUEST_X1  # 40 ft
GUEST_WIDTH = GUEST_Y2 - GUEST_Y1   # 20 ft
GUEST_PITCH = 8 / 12

# ── Barn/Garage (center + rotation) ──
BARN_CX, BARN_CY = 155, 100
BARN_LENGTH = 36   # N-S before rotation
BARN_WIDTH = 26    # E-W before rotation
BARN_PITCH = 10 / 12
BARN_ROTATION = 10  # degrees CCW off main grid

# ── Breezeway ──
BW_X1, BW_Y1 = 103, 143
BW_X2, BW_Y2 = 108, 151
BREEZEWAY_WIDTH = BW_X2 - BW_X1   # 5 ft
BREEZEWAY_LENGTH = BW_Y2 - BW_Y1  # 8 ft
BREEZEWAY_PITCH = 2 / 12
BREEZEWAY_HEIGHT = 8.0  # ft

# ── Courtyard ──
COURT_X1, COURT_Y1 = 60, 115
COURT_X2, COURT_Y2 = 108, 151
COURT_LENGTH = COURT_X2 - COURT_X1  # 48 ft
COURT_WIDTH = COURT_Y2 - COURT_Y1   # 36 ft

# ── Structural ──
BAY_SPACING_MAIN = 12    # ft
BAY_SPACING_GUEST = 10   # ft
BAY_SPACING_BARN = 12    # ft
WALL_THICKNESS = 10 / 12  # ft (10 inches)
FLOOR_TO_FLOOR = 10.5     # ft

# ── Vertical Dimensions ──
ENTRY_CEILING = 7.5
KITCHEN_CEILING = 9.5
GREAT_ROOM_RIDGE = 22.0
LIBRARY_CEILING = 9.0
PRIMARY_SUITE_RIDGE = 10.5
GUEST_CEILING = 8.5
WINE_CELLAR_CEILING = 7.0
BARN_STUDIO_RIDGE = 12.0

# ── Roof ──
EAVE_OVERHANG = 4.0  # ft
RAKE_OVERHANG = 2.0  # ft

# ── Porch / Canopy ──
GUEST_PORCH_DEPTH = 6.0   # ft, south face of guest pavilion
CANOPY_DEPTH = 10.0        # ft, corten canopy from main house into courtyard

# ── Outdoor Living ──
FIRE_WALL_HEIGHT = 8.0   # ft
FIRE_WALL_WIDTH = 12.0   # ft
FIRE_WALL_THICKNESS = 1.0  # ft

# ── Layer Styles ──
LAYER_STYLE = {
    "SITE":       {"color": (0.00, 0.00, 0.00), "width": 1.5},
    "MAIN_HOUSE": {"color": (0.15, 0.15, 0.50), "width": 2.5},
    "GUEST":      {"color": (0.20, 0.20, 0.55), "width": 2.0},
    "BARN":       {"color": (0.35, 0.35, 0.35), "width": 2.0},
    "BREEZEWAY":  {"color": (0.50, 0.30, 0.15), "width": 1.5},
    "COURTYARD":  {"color": (0.45, 0.45, 0.40), "width": 1.0},
    "CANOPY":     {"color": (0.55, 0.30, 0.10), "width": 1.5},
    "DRIVEWAY":   {"color": (0.45, 0.45, 0.45), "width": 1.0},
    "TREES":      {"color": (0.10, 0.50, 0.10), "width": 0.75},
    "WALLS":      {"color": (0.10, 0.10, 0.10), "width": 2.0},
    "GLAZING":    {"color": (0.00, 0.60, 0.85), "width": 1.0},
    "STRUCTURE":  {"color": (0.60, 0.30, 0.10), "width": 1.5},
    "ROOF":       {"color": (0.55, 0.30, 0.10), "width": 1.5},
    "DIMS":       {"color": (0.40, 0.40, 0.40), "width": 0.5},
    "SECTION_CUT":{"color": (0.00, 0.00, 0.00), "width": 3.0},
    "SECTION_BG": {"color": (0.50, 0.50, 0.50), "width": 1.0},
}
```

Include these helper functions in the same file:

```python
import Draft
import os

OUTPUT_DIR = os.path.expanduser("~")

def apply_style(obj, layer_name):
    """Set line color and width from layer style."""
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
    """Closed Draft Wire from (x, y) tuples in feet."""
    vectors = [v(x, y) for x, y in points_ft]
    wire = Draft.make_wire(vectors, closed=True, face=False)
    wire.Label = label
    group.addObject(wire)
    apply_style(wire, layer_name)
    return wire

def make_rect(x1, y1, x2, y2, label, group, layer_name):
    """Closed rectangular wire from corners in feet."""
    pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    return make_closed_wire(pts, label, group, layer_name)

def make_line(x1, y1, x2, y2, label, group, layer_name):
    """Single line segment from two points in feet."""
    wire = Draft.make_wire([v(x1, y1), v(x2, y2)], closed=False, face=False)
    wire.Label = label
    group.addObject(wire)
    apply_style(wire, layer_name)
    return wire

def make_rotated_rect(cx, cy, length, width, angle_deg, label, group, layer_name):
    """Closed rectangular wire, rotated about its center. Length along Y, Width along X before rotation."""
    hw = width / 2
    hl = length / 2
    cos_a = math.cos(math.radians(angle_deg))
    sin_a = math.sin(math.radians(angle_deg))
    corners = [(-hw, -hl), (hw, -hl), (hw, hl), (-hw, hl)]
    rotated = []
    for dx, dy in corners:
        rx = cx + dx * cos_a - dy * sin_a
        ry = cy + dx * sin_a + dy * cos_a
        rotated.append((rx, ry))
    return make_closed_wire(rotated, label, group, layer_name)

def barn_corners():
    """Return the 4 corners of the barn after rotation, in feet."""
    hw = BARN_WIDTH / 2
    hl = BARN_LENGTH / 2
    cos_a = math.cos(math.radians(BARN_ROTATION))
    sin_a = math.sin(math.radians(BARN_ROTATION))
    corners = [(-hw, -hl), (hw, -hl), (hw, hl), (-hw, hl)]
    return [(BARN_CX + dx * cos_a - dy * sin_a,
             BARN_CY + dx * sin_a + dy * cos_a) for dx, dy in corners]

def make_tree(cx_ft, cy_ft, radius_ft, label, group):
    """Draft Circle tree canopy at center in feet."""
    circle = Draft.make_circle(radius_ft * FT)
    circle.Placement.Base = v(cx_ft, cy_ft)
    circle.Label = label
    group.addObject(circle)
    apply_style(circle, "TREES")
    return circle

def export_dxf(doc, filename):
    """Export all geometry objects to DXF."""
    try:
        import importDXF
        path = os.path.join(OUTPUT_DIR, filename)
        objs = [o for o in doc.Objects if not o.isDerivedFrom("App::DocumentObjectGroup")]
        importDXF.export(objs, path)
        print("DXF exported: {}".format(path))
    except Exception as e:
        print("DXF export failed: {}".format(e))

def export_step(doc, filename):
    """Export all Part shapes to STEP."""
    import Part
    path = os.path.join(OUTPUT_DIR, filename)
    shapes = [o for o in doc.Objects if hasattr(o, 'Shape') and o.Shape.Volume > 0]
    if shapes:
        Part.export(shapes, path)
        print("STEP exported: {}".format(path))
    else:
        print("No solid shapes to export.")
```

**Step 2: Verify import works**

Run in FreeCAD Python console:
```python
import sys
sys.path.insert(0, '/home/cameron/repos/architecture')
from farmhouse_params import *
print("MAIN_BAR_LENGTH:", MAIN_BAR_LENGTH)  # expect 64
print("v(10, 20):", v(10, 20))  # expect Vector(3048, 6096, 0)
```
Expected: Both values print correctly, no import errors.

**Step 3: Commit**

```bash
git add farmhouse_params.py
git commit -m "Add shared parametric definitions module for farmhouse compound"
```

---

## Task 2: Rewrite Site Plan for Courtyard Compound

**Files:**
- Modify: `farmhouse_site_plan.py` (complete rewrite)

**Dependencies:** Task 1 must be complete.

**Step 1: Rewrite the site plan script**

Replace the entire file. The new site plan must show:

1. **Lot boundary** (200' x 220') with setback lines (dashed)
2. **Main house footprint** -- L-shaped: primary bar + wing as single closed polygon
3. **Guest pavilion footprint** -- simple rectangle
4. **Barn footprint** -- rectangle rotated 10° CCW about its center
5. **Breezeway footprint** -- narrow rectangle connecting wing to guest pavilion
6. **Courtyard paving zone** -- closed polygon with open west edge (U-shape: south edge along main house, east edge along wing, north edge along guest pavilion; west edge open)
7. **Corten canopy** -- rectangle extending from main house south wall into courtyard
8. **Fire wall** -- thick line/narrow rectangle in courtyard outdoor living zone
9. **Arrival drive** -- gravel path curving from east lot edge to barn, then to main house entry. Use a polyline approximating a gentle S-curve
10. **Trees** -- adapted exclusion zones for new building positions, same two-phase algorithm (perimeter buffer + interior scatter), 75 target trees

Main house L-shaped polygon (single closed wire):
```python
house_pts = [
    (MAIN_X1, MAIN_Y1),   # SW corner of bar
    (MAIN_X2, MAIN_Y1),   # SE corner of bar
    (MAIN_X2, WING_Y2),   # NE corner of wing
    (WING_X1, WING_Y2),   # NW corner of wing
    (WING_X1, MAIN_Y2),   # inside corner of L
    (MAIN_X1, MAIN_Y2),   # NW corner of bar
]
```

Barn as rotated rectangle:
```python
make_rotated_rect(BARN_CX, BARN_CY, BARN_LENGTH, BARN_WIDTH,
                  BARN_ROTATION, "Barn_Footprint", layers["BARN"], "BARN")
```

Driveway as open polyline (NOT closed wire):
```python
# Approximate arrival drive: enters from east, curves past barn to main house entry
# Entry point on east lot edge, curves northwest to barn area, then west to house entry
drive_pts = [
    (LOT_WIDTH, 80),      # entry from east lot edge
    (175, 85),
    (165, 92),
    (BARN_CX + 15, BARN_CY),  # passes barn
    (BARN_CX, BARN_CY - 10),
    (140, 95),
    (MAIN_X2 + 5, (MAIN_Y1 + MAIN_Y2) / 2),  # arrives at main house entry (east face, mid-height)
]
# Create as open wire (not closed)
drive_vectors = [v(x, y) for x, y in drive_pts]
drive = Draft.make_wire(drive_vectors, closed=False, face=False)
```

Tree exclusion zones -- rebuild for new building positions:
```python
EXCLUSION_ZONES = [
    # Main house + buffer
    (MAIN_X1 - 4, MAIN_Y1 - 4, MAIN_X2 + 4, MAIN_Y2 + 4),
    # Wing + buffer
    (WING_X1 - 4, WING_Y1, WING_X2 + 4, WING_Y2 + 4),
    # Guest pavilion + buffer
    (GUEST_X1 - 4, GUEST_Y1 - 4, GUEST_X2 + 4, GUEST_Y2 + 4),
    # Courtyard paving zone
    (COURT_X1 - 2, COURT_Y1, COURT_X2, COURT_Y2),
    # Driveway corridor (approximate)
    (130, 75, LOT_WIDTH, 110),
    # Breezeway
    (BW_X1 - 2, BW_Y1 - 2, BW_X2 + 2, BW_Y2 + 2),
]
# Add barn exclusion (rotated -- use bounding box of rotated corners)
bc = barn_corners()
barn_xs = [c[0] for c in bc]
barn_ys = [c[1] for c in bc]
EXCLUSION_ZONES.append((min(barn_xs) - 4, min(barn_ys) - 4,
                         max(barn_xs) + 4, max(barn_ys) + 4))
```

Layer groups for the site plan:
```python
layer_names = ["SITE", "MAIN_HOUSE", "GUEST", "BARN", "BREEZEWAY",
               "COURTYARD", "CANOPY", "DRIVEWAY", "TREES"]
```

End with `export_dxf(doc, "farmhouse_site_plan.dxf")`.

**Step 2: Run in FreeCAD and verify**

Open FreeCAD, paste script into Python console.
Expected: Site plan shows all 3 buildings, courtyard, drive, trees. DXF exports to `~/farmhouse_site_plan.dxf`.

Verify:
- Main house L-shape is correct
- Guest pavilion is offset 8' west (its west edge at x=60 vs main bar west edge at x=68)
- Barn is visibly rotated relative to main house grid
- Courtyard reads as U-shaped space between buildings
- Trees respect exclusion zones
- No geometry overlaps

**Step 3: Commit**

```bash
git add farmhouse_site_plan.py
git commit -m "Rewrite site plan for courtyard compound layout"
```

---

## Task 3: Floor Plans (Ground + Upper)

**Files:**
- Create: `farmhouse_floor_plans.py`

**Dependencies:** Task 1 must be complete.

**Step 1: Write the floor plan script**

This script generates two separate FreeCAD documents (or two plan views offset in Y): ground floor and upper floor. Each includes interior wall layout, room labels, door swings, and key dimensions.

**Ground Floor Interior Layout (Main House):**

The main bar (64' x 30') is divided along its length into:
- **Entry vestibule** (east end): 12' long section. Full width of bar (30').
  - x = 120 to 132, y = 85 to 115
- **Kitchen/Dining** (center): 28' long.
  - x = 80 to 120, y = 85 to 115  (adjusted by wall thickness)
  - Kitchen occupies south half (y = 85 to 100), dining occupies north half (y = 100 to 115)
  - No wall between kitchen and dining -- open plan
- **Great Room** (west end): 24' long. Double height.
  - x = 68 to 80, y = 85 to 115 (wait, that's only 12'. Let me recalculate)

Actually, recalculate the main bar divisions. The bar is 64' (x = 68 to 132):
- Great Room (west): 24' → x = 68 to 92
- Kitchen/Dining (center): 28' → x = 92 to 120
- Entry Vestibule (east): 12' → x = 120 to 132

The wing (24' x 28', x = 108 to 132, y = 115 to 143) contains:
- **Library** (ground floor): full wing footprint minus walls
- **Stair** to upper floor and down to wine cellar: in SW corner of wing, 4' x 10'

Interior walls as thick lines (WALL_THICKNESS = 10"):
```python
# Wall between great room and kitchen
make_line(92, 85, 92, 115, "Wall_GR_Kitchen", layers["WALLS"], "WALLS")
# Wall between kitchen and entry
make_line(120, 85, 120, 115, "Wall_Kitchen_Entry", layers["WALLS"], "WALLS")
# Opening between kitchen and dining (no wall on north half)
# ... etc
```

**Ground Floor Interior Layout (Guest Pavilion, 40' x 20'):**

Two guest bedrooms divided by central wall:
- Guest Bedroom 1 (west): x = 60 to 80, y = 151 to 171 (20' x 20')
- Guest Bedroom 2 (east): x = 80 to 100, y = 151 to 171 (20' x 20')
- Each has bathroom carved from its north side (8' x 10')
- Shared entry vestibule along south face, 4' deep

**Ground Floor Interior Layout (Barn, 36' x 26' rotated 10°):**

Open plan at ground level:
- 2-car garage (south 24' of length)
- Workshop (north 12' of length)
- Dividing wall at 24' from south end
- Stair to loft in NE corner

**Upper Floor Layout (Main House only):**

The upper floor exists only over the EAST half of the main bar (x = 92 to 132) and the wing (x = 108 to 132, y = 115 to 143). The west half (great room, x = 68 to 92) is double height -- open to below.

- **Primary Suite** (over east bar, x = 108 to 132, y = 85 to 115): 24' x 30', with ensuite bath (10' x 12') in SE corner
- **Bedroom 2** (upper wing north, x = 108 to 132, y = 125 to 143): 24' x 18', bath in NE corner
- **Bedroom 3** (upper wing south, x = 108 to 132, y = 115 to 125): 24' x 10' -- narrow, more of a study/bedroom
- **Hallway** connecting primary suite to wing bedrooms
- **Interior balcony** overlooking great room: at x = 92 to 96, y = 85 to 115 (4' deep gallery)
- **Stair** landing at wing SW corner

**Dimensions:**

Add dimension lines for all major room widths/lengths using Draft.make_dimension or simple annotated lines.

**Step 2: Run in FreeCAD**

Expected: Two clean floor plans. All rooms readable. Walls align at intersections.

Verify:
- Great room shows as double height (hatched or noted on ground floor, open void on upper floor)
- Stair locations are consistent between floors
- Primary suite is positioned with view toward canopy (east)
- Guest pavilion shows 2 bedrooms + 2 baths
- All room dimensions are annotated

**Step 3: Commit**

```bash
git add farmhouse_floor_plans.py
git commit -m "Add ground and upper floor plan scripts with interior layout"
```

---

## Task 4: Elevations (4 Views)

**Files:**
- Create: `farmhouse_elevations.py`

**Dependencies:** Task 1 must be complete.

**Step 1: Write the elevations script**

Generate 4 elevation views of the compound. Each is drawn in a separate 2D plane, arranged side by side in the FreeCAD document (offset in X by 300' per view).

Elevations are projected geometry -- flattened views of the compound from each cardinal direction. Each view shows:
- Building outlines (silhouette)
- Roof profiles with pitch
- Grade line
- Window/door openings
- Overhang profiles
- Material indication (line weight variation)

**Elevation geometry is drawn in a (horizontal, vertical) coordinate space:**
- Horizontal axis = building dimension along view direction
- Vertical axis = height from grade (z = 0 at grade)

**West Elevation (the hero view -- Light Wall visible):**

Looking east at the compound from the west. We see:
- Main house great room gable end (west face): 30' wide, ridge at 22' (8:12 pitch)
  - Full-height glazed gable triangle
  - Foundation wall: 0 to 2' height, concrete
  - Eave overhang: 4' beyond wall face
- Guest pavilion: behind and to the left (north), partially visible
  - Gable end or long face, ridge at ~15' (8:12 pitch on 20' width → ridge at GUEST_WIDTH/2 * GUEST_PITCH + wall height = 10 * 0.667 + 9.5 ≈ 16.2')

Wait, I need to calculate ridge heights properly.

Ridge height calculation:
- Main bar: width = 30', half-width = 15', pitch = 8/12. Ridge rise = 15 * 8/12 = 10'. Wall plate height = FLOOR_TO_FLOOR = 10.5'. Ridge = 10.5 + 10 = 20.5'. But design says GREAT_ROOM_RIDGE = 22'. So the great room must have a taller wall plate or steeper pitch in the double-height section. The great room is full double height (22' at ridge), meaning the wall plate of the great room is higher than the rest of the bar.

Let me reconcile: The great room has no second floor, so its interior ceiling goes to the ridge at 22'. The east half of the bar has a second floor at 10.5', then the roof above. So:
- East bar section: wall plate at ~18' (ground floor 10.5' + upper floor 8' to plate), ridge at 18 + 15 * 8/12 = 18 + 10 = 28'? That's too tall.

Let me rethink. The main bar is a single continuous gable. The ridge height is constant along its length. The interior experience differs:
- West end (great room): open to ridge, so 22' interior height
- East end: second floor inserted, so ground floor ~10' ceiling, upper floor ~8' to roof slope

For a consistent 8:12 pitch gable on a 30' wide building:
- Half-width = 15', rise = 15 * 8/12 = 10'
- If wall plate (eave height) = 12', ridge = 22' ✓

So: eave/wall plate height = 12' for main bar. Ridge = 22'. Interior: great room open to ridge (22'), east section has floor at 10.5', upper ceiling follows roof slope.

Guest pavilion: width = 20', half = 10', rise = 10 * 8/12 = 6.67'. Eave = GUEST_CEILING = 8.5'. Ridge = 8.5 + 6.67 = 15.17' ≈ 15.2'.

Wing: width = 24', half = 12', rise = 12 * 8/12 = 8'. Eave = 12' (same as main bar, they intersect). Ridge = 12 + 8 = 20'.

Barn: width = 26', half = 13', rise = 13 * 10/12 = 10.83'. Eave = 10' (slightly lower than house). Ridge = 10 + 10.83 = 20.83' ≈ 21'. But barn has loft, so BARN_STUDIO_RIDGE = 12' interior... Let me set barn eave at 10', ridge at 21'.

Add these derived constants to farmhouse_params.py:
```python
# ── Derived Heights ──
MAIN_EAVE_HEIGHT = 12.0     # ft, wall plate height
MAIN_RIDGE_HEIGHT = MAIN_EAVE_HEIGHT + (MAIN_BAR_WIDTH / 2) * MAIN_BAR_PITCH  # 22.0
WING_EAVE_HEIGHT = 12.0     # same as main (they intersect)
WING_RIDGE_HEIGHT = WING_EAVE_HEIGHT + (WING_WIDTH / 2) * WING_PITCH  # 20.0
GUEST_EAVE_HEIGHT = 8.5
GUEST_RIDGE_HEIGHT = GUEST_EAVE_HEIGHT + (GUEST_WIDTH / 2) * GUEST_PITCH  # 15.17
BARN_EAVE_HEIGHT = 10.0
BARN_RIDGE_HEIGHT = BARN_EAVE_HEIGHT + (BARN_WIDTH / 2) * BARN_PITCH  # 20.83
```

Elevation drawing approach: each elevation is a set of 2D lines drawn in a local coordinate system. For the west elevation:
- Horizontal axis = Y (north-south position of buildings as seen from west)
- Vertical axis = Z (height)
- Draw at a Y-offset in the document so elevations don't overlap site plan

```python
def draw_gable_elevation(x_offset, y_offset, width, eave_h, ridge_h,
                          overhang, label, group, layer):
    """Draw a gable-end elevation as 2D profile.
    x_offset, y_offset position the drawing in document space.
    """
    hw = width / 2
    pts = [
        (x_offset - hw - overhang, y_offset),            # grade left
        (x_offset - hw - overhang, y_offset + eave_h),   # eave left
        (x_offset, y_offset + ridge_h),                   # ridge
        (x_offset + hw + overhang, y_offset + eave_h),   # eave right
        (x_offset + hw + overhang, y_offset),             # grade right
    ]
    make_closed_wire(pts, label, group, layer)
```

Generate all four elevations: West, South, East, North, each offset by 300' in the X direction of the document.

**Step 2: Add window openings to elevations**

Key windows to show:
- West: Full-height glazed gable (triangle) in great room
- South: Horizontal ribbon windows at kitchen, entry door
- East: Entry door, horizontal slot window at primary suite (upper)
- North: Mostly solid, small windows. Barn studio clerestory visible if barn is in view.

Windows drawn as rectangles with lighter line weight (GLAZING layer).

**Step 3: Run in FreeCAD, verify**

Expected: 4 elevation views arranged horizontally. Ridge heights, pitches, and overhangs look correct. Light Wall reads as a dramatic glazed gable.

**Step 4: Commit**

```bash
git add farmhouse_elevations.py
git commit -m "Add four compound elevation views with window openings"
```

---

## Task 5: Building Sections (2 Key Cuts)

**Files:**
- Create: `farmhouse_sections.py`

**Dependencies:** Task 1 must be complete.

**Step 1: Write section script**

Two sections that tell the story of the spatial experience:

**Section A: Longitudinal (E-W) through Main Bar**

Cut line runs east-west through the center of the main bar (y ≈ 100, through the middle of the 30'-wide bar). Looking north.

This section shows the compression-release sequence:
- East end: Entry vestibule at 7.5' ceiling
- Step up in ceiling to kitchen at 9.5'
- Opening into great room: full double-height to 22' ridge
- Interior balcony at 10.5' level overlooking great room
- Wine cellar below the wing (visible where section crosses wing intersection)

Drawing approach: horizontal = X position (68 to 132), vertical = Z height (-7 to 24).

Section cut elements (heavy line weight, SECTION_CUT layer):
- Concrete foundation walls (below grade)
- Cut through exterior walls at section line
- Cut through interior walls (entry/kitchen partition at x=120, kitchen/great room at x=92)
- Cut through second floor slab (x = 92 to 132 at z = 10.5)
- Roof profile (gable, from eave at z=12 to ridge at z=22)

Beyond-section elements (lighter weight, SECTION_BG layer):
- North exterior wall profile
- Window openings in north wall
- Interior balcony railing
- Ridge beam
- Glulam columns at 12' spacing

```python
# Section A: E-W through main bar
SEC_A_Y_OFFSET = -100  # position section drawing 100' below site plan in doc

# Grade line
make_line(65, SEC_A_Y_OFFSET, 135, SEC_A_Y_OFFSET, "SectionA_Grade", grp, "SECTION_BG")

# Foundation (below grade)
# Wine cellar below wing: x = 108 to 132, z = -7 to 0
cellar_pts = [(108, SEC_A_Y_OFFSET - WINE_CELLAR_CEILING),
              (132, SEC_A_Y_OFFSET - WINE_CELLAR_CEILING),
              (132, SEC_A_Y_OFFSET),
              (108, SEC_A_Y_OFFSET)]
# ... (shown as heavy line, hatched fill if possible)

# Floor slab at grade: x = 68 to 132, z = 0 (line already at grade)

# Exterior walls - south wall in section cut (heavy)
make_line(68, SEC_A_Y_OFFSET, 68, SEC_A_Y_OFFSET + MAIN_EAVE_HEIGHT,
          "SectionA_WallW", grp, "SECTION_CUT")
make_line(132, SEC_A_Y_OFFSET, 132, SEC_A_Y_OFFSET + MAIN_EAVE_HEIGHT,
          "SectionA_WallE", grp, "SECTION_CUT")

# Roof profile
roof_pts = [
    (68 - EAVE_OVERHANG, SEC_A_Y_OFFSET + MAIN_EAVE_HEIGHT),  # eave west
    (68 + MAIN_BAR_LENGTH / 2, SEC_A_Y_OFFSET + MAIN_RIDGE_HEIGHT),  # ridge
    ... # this is wrong for a longitudinal section - the ridge runs E-W
]
```

Wait -- for a longitudinal section through a gable building where the ridge runs E-W, the section cut is parallel to the ridge. You would NOT see the gable shape in this section. Instead you'd see:
- The south wall elevation (cut through it)
- The roof as a flat profile at the ridge height (since we're cutting along the ridge)
- The ceiling heights stepping up

Let me reconsider. For an E-W section looking north:
- You see the south wall in section (cut, heavy line)
- You see the north wall in elevation (beyond, lighter)
- The roof appears as a sloped line from eave to ridge on the south side (since we're cutting slightly south of ridge, we see the south slope of roof from inside)
- The second floor slab is visible
- Interior partition walls are cut

Actually for a section cut at y=100 (center of 30' bar, y = 85 to 115, center = 100):
- The cut hits the south wall at y=85 from inside
- We look north toward the north wall at y=115
- We see the roof's south slope from below (rafters heading up to ridge)
- The section shows a sloped ceiling following the rafter line

For the E-W section, the vertical dimension varies:
- At the south wall (our cut plane), the roof is at eave height (12')
- The roof slopes up to the ridge at the center (y=100 = center, so we're AT the ridge, seeing it at 22')

This is getting complex. Let me simplify: draw the section as a 2D profile showing walls, floors, and roof outline.

For a longitudinal section (E-W):
- The CUT plane is at y = 100 (center of bar)
- We look NORTH
- What we see CUT through: exterior east wall, exterior west wall, interior partition walls, floor slabs, roof structure at the ridge line
- What we see BEYOND: the north interior wall face, north windows, roof slope descending to north eave

Key section profile:
```
z=22  ___________ridge_____________
     /                              \  (roof slopes to eaves, but we're at center
z=12 |  balcony at z=10.5           |   so we see ridge, not slope)
     |  2nd floor z=10.5            |
     |  ________________________    |
     |  |entry   |kitchen    |great room (open to ridge)
z=0  |__|________|___________|______|
     x=132       x=120  x=92  x=68
```

The section at the CENTERLINE of the building shows:
- Ridge beam running E-W at z = 22
- East wall and west wall rising to eave at z = 12
- Since we're at the centerline, we see the ridge beam above, and the roof slopes away from us to north and toward us to south
- Interior partitions at x = 120 and x = 92
- Second floor from x = 92 to x = 132 at z = 10.5
- Balcony from x = 88 to x = 92 at z = 10.5

I'll specify this more precisely in the code. Let me move on in the plan and not over-detail every coordinate.

**Section B: Cross-section (N-S) through Main Bar and Wing intersection**

Cut at x = 110 (through the wing, which runs x = 108 to 132). Looking west.

This shows:
- Main bar in cross-section: 30' wide (y = 85 to 115), gable profile from eave at 12' to ridge at 22'
- Wing in cross-section: 24' wide (y = 115 to 143, but cut at x=110 we're inside the wing), gable profile eave at 12' to ridge at 20'
- The clerestory seam where the two gables intersect (the 2' light ribbon)
- Wine cellar below wing (y = 108 to 132, z = -7 to 0)
- Second floor slab at z = 10.5
- Upper level bedrooms

**Step 2: Run in FreeCAD, verify**

Expected: Two section drawings showing spatial sequence. The compression-release from entry to great room should be clearly readable in Section A.

**Step 3: Commit**

```bash
git add farmhouse_sections.py
git commit -m "Add longitudinal and cross sections showing spatial sequence"
```

---

## Task 6: 3D Massing Model

**Files:**
- Create: `farmhouse_3d_massing.py`

**Dependencies:** Task 1 must be complete.

**Step 1: Write the 3D massing script**

This script creates solid 3D geometry using FreeCAD's Part workbench. Each building volume is a combination of:
- Rectangular box (walls up to eave height)
- Triangular prism (gable roof volume)

Use `Part.makeBox()` for rectangular volumes and `Part.makePolygon()` + `Part.Face()` + `extrude()` for gable prisms.

**Main House - Primary Bar:**
```python
import Part

# Box: base of main bar up to eave height
bar_box = Part.makeBox(
    ft_to_mm(MAIN_BAR_LENGTH),  # X dimension
    ft_to_mm(MAIN_BAR_WIDTH),   # Y dimension
    ft_to_mm(MAIN_EAVE_HEIGHT)  # Z dimension
)
bar_box.translate(v(MAIN_X1, MAIN_Y1, 0))

# Gable prism on top: triangular cross-section extruded along bar length
ridge_rise = (MAIN_BAR_WIDTH / 2) * MAIN_BAR_PITCH
gable_profile = Part.makePolygon([
    v(MAIN_X1, MAIN_Y1, MAIN_EAVE_HEIGHT),
    v(MAIN_X1, MAIN_Y2, MAIN_EAVE_HEIGHT),
    v(MAIN_X1, (MAIN_Y1 + MAIN_Y2) / 2, MAIN_RIDGE_HEIGHT),
    v(MAIN_X1, MAIN_Y1, MAIN_EAVE_HEIGHT),  # close
])
gable_face = Part.Face(Part.Wire(gable_profile.Edges))
gable_prism = gable_face.extrude(v(MAIN_BAR_LENGTH, 0, 0))

# Fuse bar + gable
main_bar_solid = bar_box.fuse(gable_prism)
```

**Main House - Wing:** Same approach, oriented N-S.
```python
wing_box = Part.makeBox(
    ft_to_mm(WING_WIDTH), ft_to_mm(WING_LENGTH), ft_to_mm(WING_EAVE_HEIGHT)
)
wing_box.translate(v(WING_X1, WING_Y1, 0))

# Wing gable: ridge runs N-S, triangular section in E-W plane
wing_ridge_rise = (WING_WIDTH / 2) * WING_PITCH
wing_gable_profile = Part.makePolygon([
    v(WING_X1, WING_Y1, WING_EAVE_HEIGHT),
    v(WING_X2, WING_Y1, WING_EAVE_HEIGHT),
    v((WING_X1 + WING_X2) / 2, WING_Y1, WING_RIDGE_HEIGHT),
    v(WING_X1, WING_Y1, WING_EAVE_HEIGHT),
])
wing_gable_face = Part.Face(Part.Wire(wing_gable_profile.Edges))
wing_gable = wing_gable_face.extrude(v(0, WING_LENGTH, 0))
wing_solid = wing_box.fuse(wing_gable)
```

**Fuse main bar + wing into single solid:**
```python
main_house = main_bar_solid.fuse(wing_solid)
main_house_obj = doc.addObject("Part::Feature", "MainHouse")
main_house_obj.Shape = main_house
```

**Guest Pavilion:** Simple box + gable prism, same pattern.

**Barn:** Box + gable prism, then rotate the entire solid 10° about its center.
```python
# Create barn at origin, then translate and rotate
barn_box = Part.makeBox(
    ft_to_mm(BARN_WIDTH), ft_to_mm(BARN_LENGTH), ft_to_mm(BARN_EAVE_HEIGHT)
)
# Center at origin for rotation
barn_box.translate(FreeCAD.Vector(-ft_to_mm(BARN_WIDTH/2), -ft_to_mm(BARN_LENGTH/2), 0))
# Add gable...
# Rotate
barn_solid.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), BARN_ROTATION)
# Translate to final position
barn_solid.translate(v(BARN_CX, BARN_CY, 0))
```

**Breezeway:** Simple box, low-profile.
```python
bw_box = Part.makeBox(
    ft_to_mm(BREEZEWAY_WIDTH), ft_to_mm(BREEZEWAY_LENGTH), ft_to_mm(BREEZEWAY_HEIGHT)
)
bw_box.translate(v(BW_X1, BW_Y1, 0))
```

**Roof overhangs:** Extend each gable prism by EAVE_OVERHANG on each eave side and RAKE_OVERHANG on each gable end. This means the roof solid is larger than the wall solid below it. Create roof as separate objects in a "Roof" group.

**Organization:** Group objects into:
- `Structure` group: wall boxes
- `Roof` group: gable prisms with overhangs
- `Site` group: ground plane rectangle

**Step 2: Export STEP**

```python
export_step(doc, "farmhouse_massing.step")
```

**Step 3: Run in FreeCAD, verify**

Expected: 3D massing model showing compound of gabled volumes. Barn is visibly rotated. Buildings are distinct solids. Roofs overhang walls.

Verify:
- Ridge heights match design (main = 22', wing = 20', guest = 15.2', barn = 20.8')
- Gable pitches are visually correct
- Barn rotation is evident
- Breezeway connects main house to guest pavilion
- STEP file exports successfully and opens in external viewer

**Step 4: Commit**

```bash
git add farmhouse_3d_massing.py
git commit -m "Add 3D massing model with STEP export"
```

---

## Task 7: Structural Framing Layout

**Files:**
- Create: `farmhouse_structural.py`

**Dependencies:** Task 1 must be complete.

**Step 1: Write structural framing script**

2D plan view showing the structural grid for all buildings. This is a separate drawing from the floor plans, focused on:
- Column grid (glulam posts at bay spacing)
- Beam lines connecting columns
- Ridge beam centerline
- Concrete shear wall locations (hatched or heavy line)
- Foundation outline

**Main House Column Grid:**

Bay spacing = 12' along main bar (x direction).
Columns at x = 68, 80, 92, 104, 116, 128, 132(?)

Wait: 64' / 12' = 5.33 bays. Not clean. Let me adjust:
- 5 bays of 12' = 60', plus a 4' bay at east end.
- Or: start at x = 68, columns at 68, 80, 92, 104, 116, 128. That's 5 x 12' = 60'. The bar ends at 132, so the last bay is 4'.
- Better: 68, 80, 92, 104, 116, 132 = bays of 12, 12, 12, 12, 16. Last bay is 16'.

This is a design question. For structural regularity:
- Option: bays at 12, 12, 12, 12, 16 (last bay wider)
- Option: 68, 78.67, 89.33, 100, 110.67, 121.33, 132 = 6 bays of 10.67'

For clean numbers, use: 68, 80, 92, 104, 116, 132 (four 12' bays + one 16' bay). The great room spans x = 68 to 92 (two bays of 12'), which is a 24' column-free span using the steel ridge beam. The entry and kitchen have standard 12' bays.

Columns along both long walls (y = 85 and y = 115) plus one at the ridge line for intermediate support... actually, for a gable building with 30' span, you typically don't have intermediate columns if using glulam -- 30' is achievable with engineered beams. So columns only at perimeter.

Structural grid:
```python
# Main bar column positions (x values)
main_col_x = [68, 80, 92, 104, 116, 132]
# Column lines at y = 85 (south wall) and y = 115 (north wall)
for x in main_col_x:
    make_line(x, 85 - 1, x, 85 + 1, f"Col_S_{x}", grp, "STRUCTURE")  # south
    make_line(x, 115 - 1, x, 115 + 1, f"Col_N_{x}", grp, "STRUCTURE")  # north
# Beam lines along walls
make_line(68, 85, 132, 85, "Beam_S", grp, "STRUCTURE")
make_line(68, 115, 132, 115, "Beam_N", grp, "STRUCTURE")
# Ridge beam
make_line(68, 100, 132, 100, "RidgeBeam_Main", grp, "STRUCTURE")
# Mark steel ridge beam in great room zone (x = 68 to 92) differently
```

Repeat for wing (10' bays or similar) and guest pavilion (10' bays).

Concrete shear walls as filled rectangles:
- Entry vestibule walls: heavy lines at x = 120, from y = 85 to y = 115
- Great room east wall: heavy line at x = 92, from y = 85 to y = 115

**Step 2: Run in FreeCAD, verify**

Expected: Clean structural grid overlay. Columns as crosses or circles, beams as lines, concrete walls as heavy filled rectangles.

**Step 3: Commit**

```bash
git add farmhouse_structural.py
git commit -m "Add structural framing layout with column grid and beam lines"
```

---

## Task 8: Integration, Verification, and Final Export

**Files:**
- Modify: `farmhouse_params.py` (add any derived constants discovered during implementation)
- Verify: all 6 scripts run without error and produce clean exports

**Step 1: Run all scripts sequentially in FreeCAD**

Open FreeCAD. In Python console:
```python
import sys
sys.path.insert(0, '/home/cameron/repos/architecture')
exec(open('/home/cameron/repos/architecture/farmhouse_site_plan.py').read())
exec(open('/home/cameron/repos/architecture/farmhouse_floor_plans.py').read())
exec(open('/home/cameron/repos/architecture/farmhouse_elevations.py').read())
exec(open('/home/cameron/repos/architecture/farmhouse_sections.py').read())
exec(open('/home/cameron/repos/architecture/farmhouse_3d_massing.py').read())
exec(open('/home/cameron/repos/architecture/farmhouse_structural.py').read())
```

**Step 2: Verify all DXF exports exist**

```bash
ls -la ~/farmhouse_site_plan.dxf
ls -la ~/farmhouse_floor_plans.dxf
ls -la ~/farmhouse_elevations.dxf
ls -la ~/farmhouse_sections.dxf
ls -la ~/farmhouse_structural.dxf
ls -la ~/farmhouse_massing.step
```

All files should exist and have non-zero size.

**Step 3: Cross-check dimensions**

Verify in at least one viewer (FreeCAD measure tool or DXF viewer):
- Main bar measures 64' x 30'
- Guest pavilion measures 40' x 20'
- Distance between main house and guest pavilion matches courtyard width (36')
- Barn is rotated 10° relative to main grid

**Step 4: Final commit**

```bash
git add -A
git commit -m "Integration verification: all CAD scripts produce clean exports"
git push origin main
```

---

## Summary of Deliverables

| File | Type | Content | Export |
|------|------|---------|--------|
| `farmhouse_params.py` | Module | Shared parameters, helpers | N/A |
| `farmhouse_site_plan.py` | Script | Compound site plan with trees | DXF |
| `farmhouse_floor_plans.py` | Script | Ground + upper floor plans | DXF |
| `farmhouse_elevations.py` | Script | 4 elevation views | DXF |
| `farmhouse_sections.py` | Script | 2 building sections | DXF |
| `farmhouse_3d_massing.py` | Script | 3D solid massing | STEP |
| `farmhouse_structural.py` | Script | Structural framing grid | DXF |
