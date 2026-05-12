# Lesson 6.2 — LES, DES, and DNS

## Concept

RANS models *all* turbulent scales. LES (Large Eddy Simulation) resolves large eddies and models only the small subgrid-scale (SGS) ones. DNS (Direct Numerical Simulation) resolves everything — no modeling at all.

```
Energy spectrum:
E(k) │\
     │ \   ← large eddies (resolved by LES + DNS)
     │  \
     │   \____  ← small eddies (modeled in LES, resolved in DNS)
     └──────────→ wavenumber k
          ↑ LES filter
```

### Comparison

| Method | Models | Cost vs RANS | Accuracy | Use Case |
|--------|--------|-------------|----------|----------|
| RANS | All turbulence | 1× | Moderate | Engineering |
| DES | Far-field RANS, near-wall LES | 10–100× | High | Bluff bodies, large sep. |
| LES | Subgrid scales only | 100–1000× | Very high | Research, acoustics |
| DNS | Nothing | 10⁶× | Exact | Fundamental research |

---

## LES in OpenFOAM

### Solver
Use `pimpleFoam` with turbulence set to LES:

`constant/turbulenceProperties`:
```cpp
simulationType  LES;

LES
{
    LESModel    Smagorinsky;    // or WALE, dynamicKEqn, dynamicLagrangian
    turbulence  on;
    delta       cubeRootVol;    // filter width = cube root of cell volume
    printCoeffs on;
}
```

### LES Models

| Model | Notes |
|-------|-------|
| `Smagorinsky` | Classic, simple. Fixed C_s = 0.1. Over-diffusive near walls. |
| `WALE` | Wall-Adapting Local Eddy-viscosity. Better near walls. |
| `dynamicKEqn` | Dynamic Smagorinsky constant. Most accurate, more expensive. |
| `dynamicLagrangian` | Lagrangian averaging of dynamic constant. |

### Mesh Requirements for LES

LES requires **much finer meshes** than RANS:
- In boundary layers: y+ ~ 1 (must resolve viscous sublayer)
- In the domain: cells should be roughly isotropic (Δx ≈ Δy ≈ Δz)
- Rule of thumb: LES mesh has 10–100× more cells than a RANS mesh for the same geometry

### Time Step for LES
LES requires Courant number < 0.5 (ideally < 0.2) to resolve turbulent timescales.

```cpp
// In controlDict:
maxCo  0.5;
adjustTimeStep  yes;
deltaT  1e-5;
```

### Statistical Sampling
LES is inherently transient — you must time-average results:

```cpp
// In system/controlDict > functions:
fieldAverage1
{
    type        fieldAverage;
    libs        (fieldFunctionObjects);
    timeStart   0.1;           // start averaging after flow develops
    fields
    (
        U  { mean on; prime2Mean on; base time; }
        p  { mean on; prime2Mean off; base time; }
    );
}
```

This creates `UMean`, `UPrime2Mean` (Reynolds stress), `pMean` fields.

---

## DES (Detached Eddy Simulation)

Hybrid approach: RANS in attached boundary layers, LES in separated regions.

```cpp
LES
{
    LESModel    SpalartAllmarasDES;   // or kOmegaSSTDES
}
```

Good for: bluff bodies with large separation where LES of the entire boundary layer is too expensive.

---

## DNS: Just for Context

DNS resolves the Kolmogorov scales (smallest turbulent eddies). The mesh requirement scales as Re^(9/4):
- Re = 1000: ~4×10⁸ cells
- Re = 10000: ~10¹¹ cells

DNS is impractical for engineering applications. It's used for:
- Generating datasets to validate RANS/LES models
- Understanding fundamental turbulence physics

---

## Exercise 6B — LES of Cube in Channel

1. Copy `$FOAM_TUTORIALS/incompressible/pimpleFoam/LES/channel395` (or similar LES tutorial)
2. Run for 2 flow-through times without averaging, then enable fieldAverage
3. After collecting statistics, plot UMean (streamwise velocity profile)
4. Compare the turbulent velocity profile to the log-law: `U+ = (1/κ)*ln(y+) + B` where κ=0.41, B=5.2

---

## Key Takeaways

- RANS: cheap, models all turbulence. LES: expensive, resolves large eddies. DNS: exact, impractical.
- LES uses `simulationType LES` in `turbulenceProperties`; solver is `pimpleFoam`.
- LES requires much finer mesh (y+ ~1) and smaller timestep (Co < 0.5).
- Always time-average LES results using `fieldAverage` function object.
- Smagorinsky is simplest LES model; WALE/dynamic are more accurate near walls.
- DES blends RANS (attached BL) and LES (separated regions) — good engineering compromise.
