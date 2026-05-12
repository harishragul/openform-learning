# Module 01 Exercises — Foundations

## Exercise 1A: Navigate a Tutorial Case

**Goal**: Get comfortable with the OpenFOAM directory structure.

```bash
source /usr/lib/openfoam/openfoam2312/etc/bashrc   # adjust path
cd $FOAM_TUTORIALS/incompressible/icoFoam/cavity
find . -type f | sort
```

**Questions**:
1. How many files are in `0/`?
2. What file controls end time?
3. Where is the mesh stored?

**Expected answers** (fill in after running):
1. ____
2. ____
3. ____

---

## Exercise 1B: Verify Installation

```bash
foamVersion
echo "Tutorials: $FOAM_TUTORIALS"
ls $FOAM_TUTORIALS/incompressible/ | head -10
```

Paste the output here and confirm all three commands work without error.

**Output**:
```
(paste here)
```

---

## Exercise 1C: Governing Equations — Conceptual

1. A liquid with μ = 0.001 Pa·s, ρ = 1000 kg/m³, U = 1 m/s, D = 0.01 m:
   - Re = ? (show calculation)
   - Laminar or turbulent?

2. Which term in the momentum equation enforces no-slip at walls?

3. If Courant number > 1, what happens?

4. Why can we drop the energy equation for slow incompressible water?

**Your answers**:
1. Re = _______ → ___________
2. _______________________
3. _______________________
4. _______________________

---

## Exercise 1D: Case Anatomy

```bash
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity ~/lesson1_cavity
cd ~/lesson1_cavity
```

For each file, write one sentence:
- `0/U`: ___
- `0/p`: ___
- `constant/transportProperties`: ___
- `system/controlDict`: ___
- `system/fvSchemes`: ___
- `system/fvSolution`: ___

Specific questions:
1. What are the dimensions of `p`? What do they mean physically?
2. `writeInterval 20` — how many timesteps between each output write?
3. How many boundary patches are in `0/U`?

---

## Completion Checklist

- [ ] 1A: Explored tutorial directory
- [ ] 1B: OpenFOAM installed and sourced correctly
- [ ] 1C: Answered all conceptual questions
- [ ] 1D: Dissected all case files

**Notes** (questions, confusions, observations):
```
(your notes here)
```
