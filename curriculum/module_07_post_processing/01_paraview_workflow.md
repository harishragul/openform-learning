# Lesson 7.1 — ParaView Workflow for OpenFOAM

## Concept

ParaView is the standard visualization tool for OpenFOAM results. It's a powerful pipeline-based visualizer — you apply filters sequentially to transform data.

---

## Opening OpenFOAM Data in ParaView

```bash
# ESI OpenFOAM:
touch case.foam          # creates an empty trigger file
paraview case.foam &     # ParaView opens and reads all time directories

# Foundation OpenFOAM:
paraFoam &

# Convert to VTK first (older workflows):
foamToVTK
paraview VTK/...
```

### First Steps in ParaView

1. **Open**: File → Open → select `case.foam`
2. **Load**: Click "Apply" in the Properties panel (left side)
3. **Select field**: Top toolbar — change "Solid Color" to "U" or "p"
4. **Rescale**: Click the "Rescale to Data Range" button (colorbar icon)
5. **Animate**: Press Play (▶) to step through time

---

## Essential ParaView Filters

Access via: Filters menu, or search bar (Ctrl+Space)

### Slice — Cut a plane through the domain
```
Filters → Slice
- Normal: (0 0 1) for z-plane, (0 1 0) for y-plane
- Useful for 3D domains: see interior flow
```

### Clip — Remove half the domain
```
Filters → Clip
- Shows cross-section of 3D geometry
```

### Stream Tracer — Visualize streamlines
```
Filters → Stream Tracer
- Seed type: Line Source (specify start/end points)
- Integration direction: Forward
- Max steps: 2000
- Apply with U field active
```

### Glyph — Arrow vectors
```
Filters → Glyph
- Glyph type: Arrow
- Scale by: U (or magnitude)
- Maximum number of sample points: 1000
- Good for showing velocity direction
```

### Plot Over Line — Extract a profile
```
Filters → Plot Over Line
- Set two end points of the line
- Shows selected field along that line
- Export data via File → Save Data (.csv)
```

### Contour — Isosurface / isolines
```
Filters → Contour
- Value: set the isovalue (e.g., p = 0 for pressure coefficient = 0)
- Useful for pressure contours, vortex identification
```

### Calculator — Create derived quantities
```
Filters → Calculator
- Result array name: "speed"
- Expression: mag(U)   → velocity magnitude
- Expression: U_X      → x-component of velocity
```

---

## Python Scripting in ParaView

For reproducible post-processing, use ParaView's Python trace:

```
Tools → Start Trace
(do your visualization actions)
Tools → Stop Trace
```

This generates a Python script. Save it and re-run with:
```bash
pvpython myScript.py
```

Example generated script:
```python
from paraview.simple import *

# Open case
case = OpenFOAMReader(FileName='case.foam')
case.MeshRegions = ['internalMesh']
case.CellArrays = ['U', 'p']

# Get last time step
animationScene = GetAnimationScene()
animationScene.GoToLast()

# Create slice
slice1 = Slice(Input=case)
slice1.SliceType.Normal = [0, 0, 1]

# Color by velocity magnitude
disp = Show(slice1, GetActiveViewOrCreate('RenderView'))
ColorBy(disp, ('POINTS', 'U', 'Magnitude'))

SaveScreenshot('velocity_slice.png', magnification=2)
```

---

## Key ParaView Keyboard Shortcuts

| Action | Shortcut |
|--------|---------|
| Fit all in view | F |
| Reset camera | Space |
| Toggle 3D axes | A |
| Next timestep | → |
| Previous timestep | ← |
| Play animation | P |
| Toggle visibility | H |

---

## Exercise 7A — Cavity Visualization

1. Open the cavity tutorial results in ParaView
2. Create a streamline visualization showing the main vortex
3. Plot the velocity profile `U_x` along a vertical line at x = 0.05 m
4. Extract the profile data to CSV and find where U_x = 0 (the vortex center)
5. Save a screenshot

---

## Key Takeaways

- Open OpenFOAM in ParaView with `touch case.foam && paraview case.foam`
- Filter pipeline: data → slice/clip → glyph/streamline → color by field
- Plot Over Line extracts profiles; export as CSV for further analysis
- Use Python scripting (pvpython) for reproducible post-processing
- Stream Tracer shows streamlines; Glyph shows velocity vectors
