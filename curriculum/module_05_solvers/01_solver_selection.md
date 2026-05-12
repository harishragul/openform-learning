# Lesson 5.1 — Solver Selection and the fvSolution/fvSchemes Dictionaries

## Concept

OpenFOAM ships over 100 solvers. Choosing the wrong one means solving the wrong equations. This lesson teaches you how to match your physical problem to the right solver, and how to configure the numerical settings.

---

## Solver Decision Tree

```
Is the flow incompressible? (Ma < 0.3)
├── YES
│   ├── Is it steady-state? (stationary solution wanted)
│   │   ├── YES → simpleFoam (turbulent) | icoFoam (laminar, unsteady is wrong!)
│   │   └── NO  (transient)
│   │       ├── Laminar? → icoFoam
│   │       ├── Turbulent? → pimpleFoam
│   │       └── Two-phase? → interFoam
│   └── With heat transfer?
│       └── buoyantSimpleFoam (steady) | buoyantPimpleFoam (transient)
└── NO (compressible, Ma > 0.3)
    ├── Steady? → rhoSimpleFoam
    └── Transient? → rhoPimpleFoam
        └── Supersonic/shock? → rhoCentralFoam
```

---

## Key Solver Details

### `icoFoam` — Transient Laminar Incompressible
- Algorithm: PISO (Pressure-Implicit Split-Operator)
- Best for: Learning, Re < 2300, educational cases
- Control: `PISO { nCorrectors 2; nNonOrthogonalCorrectors 0; }`

### `simpleFoam` — Steady-State Turbulent Incompressible
- Algorithm: SIMPLE (Semi-Implicit Method for Pressure-Linked Equations)
- Best for: Pipes, ducts, HVAC, external aero steady state
- Control: `relaxationFactors { U 0.7; p 0.3; k 0.7; epsilon 0.7; }`

### `pimpleFoam` — Transient Turbulent Incompressible
- Algorithm: PIMPLE (merged PISO + SIMPLE, large timesteps possible)
- Best for: LES, unsteady flows, vortex shedding
- Control: `PIMPLE { nOuterCorrectors 2; nCorrectors 2; nNonOrthogonalCorrectors 1; }`

### `interFoam` — Two-Phase VOF
- Tracks interface between two immiscible fluids (water/air)
- Uses `alpha.water` field (0=air, 1=water)
- Control: `PIMPLE { momentumPredictor yes; nOuterCorrectors 3; }`

---

## fvSolution Dictionary Deep Dive

```cpp
FoamFile { ... }

solvers
{
    // Pressure equation (most important to get right)
    p
    {
        solver          GAMG;          // Geometric-Algebraic Multi-Grid
        smoother        GaussSeidel;
        tolerance       1e-06;         // absolute convergence criterion
        relTol          0.1;           // relative: reduce residual by 10x
    }

    // Velocity
    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-07;
        relTol          0.1;
        nSweeps         1;
    }

    // Turbulence fields (can use same settings)
    "(k|epsilon|omega|nuTilda)"   // regex pattern — applies to all
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-07;
        relTol          0.1;
    }
}

// SIMPLE controls (for simpleFoam)
SIMPLE
{
    nNonOrthogonalCorrectors  1;   // extra correction for non-orthogonal meshes
    consistent              yes;   // SIMPLEC variant — faster convergence

    residualControl           // stop when all residuals reach these values
    {
        p       1e-4;
        U       1e-4;
        "(k|epsilon|omega)"  1e-3;
    }
}

relaxationFactors           // under-relaxation for SIMPLE stability
{
    fields
    {
        p       0.3;        // pressure: aggressive relaxation needed
    }
    equations
    {
        U       0.7;        // velocity
        k       0.7;
        epsilon 0.7;
    }
}
```

### Linear Solver Options

| Solver | Best for | Notes |
|--------|---------|-------|
| `GAMG` | Pressure (elliptic equations) | Very fast for large meshes |
| `PCG` | Symmetric matrices (pressure) | Robust, slower than GAMG |
| `PBiCGStab` | Asymmetric (velocity, turbulence) | Good general choice |
| `smoothSolver` | Small/medium meshes | Simple, reliable |
| `diagonal` | Explicit equations | Trivially fast but limited |

---

## fvSchemes Dictionary Deep Dive

```cpp
FoamFile { ... }

// Time derivative discretization
ddtSchemes
{
    default  Euler;           // 1st order, bounded, unconditionally stable
    // alternatives:
    // CrankNicolson 0.9;    // 2nd order, blended (0.9 = mostly CN)
    // backward;             // 2nd order, fully implicit
    // steadyState;          // for simpleFoam (no time derivative)
}

// Gradient schemes
gradSchemes
{
    default         Gauss linear;      // 2nd order accurate
    grad(p)         Gauss linear;
    grad(U)         cellLimited Gauss linear 1;  // bounded, less oscillatory
}

// Divergence schemes (convection terms — most important for accuracy)
divSchemes
{
    default         none;              // force explicit specification

    // Velocity convection:
    div(phi,U)      Gauss linearUpwind grad(U);  // 2nd order, stable
    // alternatives:
    // Gauss linear;          // central differencing: accurate but unbounded
    // Gauss upwind;          // 1st order: diffusive but very stable
    // Gauss limitedLinear 1; // bounded linear
    // Gauss MUSCL;           // for LES: 2nd order, low diffusion

    // Turbulence:
    div(phi,k)      Gauss upwind;
    div(phi,epsilon) Gauss upwind;
}

// Laplacian schemes (diffusion terms)
laplacianSchemes
{
    default  Gauss linear corrected;   // corrected = orthogonal correction
    // for bad meshes: Gauss linear limited corrected 0.5;
}

// Face interpolation
interpolationSchemes
{
    default  linear;
}

// Surface-normal gradient
snGradSchemes
{
    default  corrected;    // most accurate
    // for bad meshes: limited corrected 0.5;
}
```

---

## Under-Relaxation Tuning Guide

For `simpleFoam`, if it diverges or oscillates:

| Symptom | Fix |
|---------|-----|
| Pressure oscillates | Reduce `p` relaxation to 0.2 |
| Velocity diverges | Reduce `U` relaxation to 0.5 |
| Very slow convergence | Increase relaxation factors toward 0.8-0.9 |
| Turbulence NaN | Set k/epsilon relaxation to 0.3-0.5 |

---

## Exercise 5A — Convergence Tuning

1. Copy the `$FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily` tutorial
2. Run it with default settings, recording iterations to convergence
3. Change pressure relaxation from 0.3 to 0.7 — what happens?
4. Try `nNonOrthogonalCorrectors 3` — what changes?
5. Switch `div(phi,U)` from `linearUpwind` to `upwind` and compare results visually

---

## Key Takeaways

- Solver selection depends on: steady vs. transient, laminar vs. turbulent, Ma number.
- `simpleFoam` = steady SIMPLE; `pimpleFoam` = transient PIMPLE; `icoFoam` = laminar PISO.
- `fvSolution` controls linear algebra: which solver, tolerances, relaxation.
- `fvSchemes` controls numerical discretization: time, gradient, divergence, laplacian.
- Under-relaxation in SIMPLE controls stability vs. convergence speed trade-off.
- GAMG is the fastest pressure solver for large meshes.
