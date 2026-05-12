# Lesson 3.3 — snappyHexMesh: Meshing Around Complex Geometry

## Concept

For complex 3D geometries (car bodies, turbine blades, pipe fittings), blockMesh becomes impractical. `snappyHexMesh` (SHM) solves this:

1. Start with a coarse background hex mesh (from blockMesh)
2. Refine cells near the geometry surface
3. **Snap** cell faces to the STL surface
4. Optionally add prismatic **boundary layers**

```
Background hex  →  Refined near STL  →  Snapped to surface  →  + Layers
    □□□□□           □□□□□                 □□╱╲□□              □□╱│╲□□
    □□□□□           □□□▪□□         →      □╱  ╲□     →       □╱──│─╲□
    □□□□□           □□□□□                 □□□□□□              □□□│□□□
```

---

## Workflow Overview

```bash
# 1. Place STL file in constant/triSurface/
mkdir -p constant/triSurface
cp myGeometry.stl constant/triSurface/

# 2. Create background mesh (must surround the STL completely)
blockMesh

# 3. Run snappyHexMesh
snappyHexMesh -overwrite   # -overwrite replaces blockMesh mesh

# 4. Check quality
checkMesh
```

---

## The snappyHexMeshDict

Location: `system/snappyHexMeshDict`

### Three Phases

```cpp
// Which phases to run:
castellatedMesh true;   // Phase 1: refine + remove cells inside geometry
snap            true;   // Phase 2: snap to surface
addLayers       true;   // Phase 3: add prismatic layers (for BL)
```

### Phase 1: castellatedMeshControls

```cpp
castellatedMeshControls
{
    maxLocalCells   1000000;   // max cells per processor
    maxGlobalCells  2000000;   // max total cells
    minRefinementCells 0;
    nCellsBetweenLevels 3;     // buffer cells between refinement levels

    features                   // optional: refine along sharp edges
    (
        {
            file "myGeometry.eMesh";
            level 2;
        }
    );

    refinementSurfaces         // refine cells touching the STL
    {
        myGeometry              // must match STL filename (without .stl)
        {
            level (2 3);       // (min max) refinement levels
        }
    }

    refinementRegions          // refine a volume region
    {
        // (optional — useful for wakes, shear layers)
    }

    locationInMesh (0.5 0.5 0.5);  // A point INSIDE the fluid domain
                                    // Cells on the other side are removed
}
```

### Phase 2: snapControls

```cpp
snapControls
{
    nSmoothPatch    3;     // Smoothing iterations for patch
    tolerance       2.0;   // Snap tolerance relative to local cell size
    nSolveIter      30;    // Mesh deformation solver iterations
    nRelaxIter      5;
    nFeatureSnapIter 10;   // Iterations to snap to feature edges
    implicitFeatureSnap false;
    explicitFeatureSnap true;
}
```

### Phase 3: addLayersControls (Boundary Layer)

```cpp
addLayersControls
{
    relativeSizes true;   // sizes relative to local cell size

    layers
    {
        myGeometry_patch    // patch name (from STL region)
        {
            nSurfaceLayers 5;     // number of prism layers
        }
    }

    expansionRatio      1.3;   // each layer is 1.3× the previous
    finalLayerThickness 0.3;   // thickness of outermost layer / cell size
    minThickness        0.1;
    nGrow               0;
    featureAngle        60;
    slipFeatureAngle    30;
    nRelaxIter          3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals      3;
    nSmoothThickness    10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedialAxisAngle  90;
    nBufferCellsNoExtrude 0;
    nLayerIter          50;
}
```

---

## STL Surface Requirements

Your STL geometry must be:
- **Closed** (watertight): no gaps, no holes
- **Oriented**: all face normals pointing outward
- **Manifold**: no T-intersections, no duplicate faces

Check with:
```bash
surfaceCheck constant/triSurface/myGeometry.stl
```

Fix STL issues with `surfaceOrient`, `surfaceClean`, or external tools like MeshLab/Blender.

---

## Feature Edge Extraction

Sharp edges on your geometry need explicit treatment:

```bash
surfaceFeatureExtract   # generates .eMesh files from STL
```

Reads `system/surfaceFeatureExtractDict`:
```cpp
myGeometry.stl
{
    extractionMethod    extractFromSurface;
    includedAngle       150;   // edges sharper than (180-150)=30° are features
    writeObj            yes;
}
```

---

## Parallel snappyHexMesh (for large meshes)

```bash
# Decompose the background mesh first
decomposePar

# Run in parallel (4 cores)
mpirun -np 4 snappyHexMesh -parallel -overwrite

# Reconstruct
reconstructParMesh -constant
```

---

## Exercise 3C — Mesh a Sphere in a Channel

1. Create a simple sphere STL (or download one)
2. Set up a background mesh around it with blockMesh
3. Configure snappyHexMeshDict for 3 refinement levels on the sphere
4. Add 4 boundary layers on the sphere surface
5. Run and check: how many cells? What's the max non-orthogonality?

---

## Key Takeaways

- snappyHexMesh: background hex mesh → refine → snap → add layers.
- Place STL files in `constant/triSurface/`.
- `locationInMesh` tells snappyHexMesh which side of the STL is the fluid.
- Extract feature edges with `surfaceFeatureExtract` before running SHM.
- Boundary layers are critical for turbulent wall-bounded flows.
- Always run `checkMesh` after snappyHexMesh and watch for non-orthogonality.
