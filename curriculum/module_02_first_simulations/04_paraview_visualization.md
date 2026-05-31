# Lesson 2.4 — Visualizing Results in ParaView

## Concept

ParaView is not just a viewer — it's a full data analysis pipeline. Every operation you apply (slice, glyph, plot) is a *filter* that sits on top of your data source. Understanding the pipeline model is the key to using ParaView fluently.

---

## The ParaView Pipeline Model

```
Source (cavity.foam)
    └── Filter 1 (Glyph → velocity arrows)
    └── Filter 2 (Slice → cross-section)
         └── Filter 3 (Plot Over Line → velocity profile)
```

Each filter takes the output of the previous one as input. You can branch the pipeline — multiple filters on the same source simultaneously. The eye icon in the Pipeline Browser toggles visibility of each branch independently.

---

## Loading OpenFOAM Results

```bash
# ESI version — create a dummy .foam file first:
touch case.foam
paraview case.foam &

# Foundation version:
paraFoam &
```

In ParaView:
1. Select `cavity.foam` in Pipeline Browser
2. In Properties: select which fields to load (U, p — check both)
3. Click **Apply**
4. Use the time controls (play button / time field) to step through timesteps

---

## Color Maps — Getting Useful Visualisation

### Changing color map
1. Select the object in Pipeline Browser
2. Click **Edit** (paintbrush icon) next to the color bar
3. Choose a preset: **Cool to Warm** (blue→red) is standard for velocity/pressure

### Setting a fixed range
By default ParaView rescales color range per timestep — misleading for animation.
Fix: click the lock icon on the color bar to fix the range across all times.

### Scientific color maps to use
- **Cool to Warm**: general purpose, intuitive (blue = low, red = high)
- **Viridis**: perceptually uniform, good for publications
- **Rainbow**: avoid — misleading for quantitative analysis

---

## Key Filters

### 1. Slice — extract a 2D cross-section from 3D data
```
Filters → Common → Slice
```
- Set Origin and Normal to define the cut plane
- For a Y=0.05 horizontal slice: Origin=(0.05, 0.05, 0.005), Normal=(0, 1, 0)
- Color by any field on the slice

### 2. Plot Over Line — extract a 1D profile
```
Filters → Common → Plot Over Line
```
- Set Point 1 and Point 2 to define the line
- For the vertical centreline of the cavity (x=0.05, from bottom to top):
  - Point 1: (0.05, 0.0, 0.005)
  - Point 2: (0.05, 0.1, 0.005)
- Result: a line chart of any field vs position
- This is the standard method for validating against benchmark data (Ghia et al. 1982)

### 3. Probe Location — extract time history at one point
```
Filters → Common → Probe Location
```
- Set a single point (x, y, z)
- Result: value of all fields at that point over all timesteps
- Use "Plot Data" to see time history

### 4. Stream Tracer — streamlines
```
Filters → Common → Stream Tracer
```
- Vectors: U
- Seed Type: Line Source (vertical line in domain center works well)
- Color by velocity magnitude to see speed along streamlines

### 5. Glyph — velocity arrows
```
Filters → Common → Glyph
```
- Glyph Type: Arrow
- Orientation Array: U
- Scale Array: U, Vector Scale Mode: Scale by Magnitude
- Scale Factor: 0.1 (adjust for readability)
- For 2D z-fighting fix: add Transform filter, set Translate Z = 0.001

---

## Saving Output

### Screenshot
```
File → Save Screenshot
```
Set resolution (2000×2000 for publications), format PNG.

### Animation (all timesteps)
```
File → Save Animation
```
Saves each timestep as a frame. Output format: PNG sequence or AVI.

---

## Validating Against Benchmark Data — Ghia et al. (1982)

The lid-driven cavity is one of the most benchmarked problems in CFD. Ghia et al. (1982) published the exact velocity profiles at Re=100, 400, 1000.

Procedure:
1. Run your Re=100 case with a fine enough mesh (at least 40×40)
2. Apply **Plot Over Line** along the vertical centreline (x=0.05)
3. Plot U (x-velocity) vs Y position
4. Compare to Ghia et al. tabulated data

If your profile matches: your mesh, BCs, and solver are correct. This is the standard validation test for incompressible flow solvers.

---

## Exercise 2D — ParaView Workflow

1. Load your Re=100 case in ParaView
2. Apply **Plot Over Line** along the vertical centreline — plot U vs Y
3. What is the U velocity at the vortex centre (approximately Y=0.05)?
4. Apply **Probe Location** at the vortex centre point — what is the pressure there?
5. Save a screenshot of your pressure + glyph visualization

---

## Key Takeaways

- ParaView is a filter pipeline: source → filters → output. Each filter branches independently.
- Fix color range with the lock icon — otherwise animation rescales per frame.
- **Plot Over Line** extracts 1D profiles — the standard method for benchmark validation.
- **Probe Location** extracts time history at a single point — useful for monitoring convergence in post-processing.
- Always save solver output AND screenshots — results are not reproducible without the case files.
