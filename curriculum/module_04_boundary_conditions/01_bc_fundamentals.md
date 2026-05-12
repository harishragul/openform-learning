# Lesson 4.1 — Boundary Conditions: Types, Physics, Dictionary Syntax

## Concept

Boundary conditions (BCs) are the mathematical statements that tell the solver what the fluid is doing at the edges of your domain. Getting BCs wrong is the single most common source of incorrect OpenFOAM results — even with a perfect mesh and good numerics.

### The Three Mathematical Types

**1. Dirichlet (fixedValue)** — specify the field value at the boundary
```
U = (1 0 0)   ← velocity is exactly 1 m/s in x at this face
```

**2. Neumann (zeroGradient)** — specify the gradient at the boundary
```
∂U/∂n = 0    ← velocity gradient normal to boundary is zero
             ← "the field doesn't change across this boundary"
```

**3. Robin (mixed)** — weighted combination of Dirichlet and Neumann
```
αU + β(∂U/∂n) = γ    ← used internally for many OpenFOAM BCs
```

---

## Anatomy of a Boundary Condition File

Every field file in `0/` has this structure:

```cpp
FoamFile
{
    version  2.0;
    format   ascii;
    class    volVectorField;    // or volScalarField for p, k, epsilon
    object   U;
}

dimensions  [0 1 -1 0 0 0 0];  // m/s

internalField  uniform (0 0 0); // starting condition everywhere

boundaryField
{
    inlet                       // patch name (must match mesh boundary)
    {
        type    fixedValue;
        value   uniform (1 0 0);
    }

    outlet
    {
        type    zeroGradient;
    }

    walls
    {
        type    noSlip;         // shorthand for fixedValue (0 0 0)
    }

    frontAndBack
    {
        type    empty;          // 2D: not a real boundary
    }
}
```

---

## Most Important BCs: Quick Reference

### Velocity (U)

| BC Type | Dictionary Keyword | Use Case |
|---------|-------------------|----------|
| Fixed velocity | `fixedValue` | Known inlet velocity |
| No-slip wall | `noSlip` | Solid walls |
| Moving wall | `movingWallVelocity` | Rotating walls |
| Zero gradient | `zeroGradient` | Outlet (fully developed) |
| Inlet/outlet | `inletOutlet` | Outlet that might see backflow |
| Freestream | `freestreamVelocity` | External aerodynamics far-field |

### Pressure (p)

| BC Type | Dictionary Keyword | Use Case |
|---------|-------------------|----------|
| Fixed pressure | `fixedValue` | Outlet with known pressure |
| Zero gradient | `zeroGradient` | Inlet (when velocity is fixed) |
| Total pressure | `totalPressure` | Inlet with known total pressure |
| Pressure inlet/outlet | `prghPressure` | Buoyancy-driven flows |

**Important rule**: For incompressible flow, at every patch you must fix EITHER velocity OR pressure — not both, not neither.

| Patch | U | p |
|-------|---|---|
| Inlet (fixed velocity) | `fixedValue` | `zeroGradient` |
| Outlet (fixed pressure) | `inletOutlet` | `fixedValue (0)` |
| Inlet (fixed pressure) | `pressureInletVelocity` | `totalPressure` |

---

## Worked Example: Simple Channel Flow BCs

`0/U`:
```cpp
boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform (10 0 0);   // 10 m/s uniform inlet
    }
    outlet
    {
        type    inletOutlet;
        inletValue  uniform (0 0 0);
        value       uniform (0 0 0);
    }
    topWall
    {
        type    noSlip;
    }
    bottomWall
    {
        type    noSlip;
    }
    frontBack
    {
        type    empty;
    }
}
```

`0/p`:
```cpp
boundaryField
{
    inlet
    {
        type    zeroGradient;
    }
    outlet
    {
        type    fixedValue;
        value   uniform 0;   // reference pressure = 0 (gauge)
    }
    topWall
    {
        type    zeroGradient;
    }
    bottomWall
    {
        type    zeroGradient;
    }
    frontBack
    {
        type    empty;
    }
}
```

---

## Exercise 4A

For each of these physical scenarios, specify the correct BC type for U and p at each patch:

1. **Pipe flow**: fluid enters at 2 m/s, exits to atmosphere (p=0), walls are solid.
2. **Wind tunnel**: far-field freestream at (30 0 0), solid body in center, outlet is pressure outlet.
3. **Heated room**: buoyancy-driven natural convection, all walls are solid, one vent open to atmosphere.

---

## Key Takeaways

- BCs tell the solver what happens at domain edges — wrong BCs give wrong physics.
- Three mathematical types: Dirichlet (fixed value), Neumann (fixed gradient), Robin (mixed).
- Golden rule: at each patch, fix either velocity OR pressure — never both, never neither.
- `noSlip` = zero velocity at wall; `zeroGradient` = field doesn't change across boundary.
- Patch names in `0/` files must **exactly** match patch names in `constant/polyMesh/boundary`.
