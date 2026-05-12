# Lesson 1.1 — What is CFD and Why OpenFOAM?

## Concept

### What is Computational Fluid Dynamics?

Imagine you want to know how air flows around a car, how heat moves through a CPU cooler, or how blood flows through an artery. You could build a physical prototype and test it in a wind tunnel — but that costs money, takes weeks, and gives you only what sensors can measure. CFD is the alternative: solve the physics numerically inside a computer.

CFD discretizes the laws of fluid motion — the **Navier-Stokes equations** — over a spatial grid and marches them forward in time (or finds the steady state). The result is a complete 3D field of velocity, pressure, temperature, and any other quantity you care about, at every point in the domain.

The three governing equations you'll meet over and over:

1. **Continuity** (mass conservation): fluid doesn't disappear or appear from nowhere.
2. **Momentum** (Newton's 2nd law for fluids): forces cause acceleration.
3. **Energy** (1st law of thermodynamics): heat and work are conserved.

For incompressible flow (most everyday liquids and low-speed gases):
```
∇·U = 0                        (continuity)
∂U/∂t + (U·∇)U = -∇p/ρ + ν∇²U  (momentum)
```
Where `U` is velocity, `p` is pressure, `ρ` is density, `ν` is kinematic viscosity.

### What is OpenFOAM?

OpenFOAM (**Open** **F**ield **O**peration **A**nd **M**anipulation) is a free, open-source CFD toolkit written in C++. First released in 2004 (as FOAM), it is today the most widely used CFD software in research and increasingly in industry.

Key facts:
- **Free**: no license fees, no seat limits.
- **Open-source**: you can read, modify, and extend every solver.
- **Object-oriented C++**: fields, meshes, and solvers are C++ objects — highly extensible.
- **Library-based**: not just one solver, but 100+ solvers for different physics.
- **Finite Volume Method (FVM)**: discretizes equations on polyhedral meshes.

### Two Distributions

There are two actively maintained forks:

| | OpenFOAM Foundation | OpenFOAM ESI (OpenCFD) |
|---|---|---|
| Website | openfoam.org | openfoam.com |
| Latest | v11 (2023) | v2312 (2023) |
| Naming | Numbered (v10, v11) | Date-based (v2212, v2312) |
| Style | More academic | More industrial features |

Both are excellent. Syntax is ~95% compatible. This curriculum uses **ESI v2312** by default but notes differences where they exist.

### OpenFOAM vs. Commercial CFD

| Feature | OpenFOAM | ANSYS Fluent / STAR-CCM+ |
|---------|----------|--------------------------|
| Cost | Free | $20k–$100k+/year |
| GUI | Minimal (mostly terminal) | Full GUI |
| Customization | Full source access | Limited UDFs |
| Learning curve | Steep | Gentler initially |
| Community | Large, academic-heavy | Large, industry-heavy |
| Parallel | Native MPI | Licensed per core |

OpenFOAM's steep learning curve is exactly why this curriculum exists.

---

## OpenFOAM in Practice

### What a Typical Workflow Looks Like

```
1. Define geometry  →  STL file or blockMeshDict
2. Generate mesh    →  blockMesh / snappyHexMesh
3. Set up case      →  boundary conditions, initial conditions, solver settings
4. Run solver       →  simpleFoam, pimpleFoam, etc.
5. Post-process     →  ParaView, functionObjects
```

Every OpenFOAM simulation lives in a **case directory**. A minimal case has exactly this structure:

```
myCase/
├── 0/              ← initial & boundary conditions (time = 0)
│   ├── U           ← velocity field
│   └── p           ← pressure field
├── constant/       ← mesh, physical properties
│   ├── polyMesh/   ← mesh files
│   └── transportProperties
└── system/         ← solver control, numerical schemes
    ├── controlDict
    ├── fvSchemes
    └── fvSolution
```

You'll memorize this structure before Module 01 is over.

---

## Worked Example

Let's look at a real OpenFOAM tutorial case. If OpenFOAM is installed, the tutorials live at:

```bash
# ESI version
$FOAM_TUTORIALS

# Foundation version
$FOAM_TUTORIALS

# Typically resolves to something like:
ls $FOAM_TUTORIALS/incompressible/icoFoam/cavity/
```

You should see:
```
0/  constant/  system/
```

Try:
```bash
cat $FOAM_TUTORIALS/incompressible/icoFoam/cavity/system/controlDict
```

This file controls the simulation: start time, end time, timestep, output frequency. We'll dissect it fully in Lesson 1.4.

---

## Exercise 1A

**Task**: Navigate to an OpenFOAM tutorial and list what's inside.

```bash
# Step 1: Source OpenFOAM (if not already done)
source /usr/lib/openfoam/openfoam2312/etc/bashrc   # ESI — adjust path
# or
source /opt/openfoam11/etc/bashrc                  # Foundation

# Step 2: Go to the cavity tutorial
cd $FOAM_TUTORIALS/incompressible/icoFoam/cavity

# Step 3: List the directory tree
find . -type f | sort
```

**Answer these questions**:
1. How many files are in the `0/` directory?
2. What file controls the end time of the simulation?
3. What file contains the mesh?

Write your answers in the chat and the instructor will review them.

---

## Key Takeaways

- CFD solves the Navier-Stokes equations numerically on a computational mesh.
- OpenFOAM is free, open-source, and uses the Finite Volume Method.
- Every simulation is a case directory with three subdirectories: `0/`, `constant/`, `system/`.
- There are two main OpenFOAM distributions (Foundation and ESI) — both excellent.
- The learning curve is steep, but mastering it opens up unlimited customization.
