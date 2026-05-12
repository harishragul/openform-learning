# OpenFOAM Quick Reference Cheat Sheet

## Essential Commands

```bash
# Source OpenFOAM (do this first in every session)
source /usr/lib/openfoam/openfoam2312/etc/bashrc    # ESI
source /opt/openfoam11/etc/bashrc                    # Foundation

# Navigate to tutorials
cd $FOAM_TUTORIALS

# Mesh generation
blockMesh                    # structured hex mesh
snappyHexMesh -overwrite     # unstructured mesh from STL
surfaceFeatureExtract        # extract feature edges from STL

# Mesh check
checkMesh                    # validate quality
checkMesh -allGeometry       # detailed geometry checks

# Run solver (always tee the output!)
icoFoam 2>&1 | tee log.icoFoam
simpleFoam 2>&1 | tee log.simpleFoam
pimpleFoam 2>&1 | tee log.pimpleFoam

# Parallel
decomposePar
mpirun -np 4 simpleFoam -parallel 2>&1 | tee log.simpleFoam
reconstructPar
reconstructPar -latestTime

# Post-processing
touch case.foam && paraview case.foam &    # ESI
paraFoam &                                  # Foundation
postProcess -func "yPlus" -latestTime
postProcess -func "forceCoeffs" -latestTime
foamToVTK                                   # convert to VTK

# Stop a running simulation gracefully
touch stop

# Utilities
foamVersion                  # check version
foamInfo icoFoam             # info about a solver
foamSearch $WM_PROJECT_DIR U # search source for symbol
```

---

## Case Directory Structure

```
case/
├── 0/                     ← initial & boundary conditions (one file per field)
│   ├── U                  ← velocity [m/s]
│   ├── p                  ← kinematic pressure [m²/s²]
│   ├── k                  ← turbulent kinetic energy [m²/s²]
│   ├── epsilon            ← dissipation [m²/s³]
│   └── nut                ← turbulent viscosity [m²/s]
├── constant/
│   ├── polyMesh/          ← mesh files
│   ├── transportProperties← fluid properties
│   └── turbulenceProperties
└── system/
    ├── controlDict        ← time, output control
    ├── fvSchemes          ← numerical schemes
    ├── fvSolution         ← linear solvers & relaxation
    ├── blockMeshDict      ← blockMesh geometry
    └── decomposeParDict   ← parallel decomposition
```

---

## Solver Quick Reference

| Solver | Physics | Use Case |
|--------|---------|----------|
| `icoFoam` | Transient, laminar, incompressible | Learning, Re<2300 |
| `simpleFoam` | Steady, turbulent, incompressible | Pipes, HVAC, aero |
| `pimpleFoam` | Transient, turbulent, incompressible | Unsteady, LES |
| `rhoPimpleFoam` | Transient, compressible | Ma > 0.3 |
| `interFoam` | Two-phase VOF | Free surface, waves |
| `buoyantSimpleFoam` | Steady, heat transfer | Natural convection |

---

## Boundary Condition Quick Reference

### Velocity (U)
```
fixedValue      → known velocity (inlet)
noSlip          → zero velocity at wall
zeroGradient    → outlet (fully developed)
inletOutlet     → outlet allowing backflow
pressureInletVelocity → inlet with known pressure
movingWallVelocity → rotating/moving walls
```

### Pressure (p)
```
fixedValue    → known pressure (outlet usually)
zeroGradient  → inlet (when velocity is fixed)
totalPressure → inlet with known stagnation pressure
```

### Rule: at each patch, fix EITHER U OR p — not both!

| Patch | U | p |
|-------|---|---|
| Velocity inlet | `fixedValue` | `zeroGradient` |
| Pressure outlet | `inletOutlet` | `fixedValue` |
| Wall | `noSlip` | `zeroGradient` |

---

## Turbulence Models

```cpp
// constant/turbulenceProperties

simulationType  RAS;     // RANS
// or
simulationType  LES;     // Large Eddy Simulation

RAS { RASModel  kOmegaSST; }   // recommended for most cases
RAS { RASModel  kEpsilon; }    // free shear flows
LES { LESModel  WALE; }        // LES, better near walls
```

### Inlet Turbulence Estimates
```
I (intensity) = 0.05  for developed pipe flow
l (length scale) = 0.07 * D_hydraulic

k       = 1.5 * (U * I)²
epsilon = 0.09^0.75 * k^1.5 / l
omega   = k^0.5 / (0.09^0.25 * l)
```

### y+ Guide
```
y+ ~ 1:       resolve viscous sublayer (low-Re wall treatment)
y+ 5-30:      AVOID (buffer layer)
y+ 30-300:    log-law region (use wall functions)
```

---

## Dimensions Notation

```
[kg  m  s  K  mol  A  cd]

Velocity U:        [0  1 -1  0  0  0  0]   m/s
Pressure p/ρ:      [0  2 -2  0  0  0  0]   m²/s²
Kinematic visc ν:  [0  2 -1  0  0  0  0]   m²/s
Density ρ:         [1 -3  0  0  0  0  0]   kg/m³
k:                 [0  2 -2  0  0  0  0]   m²/s²
epsilon:           [0  2 -3  0  0  0  0]   m²/s³
```

---

## Convergence Rules of Thumb (SIMPLE)

```
Good convergence:   residuals < 1e-4 for all fields
Stalled:            residuals plateau above 1e-3 → check BCs, mesh
Diverging:          residuals growing → reduce relaxation or timestep
Diverged:           NaN/Inf → check for inverted cells, wrong BCs

Relaxation factors (starting values):
  p: 0.3    U: 0.7    k/epsilon: 0.7
```

---

## Common Errors and Fixes

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `Floating point exception` | Divergence, bad mesh | Reduce dt, fix mesh |
| `Patch not found` | BC name mismatch | Check boundary file vs 0/ |
| `dimensions error` | Wrong units | Check dimensions in field file |
| `Cannot find file` | Missing 0/ field | Copy from tutorial or create |
| `checkMesh max non-orth > 85` | Bad mesh | Refine, use correctors |
| `GAMG: max iterations reached` | Tolerance too tight | Increase relTol to 0.1 |
