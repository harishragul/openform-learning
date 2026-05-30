# Lesson 2.1 — The Lid-Driven Cavity (icoFoam)

## Concept

The lid-driven cavity is the "Hello World" of CFD. It's a square box filled with fluid. The top wall moves at a fixed velocity; all other walls are stationary. The moving lid drags the fluid, creating a large recirculating vortex.

```
  ←←← U = 1 m/s ←←←        (moving lid)
 ┌──────────────────────┐
 │                      │
 │     ↙ vortex ↗       │
 │                      │
 └──────────────────────┘
  (fixed walls, no-slip)
```

Why this case?
- Geometry is trivially simple (no meshing complexity)
- Has an analytical/benchmark solution for comparison
- Demonstrates all the key OpenFOAM concepts in one small case

---

## OpenFOAM in Practice

### Step 1: Copy the tutorial

```bash
mkdir -p ~/openfoam_learning
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity ~/openfoam_learning/
cd ~/openfoam_learning/cavity
```

### Step 2: Examine the mesh setup

```bash
cat system/blockMeshDict
```

Key section — the block definition:
```cpp
blocks
(
    hex (0 1 2 3 4 5 6 7)   // 8 vertices forming a hexahedral block
    (20 20 1)               // 20 cells in x, 20 in y, 1 in z (2D!)
    simpleGrading (1 1 1)   // uniform spacing
);
```

This creates a 20×20 structured mesh. Later you'll learn to refine it and use grading to cluster cells near walls.

### Step 3: Generate the mesh

```bash
blockMesh
```

Output tells you:
- Number of cells created
- Mesh bounding box
- Any errors (non-orthogonality, skewness)

Verify:
```bash
checkMesh
```

Watch for: **Max non-orthogonality** should be < 70°. **Max skewness** should be < 4. This mesh will be perfect.

### Step 4: Run the solver

```bash
icoFoam 2>&1 | tee log.icoFoam
```

The `2>&1 | tee` captures solver output to a log file while still printing to screen. Always do this — you'll want to examine the log later.

### Interpreting Solver Output

```
Time = 0.005                      ← current simulation time

smoothSolver:  Solving for Ux,    ← solving x-velocity
    Initial residual = 0.0812,    ← how far from converged
    Final residual = 7.01e-06,    ← converged to this
    No Iterations 12              ← took 12 iterations

smoothSolver:  Solving for Uy,    ← y-velocity
    ...

PISO: Solving for p,              ← pressure (PISO loop)
    ...

ExecutionTime = 0.03 s            ← wall-clock time so far
```

Residuals tell you how well the linear system is solved each timestep. **Good**: final residual << tolerance. **Bad**: residual not dropping, or exploding to `nan`/`inf`.

### Step 5: Visualize

```bash
# ESI version:
touch cavity.foam
paraview cavity.foam &

# Foundation version:
paraFoam &
```

#### Basic workflow
1. Click **Apply** to load the data
2. Select field **U** or **p** in the toolbar dropdown
3. Click **Play** to animate through time
4. Use **Filters → Common → Stream Tracer** to see streamlines

#### Pressure contour + velocity glyph overlay (recommended)

This is the clearest way to see both pressure and velocity simultaneously:

**Layer 1 — Pressure background:**
1. Select `cavity.foam` in Pipeline Browser
2. Change field to **p** in the toolbar dropdown
3. The surface now shows the pressure colour map

**Layer 2 — Velocity arrows on top:**
1. With `cavity.foam` selected, go to **Filters → Common → Glyph**
2. In Properties:
   - **Glyph Type**: `Arrow`
   - **Orientation Array**: `U`
   - **Scale Array**: `U`, **Vector Scale Mode**: `Scale by Magnitude`
   - **Scale Factor**: `0.1` (adjust until arrows are readable)
3. Color the Glyph by **U → Magnitude**
4. Click **Apply**

**Fix for 2D z-fighting** (arrows disappearing into the surface):
Since the cavity is one cell thick in z, glyphs and the surface are coplanar — they fight for the same pixel. Fix:
1. Select **Glyph1** in Pipeline Browser
2. **Filters → Common → Transform**
3. Set **Translate Z = 0.001**
4. Click Apply — glyphs now sit 1 mm in front of the surface

#### Why only cell data icons in ParaView (no point icons)?

OpenFOAM uses the **Finite Volume Method** — all field values (U, p) are stored as averages at **cell centres**, not at mesh vertices. ParaView shows a cell icon because the data lives in cells. To get smoother visualisation, apply **Filters → Cell Data to Point Data** which interpolates cell values to vertices. The underlying data doesn't change — it's display only.

---

## The Physics You Should See

**Re = 10** (default, ν = 0.01): One clean vortex sitting low in the cavity, biased toward bottom-left. Pressure nearly uniform — large ν means large pressure range is needed to drive flow against friction.

**Re = 100** (ν = 0.001): Vortex center shifts **upward and toward the geometric center**. Pressure range actually shrinks (fluid needs less pressure to move with lower viscosity), but becomes sharply concentrated in the top-right corner where the lid pushes fluid into the wall. Corner vortices exist but require mesh finer than 20×20 to resolve.

**Re = 1000** (ν = 0.0001): Primary vortex nearly centered. Secondary corner vortices clearly visible on a refined mesh. Flow approaches the benchmark solution of Ghia et al. (1982).

**Re = 10000**: Flow becomes unsteady — a steady solver will not converge. Requires `pimpleFoam`, a finer mesh, and a smaller timestep.

Reynolds number for the default case:
```
Re = U * L / ν = 1 * 0.1 / 0.01 = 10
```
(default ν = 0.01 m²/s — very viscous, Re = 10, purely laminar)

**Key counter-intuitive result**: Higher Re does NOT always mean larger pressure differences. For the cavity, lower viscosity means the fluid moves more freely — less pressure gradient is needed to drive it. What changes is *where* the pressure concentrates, not how large the total range is.

---

## Exercise 2A

Run the cavity tutorial and answer:

1. What is the maximum velocity magnitude in the domain at t = 0.5 s?
2. Where is the pressure highest? Lowest? Why?
3. How long did the simulation take (check `ExecutionTime` at the end of the log)?
4. How many time directories were written?

---

## Key Takeaways

- Lid-driven cavity: top wall moves, drags fluid into a recirculating vortex.
- `blockMesh` generates the structured mesh from `blockMeshDict`.
- `checkMesh` validates mesh quality — run it after every mesh generation.
- `icoFoam` is the transient laminar incompressible solver.
- Residuals in solver output indicate convergence quality — watch them carefully.
- Always save solver output to a log file with `tee`.
