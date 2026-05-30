# Lesson 2.2 — Running Simulations and Reading Output

## Concept

Running an OpenFOAM simulation correctly isn't just about typing the solver name. You need to:
- Know which solver to use
- Understand what the output means
- Recognize convergence vs. divergence
- Know how to stop, restart, and continue runs

---

## Choosing the Right Solver

OpenFOAM has 100+ solvers. The key ones you'll use most:

| Solver | Physics | When to use |
|--------|---------|-------------|
| `icoFoam` | Transient, incompressible, laminar | Re < 2300, learning |
| `simpleFoam` | Steady-state, incompressible, turbulent | Most industrial internal flows |
| `pimpleFoam` | Transient, incompressible, turbulent | Unsteady industrial flows |
| `pisoFoam` | Transient, incompressible, turbulent | Like pimpleFoam, older |
| `rhoPimpleFoam` | Transient, compressible | Subsonic/supersonic flows |
| `interFoam` | Two-phase (VOF), incompressible | Free surface, wave breaking |
| `buoyantPimpleFoam` | Heat transfer + natural convection | Buoyancy-driven flows |

Check which solver a tutorial uses:
```bash
grep application system/controlDict
```

---

## The Run Sequence

Every simulation follows this pattern:

```bash
# 1. Generate mesh
blockMesh            # or snappyHexMesh for complex geometry

# 2. Validate mesh
checkMesh

# 3. Set initial conditions (already done in 0/ directory)

# 4. Run solver (always capture output)
simpleFoam 2>&1 | tee log.simpleFoam

# 5. Post-process
postProcess -func residuals    # plot convergence
paraview case.foam &           # visualize
```

---

## Anatomy of a Log File

For `simpleFoam` (steady-state SIMPLE algorithm):

```
/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           |
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/

...

// SIMPLE iteration loop:

Time = 1                         ← pseudo-time step (iterations for steady)

smoothSolver:  Solving for Ux,
    Initial residual = 1,        ← first iteration: fully unresolved
    Final residual = 0.0812,
    No Iterations 8

smoothSolver:  Solving for Uy,
    Initial residual = 1,
    Final residual = 0.0643,
    No Iterations 8

GAMG:  Solving for p,            ← GAMG = Geometric-Algebraic Multi-Grid
    Initial residual = 1,
    Final residual = 0.0456,
    No Iterations 2

...

Time = 50
smoothSolver:  Solving for Ux,
    Initial residual = 3.4e-05,  ← getting small — approaching convergence
    Final residual = 2.1e-07,
    No Iterations 3
```

**Convergence criteria** (set in `fvSolution`):
```cpp
residualControl
{
    p       1e-4;    // Stop when p residual < 1e-4
    U       1e-4;    // Stop when U residual < 1e-4
    k       1e-4;
    epsilon 1e-4;
}
```

---

## Recognizing Divergence

Bad signs in log output:
```
smoothSolver:  Solving for Ux,
    Initial residual = 127.4,    ← > 1 means something is very wrong
    ...

Floating point exception (core dumped)   ← solver crashed

nan  nan  nan  nan               ← Not a Number — numerical blow-up
```

Common causes of divergence — always diagnose from the residual history before touching `deltaT`:

| Cause | Symptom in log | Fix |
|-------|---------------|-----|
| Timestep too large (Co > 1) | residuals jump to 1e+10, then NaN | Reduce `deltaT` |
| Bad mesh quality | residuals won't drop below 0.1 | Fix mesh — run `checkMesh` |
| Wrong boundary conditions | residuals oscillate, never converge | Check BC types and values |
| Wrong units (Pa instead of m²/s²) | residuals explode immediately | Recalculate — use kinematic p |
| Under-relaxation too aggressive | residuals oscillate steadily | Reduce `relaxationFactors` in `fvSolution` |

**Diagnostic rule**: check whether the residual jumps > 1 immediately (BC or units problem) vs. slowly climbs over time (timestep or mesh problem). The shape of the divergence tells you the cause.

---

## Stopping and Restarting

### Stop gracefully mid-run:
```bash
# In another terminal, in the case directory:
touch stop              # graceful stop after current timestep
# or:
touch stopAt            # same effect
```

Or set in controlDict:
```cpp
stopAt  writeNow;       // write current state and stop
```

### Restart from latest time:
```cpp
// In controlDict:
startFrom   latestTime;   // automatically finds the last written directory
```

### Restart from specific time:
```cpp
startFrom   startTime;
startTime   0.3;          // restart from t = 0.3 s
```

---

## Monitoring Convergence in Real Time

```bash
# Watch residuals as simulation runs:
tail -f log.icoFoam | grep "Solving for"

# Plot residuals (creates postProcessing/ directory):
foamMonitor -l postProcessing/residuals/0/residuals.dat
```

---

## Exercise 2B

1. Open `system/controlDict` in the cavity case.
2. Change `endTime` to `1.0` and `writeInterval` to `40`.
3. Re-run `icoFoam` and check: how many time directories are written now?
4. Look at the log: what are the final residuals for `Ux` and `Uy`?
5. Bonus: add `stopAt writeNow;` to controlDict, restart the run, and observe what happens.

---

## Key Takeaways

- Choose the solver based on physics: steady/transient, laminar/turbulent, compressible/incompressible.
- Always capture solver output: `solver 2>&1 | tee log.solverName`
- Residuals decreasing to < 1e-4 (or your set tolerance) = converged.
- Residuals increasing or going to NaN = divergence — fix the cause, don't just reduce timestep blindly.
- `touch stop` gracefully halts any running simulation.
- `startFrom latestTime` resumes from where you left off.
