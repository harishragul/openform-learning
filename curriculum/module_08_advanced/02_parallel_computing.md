# Lesson 8.2 — Parallel Computing with OpenFOAM

## Concept

For large meshes (>5 million cells) or long simulations, running on a single CPU core takes too long. OpenFOAM uses **MPI** (Message Passing Interface) to split the domain across multiple CPU cores — each core handles a subdomain and communicates with neighbors.

```
Single core:               4 cores (decomposed):
┌──────────────────┐       ┌─────┬─────┬─────┬─────┐
│                  │  →    │  0  │  1  │  2  │   3  │
│  Full domain     │       │     │     │     │     │
│                  │       └─────┴─────┴─────┴─────┘
└──────────────────┘
```

---

## Parallel Workflow

```bash
# 1. Set up decomposeParDict
# 2. Decompose
decomposePar

# 3. Check decomposition (optional)
ls processor*/
checkMesh -parallel

# 4. Run in parallel
mpirun -np 4 simpleFoam -parallel 2>&1 | tee log.simpleFoam

# 5. Reconstruct results
reconstructPar
# or reconstruct only latest time:
reconstructPar -latestTime
```

---

## decomposeParDict

Location: `system/decomposeParDict`

```cpp
FoamFile { ... }

numberOfSubdomains  4;         // must match -np N in mpirun

method  scotch;                // recommended: automatic, load-balanced
// alternatives:
// simple   — geometric slicing (fast, less balanced)
// hierarchical — multi-level geometric
// metis    — graph-based (good but requires metis library)

// For 'simple' method:
// simpleCoeffs
// {
//     n   (4 1 1);    // 4 slices in x, 1 in y, 1 in z
//     delta   0.001;
// }
```

### Decomposition Methods Compared

| Method | Load balance | Complex geometry | Speed |
|--------|-------------|-----------------|-------|
| `scotch` | Excellent | Excellent | Moderate |
| `metis` | Excellent | Excellent | Moderate |
| `simple` | Poor | Poor | Fast |
| `hierarchical` | Moderate | Moderate | Fast |

Always use `scotch` or `metis` for production runs.

---

## Running on HPC Clusters (SLURM)

Typical SLURM job script:
```bash
#!/bin/bash
#SBATCH --job-name=openfoam_run
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=32          # 4 nodes × 32 cores = 128 cores
#SBATCH --time=48:00:00
#SBATCH --partition=compute

source /path/to/openfoam/etc/bashrc

cd $SLURM_SUBMIT_DIR

# Decompose (run on single node)
decomposePar -force

# Run solver in parallel
mpirun -np 128 simpleFoam -parallel 2>&1 | tee log.simpleFoam

# Reconstruct
reconstructPar -latestTime
```

Submit: `sbatch job.sh`
Monitor: `squeue -u $USER`

---

## Parallel Mesh Generation

For very large meshes, run snappyHexMesh in parallel too:

```bash
# Decompose background mesh
decomposePar

# Run snappyHexMesh in parallel
mpirun -np 16 snappyHexMesh -parallel -overwrite

# Reconstruct mesh (but keep decomposed for simulation)
reconstructParMesh -constant
```

---

## Scalability and Amdahl's Law

Parallel speedup is not linear due to inter-process communication. Rule of thumb:
- **10,000–100,000 cells per core** is the sweet spot
- Below 10k cells/core: communication overhead dominates
- Above 100k cells/core: not using parallel fully

```bash
# Check cells per processor:
foamDictionary processor*/constant/polyMesh/owner -entry size
# or:
wc -l processor*/constant/polyMesh/owner
```

---

## Parallel Utilities

```bash
# Run checkMesh in parallel:
mpirun -np 4 checkMesh -parallel

# Run postProcess in parallel:
mpirun -np 4 postProcess -func forces -parallel

# Reconstruct specific times only:
reconstructPar -time '0.1:0.5'     # times 0.1 to 0.5

# Reconstruct fields only (not mesh):
reconstructPar -fields '(U p)'
```

---

## Exercise 8B — Parallel Pipe Flow

1. Create a 3D pipe flow case (blockMesh: cylinder extruded in z)
2. Set up decomposeParDict for 4 subdomains using scotch
3. Run `decomposePar` and verify 4 processor directories are created
4. Run `mpirun -np 4 simpleFoam -parallel`
5. Reconstruct and visualize
6. Compare wall-clock time vs. single-core run

---

## Key Takeaways

- OpenFOAM parallelizes with MPI: `decomposePar` → `mpirun -np N solver -parallel` → `reconstructPar`.
- `scotch` decomposition gives best load balance for complex geometries — always prefer it.
- Sweet spot: 10k–100k cells per core.
- On HPC clusters, submit via SLURM/PBS; mount case directory on shared filesystem.
- Most utilities (checkMesh, postProcess, snappyHexMesh) also run in parallel with `-parallel`.
