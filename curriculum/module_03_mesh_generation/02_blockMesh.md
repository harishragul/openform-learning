# Lesson 3.2 — blockMesh: Structured Grids from Scratch

## Concept

`blockMesh` generates structured hexahedral meshes from a text dictionary. It's the most reliable meshing tool in OpenFOAM and produces the highest-quality meshes. For any geometry that can be described with hexahedral blocks, use blockMesh.

The idea: you describe the geometry as one or more **hexahedral blocks**, each defined by 8 vertices. blockMesh connects them into a conformal mesh.

---

## The blockMeshDict File

Location: `system/blockMeshDict`

### Minimal 2D Channel Example

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// Scale factor — all coordinates multiplied by this
scale   1;

// Step 1: Define all vertices (x y z)
vertices
(
    (0  0  0)   // vertex 0
    (1  0  0)   // vertex 1
    (1  0.1  0) // vertex 2
    (0  0.1  0) // vertex 3
    (0  0  0.01)// vertex 4  ← z-direction: thin slab for 2D
    (1  0  0.01)// vertex 5
    (1  0.1  0.01)// vertex 6
    (0  0.1  0.01)// vertex 7
);

// Step 2: Define blocks
// hex (v0 v1 v2 v3 v4 v5 v6 v7) (nx ny nz) grading
blocks
(
    hex (0 1 2 3 4 5 6 7)
    (100 20 1)              // 100 cells in x, 20 in y, 1 in z (2D)
    simpleGrading (1 1 1)   // uniform spacing
);

// Step 3: Define boundary patches
boundary
(
    inlet
    {
        type patch;
        faces ((0 4 7 3));   // left face: vertices 0,4,7,3
    }
    outlet
    {
        type patch;
        faces ((1 2 6 5));   // right face
    }
    top
    {
        type wall;
        faces ((3 7 6 2));
    }
    bottom
    {
        type wall;
        faces ((0 1 5 4));
    }
    frontAndBack
    {
        type empty;          // 2D: tells OpenFOAM to ignore z-direction
        faces
        (
            (0 3 2 1)        // front (z=0)
            (4 5 6 7)        // back  (z=0.01)
        );
    }
);
```

### Vertex Ordering is Critical

Vertices in a hex block must follow this **right-hand rule** convention:

```
    3─────────2        7─────────6
    │  back   │        │  front  │
    │  face   │        │  face   │
    0─────────1        4─────────5
    (z=0)              (z=thickness)
```

The 8 vertices are listed as: bottom-front CCW (0,1,2,3), then top-front CCW (4,5,6,7).

---

## Mesh Grading

Grading concentrates cells near walls or regions of interest.

### simpleGrading

```cpp
simpleGrading (xGrading yGrading zGrading)
```

`yGrading = 4` means: last cell is 4× larger than first cell.
`yGrading = 0.25` means: last cell is 0.25× first cell (refined at end).

For boundary layer refinement at bottom wall:
```cpp
simpleGrading (1 0.1 1)   // y: cells get smaller toward bottom (y=0)
```

### edgeGrading (more control)

```cpp
// For fine control of each edge:
edges
(
    // No curved edges, just straight lines (default)
);
```

For a curved top boundary:
```cpp
edges
(
    arc 1 2 (0.5 0.12 0)   // arc from vertex 1 to 2 passing through midpoint
);
```

---

## Multi-Block Meshes

For L-shaped domains, stepped channels, or any non-rectangular geometry, use multiple blocks:

```
Block 0 │ Block 1
────────┼────────
        │ Block 2
        └────────
```

```cpp
blocks
(
    hex (0 1 2 3 4 5 6 7)   (50 20 1)  simpleGrading (1 1 1)  // Block 0
    hex (1 8 9 2 5 10 11 6) (50 20 1)  simpleGrading (1 1 1)  // Block 1
    ...
);
```

Shared vertices and faces between blocks are automatically merged — this is how conformal multi-block meshes work.

---

## 2D Simulations

OpenFOAM is inherently 3D. For 2D:
- Make the mesh one cell thick in z
- Set the front/back patches to type `empty`

```cpp
frontAndBack
{
    type empty;   // This is the magic word for 2D
    faces (...);
}
```

For **axisymmetric** cases (wedge geometry):
```cpp
wedge_front
{
    type wedge;
    faces (...);
}
```

---

## Running blockMesh

```bash
# From case directory:
blockMesh

# If blockMeshDict is in a non-default location:
blockMesh -dict system/myBlockMeshDict

# Always check the mesh afterward:
checkMesh
```

---

## Exercise 3B — Build a Channel Mesh

Create a new case directory and write a `blockMeshDict` for:
- A rectangular channel: 2 m long × 0.1 m tall × 0.01 m deep (2D)
- 200 cells in x, 40 cells in y
- Grade y so cells are 5× finer at the walls (grading = 0.1 at bottom, 10 at top)
- Patches: `inlet` (left), `outlet` (right), `topWall` (top), `bottomWall` (bottom), `frontBack` (empty)

Then run `blockMesh` and `checkMesh`. Report: max non-orthogonality, max aspect ratio.

---

## Key Takeaways

- `blockMesh` generates structured hexahedral meshes from `system/blockMeshDict`.
- Vertices → blocks → patches is the workflow.
- Vertex ordering follows the right-hand rule (CCW when viewed from outside).
- Grading concentrates cells near walls — essential for boundary layer resolution.
- 2D simulations use `type empty` for front/back patches.
- Always run `checkMesh` after `blockMesh`.
