# Lesson 1.3 — CFD Governing Equations (Intuitive Introduction)

## Concept

Before you trust a simulation, you need to understand what equations OpenFOAM is solving. You don't need to derive them — but you need to recognize them and understand what each term means physically.

### The Continuity Equation (Mass Conservation)

For an incompressible fluid (constant density):

```
∇·U = 0
```

In words: **the net flow of mass into any control volume is zero**. What goes in must come out. In 3D Cartesian coordinates:

```
∂u/∂x + ∂v/∂y + ∂w/∂z = 0
```

Analogy: Imagine water flowing through a pipe network. At every junction, the flow rate in equals flow rate out.

### The Momentum Equation (Newton's 2nd Law)

For incompressible, Newtonian fluids:

```
ρ (∂U/∂t + (U·∇)U) = -∇p + μ∇²U + ρg + f_body
```

Breaking it down:

| Term | Physical Meaning |
|------|-----------------|
| `ρ ∂U/∂t` | Time rate of change of momentum (inertia) |
| `ρ (U·∇)U` | Convective acceleration (momentum carried by flow) |
| `-∇p` | Pressure gradient force (pushes fluid from high to low pressure) |
| `μ∇²U` | Viscous diffusion (friction between fluid layers) |
| `ρg` | Gravity |
| `f_body` | Other body forces (magnetic, Coriolis, etc.) |

Analogy: A ball rolling down a hill accelerates due to gravity, slows due to friction, and curves due to pressure differences — fluids work the same way, just continuously distributed in space.

### Dimensionless Numbers You Must Know

**Reynolds Number (Re)**:
```
Re = ρUL/μ = UL/ν
```
- Ratio of inertial to viscous forces.
- Re < ~2300: laminar flow (smooth, predictable).
- Re > ~4000: turbulent flow (chaotic, mixing-dominated).
- In between: transitional.

**Courant Number (Co)**:
```
Co = U·Δt/Δx
```
- Measures how far a fluid parcel travels in one timestep relative to one cell.
- For explicit time-marching: Co < 1 is required for stability.
- OpenFOAM reports this automatically — watch it in solver output.

**Mach Number (Ma)**:
```
Ma = U/c   (c = speed of sound)
```
- Ma < 0.3: incompressible assumption is valid.
- Ma > 0.3: compressibility effects matter — use a compressible solver.

---

## OpenFOAM in Practice

OpenFOAM represents these equations as **tensor operations on fields**. The momentum equation in OpenFOAM C++ (simplified) looks like:

```cpp
// From icoFoam.C
fvVectorMatrix UEqn
(
    fvm::ddt(U)              // ∂U/∂t
  + fvm::div(phi, U)         // (U·∇)U  — convection
  - fvm::laplacian(nu, U)    // ν∇²U    — diffusion
);
```

This maps almost 1:1 with the math. `fvm::` means Finite Volume Method discretization (implicit), `fvc::` means explicit evaluation.

In `fvSchemes`, you control **how** each term is discretized:

```
divSchemes
{
    div(phi,U)   Gauss linearUpwind grad(U);  // upwind scheme for convection
}
```

In `fvSolution`, you control **how** the resulting linear system is solved:

```
solvers
{
    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-6;
    }
}
```

---

## Exercise 1C — Conceptual Check

Answer these questions (no simulation needed yet):

1. A liquid with viscosity μ = 0.001 Pa·s and density ρ = 1000 kg/m³ flows at U = 1 m/s through a pipe of diameter D = 0.01 m. What is Re? Is it laminar or turbulent?

2. In the momentum equation, which term is responsible for the no-slip condition at walls?

3. If your Courant number exceeds 1 during a simulation, what is likely to happen?

4. Why can we ignore the energy equation for slow-moving incompressible water?

---

## Key Takeaways

- The continuity equation enforces mass conservation: `∇·U = 0` for incompressible flow.
- The momentum equation is Newton's 2nd law: inertia = pressure + viscosity + body forces.
- Reynolds number separates laminar (Re < 2300) from turbulent (Re > 4000) flow.
- Courant number must stay < 1 for stable explicit time-stepping.
- OpenFOAM's C++ syntax mirrors the math: `fvm::ddt` = time derivative, `fvm::div` = divergence.
