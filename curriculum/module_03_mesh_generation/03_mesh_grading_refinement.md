# Lesson 3.3 — Mesh Grading and Refinement

## Concept

Grading is the art of putting cells where the physics demands them. Near walls and sharp gradients, you need many small cells. In the open flow interior, large cells are fine. Getting this balance right controls both accuracy and compute cost.

---

## Why Grading Exists — The Boundary Layer Problem

In any viscous flow past a wall, there's a thin region where velocity changes dramatically — from zero at the wall (no-slip) to the free-stream value. This is the **boundary layer**.

```
Free stream  U = 1 m/s    →→→→→→→→→→→→→→→
                           →→→→→→→→→→→→
                           →→→→→→→→→
                           →→→→
                           →→
Wall         U = 0    ─────────────────────
```

The velocity gradient `dU/dy` is steepest right at the wall. If you use uniform cells and your cell is larger than the region where the gradient lives, you smear it out — your simulation misses the physics entirely.

**Rule**: you need at least 5–10 cells inside the boundary layer. For turbulent flows you need even finer — down to a first cell size of fractions of a millimetre.

---

## The Geometry of Grading — A Geometric Series

When you set `simpleGrading (1 r 1)` in blockMesh, the y-cell sizes form a geometric series:

```
cell 1 height = h
cell 2 height = h × r^(1/N-1)
...
cell N height = h × r
```

Where `r` = grading ratio (last cell / first cell) and `N` = number of cells.

The total height H of the block = sum of all cell heights:

```
H = h × (r^(1/(N-1))^N - 1) / (r^(1/(N-1)) - 1)
```

In practice, you don't solve this by hand — you choose r and N, then blockMesh computes h.

**The key relationship** — r = last cell size / first cell size:

| r | Meaning | Small cells at | Refinement at |
|---|---------|---------------|----------------|
| r = 10 | last is 10× bigger than first | start (first) | **start of block** |
| r = 0.1 | last is 10× smaller than first | end (last) | **end of block** |
| r = 1 | equal sizes | everywhere | uniform |

Memory rule: **r > 1 → refine at start. r < 1 → refine at end.**

For a y-block going bottom (y=0) → top (y=H): r > 1 refines at the bottom wall, r < 1 refines at the top wall.

---

## First Cell Height and y+

For turbulent flows (Module 06 covers this fully), the required first cell height is determined by the **y+** target:

```
y+ = u_τ × y₁ / ν
```

Where:
- `u_τ` = friction velocity (≈ 0.05 × U_∞ as a rough estimate)
- `y₁` = first cell centre height (= first cell height / 2)
- `ν` = kinematic viscosity

For wall-resolved turbulence (no wall functions): **y+ ≈ 1**
For wall functions: **y+ = 30–300**

The first cell height calculation:
```
y₁ = y+ × ν / u_τ
```

This is the target first-cell height you plug into your grading calculation.

**We will do this calculation properly in Module 06.** For now: know that grading ratio and first cell height are chosen based on the flow physics, not arbitrarily.

---

## Calculating Grading Ratio

You have:
- Total block height H = 0.1 m
- Number of cells N = 40
- Target first cell height y₁ = 0.001 m (1 mm)

Find grading ratio r:

```python
# Approximate (for large N):
r ≈ (H / (N × y₁))^(2/(N-1))

# Example:
r ≈ (0.1 / (40 × 0.001))^(2/39) = 2.5^(0.051) ≈ 1.05
```

So `simpleGrading (1 1.05 1)` would give you roughly 1mm first cells at y=0.

For quick estimates, the OpenFOAM `blockMesh` utility accepts `simpleGrading` and computes the actual first/last cell sizes — check them in `checkMesh` output or by using:

```bash
# After running blockMesh, check cell sizes:
postProcess -func writeCellVolumes
```

---

## Mesh Independence Study

Even with a good grading strategy, you must verify that your results don't change when you refine the mesh further. This is called a **mesh independence study** (or grid convergence study):

1. Run with coarse mesh (e.g., 20×20)
2. Run with medium mesh (40×40)
3. Run with fine mesh (80×80)
4. Compare key quantities (max velocity, drag, pressure drop)
5. If results stop changing between medium and fine: the medium mesh is sufficient

```
Coarse → Medium: result changes by 5% → not yet converged
Medium → Fine:   result changes by 0.3% → mesh independent
```

A result is only trustworthy when it's mesh-independent. Publishing results from a single mesh without a convergence study is a common CFD mistake.

---

## checkMesh — Reading Quality After Grading

After running blockMesh with grading, checkMesh reports something like:

```
Mesh non-orthogonality Max: 0 average: 0        ← grading preserves orthogonality
Max skewness = 1.6e-14                           ← still perfect
Max aspect ratio = 9.99                          ← expected with grading

Overall mesh quality OK.
```

High aspect ratio near walls is expected and acceptable. Non-orthogonality remains 0 for structured blockMesh grids regardless of grading — because the cell-centre vectors still point perpendicular to the faces.

---

## Exercise 3C — Mesh Independence Check

Using your channel case from Exercise 3B:

1. Run the channel at three mesh resolutions:
   - Coarse: 100×20×1
   - Medium: 200×40×1 (already done)
   - Fine: 400×80×1

2. For each mesh, report max aspect ratio from `checkMesh`

3. Change the y-grading from 0.2 to 0.05 (stronger wall refinement) on the medium mesh.
   What happens to the max aspect ratio? Why?

4. Conceptual: if you were running a turbulent channel flow at Re=10,000 and needed y+ ≈ 1, would you want a higher or lower grading ratio (r)?

---

## Key Takeaways

- Grading puts cells where the physics needs them: refined near walls, coarse in the interior.
- Cell sizes follow a geometric series; the ratio r = last cell size / first cell size.
- First cell height is set by the y+ target — determined by the flow physics, not chosen arbitrarily.
- High aspect ratio near walls is intentional and normal — it reflects the thin boundary layer.
- Always do a mesh independence study: results must not change significantly when the mesh is refined.
- `checkMesh` confirms grading quality — non-orthogonality stays 0 for structured graded meshes.
