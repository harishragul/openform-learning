# Lesson 7.2 — functionObjects: In-Situ Post-Processing

## Concept

functionObjects run **during** the simulation, extracting data without stopping the solver. They live in `system/controlDict` under the `functions` block. This is how you:
- Monitor forces on a wall
- Sample velocity at probe points
- Compute averages, integrals, and derived quantities
- Write surface data

---

## Adding functionObjects to controlDict

```cpp
functions
{
    // Each function object has a unique name
    residuals1
    {
        type    residuals;
        libs    (utilityFunctionObjects);
        fields  (p U k epsilon);
    }

    forceCoeffs1
    {
        type    forceCoeffs;
        libs    (forces);
        patches (cylinder);       // patch on the body
        rho     rhoInf;           // incompressible: use rhoInf
        rhoInf  1.225;            // air density kg/m³
        U       UInf;
        UInf    (10 0 0);         // freestream velocity
        liftDir (0 1 0);
        dragDir (1 0 0);
        pitchAxis (0 0 1);
        magUInf  10;
        lRef    0.1;              // reference length (chord)
        Aref    0.01;             // reference area
    }
}
```

---

## Common functionObjects

### 1. `probes` — Sample at specific points
```cpp
probes1
{
    type        probes;
    libs        (sampling);
    probeLocations
    (
        (0.5  0.0  0.005)    // x y z of probe point
        (1.0  0.0  0.005)
        (1.5  0.0  0.005)
    );
    fields      (U p);
    writeInterval 10;         // write every 10 timesteps
}
```
Output: `postProcessing/probes1/0/U` and `p` — time series at each point.

### 2. `forces` — Total force on a patch
```cpp
forces1
{
    type    forces;
    libs    (forces);
    patches (body);
    rho     rhoInf;
    rhoInf  1.225;
    CofR    (0 0 0);         // center of rotation for moment calculation
}
```

### 3. `fieldAverage` — Time-averaged fields (essential for LES)
```cpp
fieldAverage1
{
    type        fieldAverage;
    libs        (fieldFunctionObjects);
    timeStart   0.5;          // start averaging at t=0.5 s
    fields
    (
        U   { mean on; prime2Mean on; base time; }
        p   { mean on; prime2Mean off; base time; }
    );
}
```
Creates: `UMean`, `pMean`, `UPrime2Mean` (Reynolds stresses).

### 4. `streamlines` — Streamline seeding and writing
```cpp
streamlines1
{
    type        streamlines;
    libs        (fieldFunctionObjects);
    U           U;
    seedSampleSet
    {
        type    lineUniform;
        axis    x;
        start   (0 0.05 0.005);
        end     (0 0.001 0.005);
        nPoints 20;
    }
}
```

### 5. `surfaceSampling` — Sample on a surface (slice)
```cpp
surfaces1
{
    type    surfaces;
    libs    (sampling);
    fields  (U p);
    surfaces
    {
        zMidPlane
        {
            type    cuttingPlane;
            planeType pointAndNormal;
            pointAndNormalDict
            {
                point  (0 0 0.005);
                normal (0 0 1);
            }
            interpolate true;
        }
    }
}
```

### 6. `yPlus` — Wall y+ distribution
```cpp
yPlus1
{
    type    yPlus;
    libs    (fieldFunctionObjects);
    patches (walls);
}
```

### 7. `wallShearStress` — Shear stress on walls
```cpp
wallShearStress1
{
    type    wallShearStress;
    libs    (fieldFunctionObjects);
    patches (walls);
}
```

---

## Running functionObjects in Post-Processing Mode

You don't have to re-run the simulation! Apply function objects to existing results:

```bash
simpleFoam -postProcess -func forceCoeffs1 -latestTime
```

Or use the `postProcess` utility:
```bash
postProcess -func "wallShearStress" -latestTime
postProcess -func "yPlus" -latestTime
```

---

## Reading functionObject Output

Results go to `postProcessing/`:
```
postProcessing/
├── forces1/
│   └── 0/
│       └── force.dat        ← time vs. (Fx Fy Fz) (pressure)
│           forceCoeff.dat   ← time vs. Cd, Cl
├── probes1/
│   └── 0/
│       ├── U                ← time series at each probe
│       └── p
└── fieldAverage1/
    └── ...
```

Parse with Python or gnuplot:
```python
import numpy as np
data = np.loadtxt('postProcessing/forces1/0/forceCoeff.dat', comments='#')
time = data[:, 0]
Cd   = data[:, 1]
Cl   = data[:, 2]
```

---

## Exercise 7B — Monitoring Forces

1. Add a `forces1` functionObject to the pitzDaily simpleFoam tutorial
2. Add a `probes1` that monitors U at 3 points downstream of the step
3. Run for 200 iterations
4. Plot Cd vs. iteration number
5. At what iteration does Cd stabilize?

---

## Key Takeaways

- functionObjects run **during** the simulation — no need to restart to extract data.
- Define them in `system/controlDict` under `functions {}`.
- `probes`: point-wise time series. `forces`: integrated force/moment on patches.
- `fieldAverage`: required for LES statistics. `yPlus`: check mesh quality at walls.
- Use `postProcess -func <name>` to apply functions to existing results without re-running.
- Output goes to `postProcessing/` — read with Python or gnuplot.
