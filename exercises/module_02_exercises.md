# Module 02 Exercises — First Simulations

## Exercise 2A: Run the Cavity Tutorial

```bash
cp -r $FOAM_TUTORIALS/incompressible/icoFoam/cavity ~/cavity_run
cd ~/cavity_run
blockMesh
checkMesh
icoFoam 2>&1 | tee log.icoFoam
```

**Questions**:
1. Maximum velocity magnitude at t = 0.5 s? (use ParaView or `postProcess -func mag(U) -latestTime`)
2. Where is pressure highest? Where lowest? Why?
3. Total `ExecutionTime` from the log?
4. How many time directories were written?

**Answers**:
1. ______
2. ______
3. ______
4. ______

**Screenshot**: attach velocity field visualization

---

## Exercise 2B: Change Reynolds Number

Modify the case to run at Re = 1000 (instead of Re = 10):

Current: `nu = 0.01` → `Re = U*L/nu = 1*0.1/0.01 = 10`
Target: `Re = 1000` → `nu = U*L/Re = 1*0.1/1000 = 1e-4`

```bash
# Edit constant/transportProperties
# Change: nu 0.01  →  nu 1e-4
```

Also reduce timestep (higher Re = more turbulent, need smaller dt):
```cpp
// In system/controlDict:
deltaT  0.001;   // was 0.005
endTime 2.0;     // was 0.5
```

**Questions**:
1. Does the flow look different? Describe the vortex pattern.
2. Are there secondary vortices in the corners?
3. What are the final residuals? Are they lower or higher than Re=10?

**Answers**:
1. ______
2. ______
3. ______

---

## Exercise 2C: Interpret Log File (Bonus)

From your `log.icoFoam`, find:
- The timestep where Ux residuals first drop below 1e-5
- The maximum Courant number reached during the run
- The average time per timestep (ExecutionTime / number of timesteps)

**Answers**:
- First t where residual < 1e-5: ______
- Max Co: ______
- Avg time/step: ______

---

## Completion Checklist

- [ ] 2A: Ran cavity, answered 4 questions, captured screenshot
- [ ] 2B: Changed Re to 1000, observed flow differences
- [ ] 2C (bonus): Mined log file for performance stats

**Notes**:
```
(questions, confusions, surprises)
```
