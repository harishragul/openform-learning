# Lesson 6.1 — RANS Turbulence Models: k-epsilon and k-omega SST

## Concept

Most engineering CFD uses **RANS** (Reynolds-Averaged Navier-Stokes) turbulence modeling. The idea: decompose every quantity into a mean and a fluctuating part.

```
U = Ū + u'      (mean + fluctuation)
```

After averaging, a new stress term appears: the **Reynolds stress tensor** `−ρ<u'u'>`. This is the "closure problem" — we need additional equations to model it.

### The Boussinesq Hypothesis

Most RANS models assume turbulent stresses are proportional to the mean strain rate:
```
−ρ<u'u'> ≈ μ_t * (∇Ū + (∇Ū)^T) − (2/3)ρk*I
```
where `μ_t` is the **turbulent (eddy) viscosity** — the quantity all two-equation models solve for.

---

## k-epsilon Model

Solves two transport equations:
- `k` (turbulent kinetic energy): `∂k/∂t + ... = P_k - ε`
- `ε` (dissipation rate): `∂ε/∂t + ... = C1*ε/k*P_k - C2*ε²/k`

Then: `μ_t = ρ * C_μ * k² / ε`  (C_μ = 0.09)

**Strengths**: Robust, well-validated for free shear flows (jets, wakes).
**Weaknesses**: Poor for adverse pressure gradients, separation, strong streamline curvature.

### Setup in OpenFOAM

`constant/turbulenceProperties`:
```cpp
simulationType  RAS;

RAS
{
    RASModel    kEpsilon;
    turbulence  on;
    printCoeffs on;
}
```

`0/k`:
```cpp
internalField   uniform 0.375;    // estimated from turbulence intensity
boundaryField
{
    inlet    { type fixedValue; value uniform 0.375; }
    outlet   { type inletOutlet; inletValue uniform 0; value uniform 0; }
    walls    { type kqRWallFunction; value uniform 0; }
}
```

`0/epsilon`:
```cpp
internalField   uniform 14.9;
boundaryField
{
    inlet    { type fixedValue; value uniform 14.9; }
    outlet   { type inletOutlet; inletValue uniform 0; value uniform 0; }
    walls    { type epsilonWallFunction; value uniform 0; }
}
```

---

## k-omega SST Model

Solves:
- `k` (same as k-epsilon)
- `ω` (specific dissipation rate): combines k-epsilon in freestream with k-omega near walls

Then: `μ_t = ρ * a1 * k / max(a1*ω, Ω*F2)`

**Strengths**: Excellent for adverse pressure gradients and mild separation. Gold standard for most external aero and turbomachinery.
**Weaknesses**: Sensitive to freestream ω values; slightly more expensive than k-epsilon.

### Why k-omega SST is Usually Preferred

| Feature | k-epsilon | k-omega SST |
|---------|-----------|-------------|
| Near-wall accuracy | Poor (needs wall functions) | Excellent |
| Separation prediction | Poor | Good |
| Freestream sensitivity | Low | Moderate (fix with ω limiter) |
| Computational cost | Base | +5-10% |
| Recommended for | Free jets, mixing layers | Most wall-bounded flows |

### Setup in OpenFOAM

`constant/turbulenceProperties`:
```cpp
RAS
{
    RASModel    kOmegaSST;
}
```

`0/omega`:
```cpp
internalField   uniform 213;
boundaryField
{
    inlet    { type fixedValue; value uniform 213; }
    outlet   { type inletOutlet; inletValue uniform 0; value uniform 0; }
    walls    { type omegaWallFunction; value uniform 0; }
}
```

---

## y+ — The Critical Mesh Parameter for RANS

y+ measures how far the first cell center is from the wall in wall units:
```
y+ = y * u_τ / ν
u_τ = sqrt(τ_wall / ρ)   (friction velocity)
```

| y+ range | Required treatment |
|----------|-------------------|
| y+ ~ 1 | Low-Re (no wall function, resolve viscous sublayer) |
| y+ 5-30 | Buffer layer — avoid this range! |
| y+ 30-300 | Log-law region — wall functions work here |

### Estimating first cell height for target y+

```
Δy = y+ * ν / u_τ

For pipe flow: u_τ ≈ U * sqrt(f/8)  where f = 0.316 * Re^(-0.25) (Blasius)
```

Use the online "y+ calculator" or:
```bash
# OpenFOAM utility:
yPlus -latestTime
```

---

## Exercise 6A — RANS Setup for Backward-Facing Step

The backward-facing step is a classic test case for turbulence models (flow separates at the step and reattaches downstream).

1. Copy `$FOAM_TUTORIALS/incompressible/simpleFoam/backwardFacingStep2D`
2. Run with k-epsilon (default)
3. Switch to k-omega SST and re-run
4. Compare: where does the flow reattach in each case? (Look for the point where U_x changes sign near the bottom wall)

---

## Key Takeaways

- RANS averages the Navier-Stokes equations and models turbulence via eddy viscosity.
- k-epsilon: good for free shear flows; bad for separation and adverse pressure gradients.
- k-omega SST: blends k-omega (near wall) with k-epsilon (freestream) — best general choice.
- y+ determines whether to use wall functions (y+ 30–300) or resolve the boundary layer (y+ ~1).
- Always compute inlet k, epsilon/omega from turbulence intensity and length scale.
- `constant/turbulenceProperties` sets which model; `0/k`, `0/epsilon` or `0/omega` set BCs.
