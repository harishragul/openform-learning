# Lesson 2.3 — Reading Solver Output and Log Files

## Concept

The log file is your simulation's diary. Every iteration, every convergence step, every error is recorded there. Learning to read it fluently is the difference between a CFD engineer who knows what their simulation is doing and one who just hopes it converged.

---

## Anatomy of a Log File

A typical `icoFoam` log has four sections:

### Section 1 — Header (printed once at startup)
```
/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  11
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
Build  : ...
Exec   : icoFoam
Date   : May 30 2026
Time   : 10:23:14
Host   : "MacBookPro"
PID    : 12345
```
Useful: confirms which solver ran, when, on which machine. Essential when you have many logs.

### Section 2 — Mesh and Setup Info (printed once)
```
Create time
Create mesh for time = 0

PISO: Operating solver in PISO mode

Reading transportProperties
Reading field p
Reading field U
Reading/calculating face flux field phi

Selecting incompressible transport model Newtonian
Selecting turbulence model type laminar
```
Confirms: mesh loaded, fields initialised, turbulence model selected. If OpenFOAM can't find a file, the error appears here.

### Section 3 — Time Loop (printed every timestep — the main event)
```
Time = 0.005                             ← current simulation time

smoothSolver:  Solving for Ux,
    Initial residual = 0.200,            ← residual BEFORE solving this timestep
    Final residual   = 6.45e-06,         ← residual AFTER solving (should be << initial)
    No Iterations 15                     ← iterations needed to reach final residual

smoothSolver:  Solving for Uy,
    Initial residual = 0.198,
    Final residual   = 7.12e-06,
    No Iterations 14

PISO: Solving for p,
    Initial residual = 0.543,
    Final residual   = 4.21e-07,
    No Iterations 35
PISO: Solving for p,                     ← second PISO corrector (nCorrectors = 2)
    Initial residual = 0.031,
    Final residual   = 8.10e-08,
    No Iterations 22

PISO: Solving for p,                     ← third PISO corrector
    ...

continuityErrors : sum local = 3.2e-10,  ← how well mass is conserved
                   global = -1.4e-11,    ← should be < 1e-3 at minimum, ideally < 1e-6
                   cumulative = -1.4e-11

ExecutionTime = 0.03 s  ClockTime = 0 s  ← wall-clock time elapsed
```

### Section 4 — Footer (printed once at end)
```
End

Finalising parallel run
```

---

## Initial vs Final Residual — The Key Distinction

**Initial residual**: how wrong the solution is *at the start* of this timestep, based on the solution from the previous timestep. This tells you how much change is happening between timesteps.

**Final residual**: how wrong the solution is *after* the iterative solve. This tells you how well the linear system was solved within this timestep.

Rule of thumb:
- Final residual should be at least 100× smaller than initial residual.
- If they're similar, the solver isn't converging within the timestep — increase `maxIter` in `fvSolution`.

The initial residual of each timestep ≈ the final residual of the previous timestep. As the simulation approaches steady state (or a periodic state), initial residuals stop decreasing.

### Residual vs Correction — A Critical Distinction

The residual is NOT the difference between two consecutive iteration values. That difference is called the **correction**.

For a simple equation `2x = 10`:
- x = 2.0 → residual = |10 - 4| = 6   (large)
- x = 2.5 → residual = |10 - 5| = 5   (still large)
- correction = 2.5 - 2.0 = 0.5         (small)

A small correction does NOT mean a small residual. The solver could take tiny steps and still be far from satisfying the equation. This is why OpenFOAM uses residuals — not corrections — as convergence criteria. The residual measures equation satisfaction directly by plugging the current solution back into `A·x = b` and computing `|b - A·x|`.

---

## continuityErrors

```
continuityErrors : sum local = 3.2e-10, global = -1.4e-11, cumulative = -1.4e-11
```

This measures how well the continuity equation (`∇·U = 0`) is satisfied. In words: how much mass is being created or destroyed in the domain (there should be none).

- `local`: worst-case cell-by-cell error
- `global`: net mass imbalance over the whole domain
- `cumulative`: accumulated since t=0

**Acceptable**: global < 1e-3. **Good**: < 1e-6. **Bad**: > 1e-2 (serious mass conservation violation — check mesh or BCs).

---

## ExecutionTime vs ClockTime

```
ExecutionTime = 1.23 s  ClockTime = 2 s
```

- `ExecutionTime`: CPU time consumed (what the processor actually did)
- `ClockTime`: wall-clock time elapsed (what your watch shows)

For a single-core run, they're nearly equal. For parallel runs, `ExecutionTime` = sum across all cores; `ClockTime` = real elapsed time. Efficiency = ExecutionTime / (nCores × ClockTime).

---

## Monitoring Residuals in Real Time

### Option 1 — Live terminal filter
```bash
tail -f log.icoFoam | grep "Initial residual"
```
Shows only the initial residuals scrolling as the run progresses. Useful for catching divergence early.

### Option 2 — postProcess utility
```bash
# After the run (or while running in background):
postProcess -func residuals
```
Creates `postProcessing/residuals/0/residuals.dat` — a time-series file of all residuals.

### Option 3 — foamMonitor (ESI versions)
```bash
foamMonitor -l postProcessing/residuals/0/residuals.dat
```
Plots residuals in a live graph window.

### Reading residuals.dat manually
```bash
cat postProcessing/residuals/0/residuals.dat
# Time    Ux           Uy           p
# 0.005   0.200        0.198        0.543
# 0.01    0.143        0.141        0.382
# ...
```

---

## What Good Convergence Looks Like

```
Time = 0.005    Ux initial = 0.200    p initial = 0.543
Time = 0.010    Ux initial = 0.143    p initial = 0.382
Time = 0.050    Ux initial = 0.021    p initial = 0.056
Time = 0.200    Ux initial = 0.001    p initial = 0.003
Time = 0.500    Ux initial = 3.2e-5   p initial = 8.1e-5   ← converged
```

Residuals decrease monotonically toward zero. Final state is steady.

## What Divergence Looks Like

```
Time = 0.005    Ux initial = 0.200
Time = 0.010    Ux initial = 0.350    ← going UP
Time = 0.015    Ux initial = 1.240
Time = 0.020    Ux initial = 47.3
Time = 0.025    Ux initial = 4.7e+08
...
Floating point exception (core dumped)
```

The moment you see residuals climbing rather than falling — stop the run immediately (`touch stop`), diagnose the cause, fix it, restart.

---

## Exercise 2C — Read Your Own Log

Open your `log.icoFoam` from the Re=100 run and answer:

1. What was the initial residual of `Ux` at the first timestep?
2. What was the final residual of `p` at the last timestep?
3. What is the `continuityErrors` global value? Is it acceptable?
4. How many PISO correctors ran each timestep? (Count the "Solving for p" lines per time block)
5. Run `postProcess -func residuals` and open the `.dat` file — does the residual trend match what you expected?

---

## Key Takeaways

- The log has four sections: header, setup info, time loop, footer. The time loop is what you read.
- **Initial residual** = error entering this timestep. **Final residual** = error after solving. Final should be 100× smaller than initial.
- **continuityErrors global** should be < 1e-3. If not, check your mesh and boundary conditions.
- Residuals climbing (not falling) = divergence. Stop immediately, diagnose, don't just reduce deltaT.
- `postProcess -func residuals` extracts residual history for plotting.
- `tail -f log | grep "Initial residual"` is your real-time convergence monitor.
