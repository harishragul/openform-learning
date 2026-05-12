# Lesson 8.1 — Writing a Custom Solver

## Concept

One of OpenFOAM's greatest strengths is that every solver is just a C++ program using OpenFOAM's library. You can read the source of `simpleFoam.C` (it's ~100 lines) and modify it. This lesson walks you through creating a custom solver by starting from an existing one.

---

## Finding and Reading Solver Source

```bash
# Find simpleFoam source
find $FOAM_SOLVERS -name "simpleFoam.C" | head -5

# Or:
ls $FOAM_SOLVERS/incompressible/simpleFoam/
# simpleFoam.C  Make/

cat $FOAM_SOLVERS/incompressible/simpleFoam/simpleFoam.C
```

### simpleFoam.C — Annotated

```cpp
// Main time loop
while (simple.loop(runTime))
{
    Info<< "Time = " << runTime.timeName() << nl << endl;

    // Pressure-velocity coupling (SIMPLE algorithm)
    while (simple.correctNonOrthogonal())
    {
        // --- Pressure equation
        {
            volScalarField rAU(1.0/UEqn.A());  // inverse diagonal of U matrix
            volVectorField HbyA(constrainHbyA(rAU*UEqn.H(), U, p));

            surfaceScalarField phiHbyA("phiHbyA", fvc::flux(HbyA));
            adjustPhi(phiHbyA, U, p);

            // Pressure equation: ∇·(1/A * ∇p) = ∇·HbyA
            fvScalarMatrix pEqn
            (
                fvm::laplacian(rAU, p) == fvc::div(phiHbyA)
            );

            pEqn.setReference(pRefCell, pRefValue);
            pEqn.solve();

            // Momentum corrector: U = HbyA - rAU * ∇p
            if (simple.finalNonOrthogonalIter())
            {
                phi = phiHbyA - pEqn.flux();
            }
        }
        U = HbyA - rAU*fvc::grad(p);
        U.correctBoundaryConditions();
        fvOptions.correct(U);
    }

    // Turbulence model update
    turbulence->correct();
    runTime.write();
}
```

---

## Creating a Custom Solver (Example: Add a Body Force)

### Step 1: Copy simpleFoam

```bash
mkdir -p $FOAM_RUN/../applications/solvers/mySimpleFoam
cp -r $FOAM_SOLVERS/incompressible/simpleFoam/* \
       $FOAM_RUN/../applications/solvers/mySimpleFoam/
cd $FOAM_RUN/../applications/solvers/mySimpleFoam
mv simpleFoam.C mySimpleFoam.C
```

### Step 2: Rename in Make/files

```bash
cat Make/files
# simpleFoam.C
# EXE = $(FOAM_APPBIN)/simpleFoam

# Change to:
# mySimpleFoam.C
# EXE = $(FOAM_USER_APPBIN)/mySimpleFoam
```

Edit `Make/files`:
```
mySimpleFoam.C
EXE = $(FOAM_USER_APPBIN)/mySimpleFoam
```

### Step 3: Add a body force term

In `UEqn.H` (included in the main loop), find the momentum equation:

```cpp
// Original:
fvVectorMatrix UEqn
(
    fvm::div(phi, U)
  + MRF.DDt(U)
  + turbulence->divDevReff(U)
 ==
    fvOptions(U)
);
```

Add a constant body force `f = (0 -9.81 0)` (gravity):

```cpp
// Modified:
dimensionedVector bodyForce
(
    "bodyForce",
    dimensionSet(0, 1, -2, 0, 0, 0, 0),  // m/s² = acceleration
    vector(0, -9.81, 0)
);

fvVectorMatrix UEqn
(
    fvm::div(phi, U)
  + MRF.DDt(U)
  + turbulence->divDevReff(U)
 ==
    fvOptions(U)
  + bodyForce                  // ← added gravity
);
```

### Step 4: Compile

```bash
wmake
# Creates: $FOAM_USER_APPBIN/mySimpleFoam
```

### Step 5: Run

```cpp
// In system/controlDict:
application mySimpleFoam;
```

```bash
mySimpleFoam
```

---

## Understanding wmake

`wmake` is OpenFOAM's build system:

```
Make/
├── files     ← which .C files to compile, output binary name
└── options   ← include paths and libraries to link
```

`Make/options` for a solver:
```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/TurbulenceModels/turbulenceModels/lnInclude \
    -I$(LIB_SRC)/TurbulenceModels/incompressible/lnInclude \
    -I$(LIB_SRC)/transportModels \
    -I$(LIB_SRC)/transportModels/incompressible/singlePhaseTransportModel

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools \
    -lturbulenceModels \
    -lincompressibleTurbulenceModels \
    -lincompressibleTransportModels \
    -lfvOptions \
    -lsampling
```

---

## Exercise 8A — Source Term Solver

Modify `icoFoam` to add a spatially varying momentum source:

```
f(x,y) = -A * U * exp(-((x-x0)² + (y-y0)²) / σ²)
```

This models a porous medium (like a screen) at location (x0, y0) that decelerates the flow.

Steps:
1. Copy icoFoam to myIcoFoam
2. Add the source term to the UEqn
3. Read A, x0, y0, sigma from a `transportProperties` dictionary
4. Compile and test on the cavity case

---

## Key Takeaways

- Every OpenFOAM solver is a short C++ program — read it to understand what it does.
- Copy an existing solver, rename it, add your physics, compile with `wmake`.
- User solvers compile to `$FOAM_USER_APPBIN` — set in `system/controlDict > application`.
- `fvm::` = implicit discretization (goes into the matrix). `fvc::` = explicit (evaluated immediately).
- OpenFOAM operators map almost directly to the mathematical equations.
- `wmake` handles dependencies — just run it in the solver directory.
