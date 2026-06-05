# Lesson 3.5 — checkMesh and Mesh Quality Metrics

## Concept

`checkMesh` is the building inspector for your mesh. Every metric it reports maps to a specific numerical failure mode in the solver. Understanding what each metric means physically lets you diagnose and fix problems before they cause solver divergence.

---

## The Four Key Metrics

### 1. Non-Orthogonality

The FVM assumes the vector connecting two neighbouring cell centres is perpendicular to their shared face. Non-orthogonality measures the angle between this vector and the face normal.

```
IDEAL (0°):                     NON-ORTHOGONAL (40°):

  cell A ●──────────●  cell B     cell A ●
         │   face   │                     \  ← vector skewed from face normal
                                    cell B  ●──────────●
```

When high, the flux across the face is computed in the wrong direction. Fix with `nNonOrthogonalCorrectors` in `fvSolution`.

| Non-ortho | Status | nNonOrthogonalCorrectors |
|-----------|--------|--------------------------|
| 0°        | Perfect (blockMesh) | 0 |
| < 40°     | Good | 1 |
| 40–70°    | Acceptable | 2–3 |
| 70–85°    | Problematic | Fix mesh |
| > 85°     | Severe — likely divergence | Must fix mesh |

### 2. Skewness

The face geometric centre may not coincide with where the cell-centre vector intersects the face. High skewness corrupts the convection term interpolation.

- < 0.85: Good
- 0.85–4: Acceptable
- > 4: Problematic — fix the STL or the mesh

### 3. Aspect Ratio

Ratio of longest to shortest cell edge.

- In boundary layers: high AR (10–1000) is intentional and correct
- In flow interior: > 20 produces large truncation errors

### 4. Minimum Volume / Volume Ratio

Degenerate (near-zero-volume) cells impose tiny timesteps on the whole domain via the CFL condition. Usually caused by bad STL or locationInMesh inside the solid.

---

## Reading checkMesh Output

```
Mesh stats                           ← cell/face/point counts, patch count
Overall number of cells of each type ← hex/polyhedra/tet breakdown
Checking topology...                 ← connectivity sanity checks
Checking patch topology...           ← each patch is singly connected
Checking geometry...                 ← the four metrics
    Mesh non-orthogonality Max: X  average: Y
    Max skewness = Z
    Max aspect ratio = W
Mesh OK.                             ← all checks passed
```

`***` stars before a metric = hard warning. `Mesh OK` will not appear. Fix before running solver.

---

## Three Reference Meshes

| Mesh | Cells | Non-ortho max | Skewness max | AR max | Verdict |
|------|-------|--------------|-------------|--------|---------|
| Cavity (blockMesh uniform) | 400 | 0° | ~0 | 1.0 | Perfect |
| Channel (blockMesh graded) | 8,000 | 0° | ~0 | 9.99 | Perfect (AR from BL grading) |
| Sphere (snappyHexMesh) | 28,292 | 36.1° | 0.53 | 5.55 | Very good for SHM |

blockMesh always gives non-ortho = 0. snappyHexMesh always introduces some — the trade-off for geometric flexibility.

---

## Common Failures and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| High non-orthogonality | SHM cut cells | Increase `nNonOrthogonalCorrectors`; reduce level jumps |
| High skewness | Bad STL quality | Fix STL; reduce snap tolerance |
| Negative volume | locationInMesh inside solid | Move locationInMesh into fluid |
| Very high interior AR | Aggressive grading in bulk | Remove grading away from walls |
| Topology failure | Bad parallel reconstruction | Run `reconstructParMesh` cleanly |

---

## fvSolution Link

```cpp
PISO   // or PIMPLE or SIMPLE
{
    nNonOrthogonalCorrectors 1;   // use 1 for SHM meshes with non-ortho < 40°
                                   // use 2-3 for non-ortho up to 70°
}
```

---

## Key Takeaways

- Non-orthogonality > 70° → increase `nNonOrthogonalCorrectors`; > 85° → rebuild mesh.
- Skewness > 4 corrupts face interpolation — usually signals bad STL geometry.
- High aspect ratio in boundary layers is normal; in the interior it is a problem.
- `***` stars in checkMesh = hard warning; solver may diverge without fixing.
- blockMesh gives zero non-orthogonality; snappyHexMesh always has some — this is normal.
- Always run `checkMesh`. Never skip it.
