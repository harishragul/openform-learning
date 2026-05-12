# Lesson 8.3 — OpenFOAM with Python (PyFoam, fluidfoam, Ofpp)

## Concept

Python dramatically improves OpenFOAM productivity:
- **Parameter sweeps**: run 50 cases automatically with different inlet velocities
- **Result parsing**: read OpenFOAM field data without ParaView
- **Optimization**: couple OpenFOAM with scipy/optuna optimizers
- **CI/testing**: automated regression tests for your custom solvers

---

## Python Libraries for OpenFOAM

| Library | What it does | Install |
|---------|-------------|---------|
| `PyFoam` | Run cases, parse logs, manipulate dicts | `pip install PyFoam` |
| `fluidfoam` | Read OpenFOAM binary/ASCII field files | `pip install fluidfoam` |
| `Ofpp` | Lightweight field reader | `pip install Ofpp` |
| `pyvista` | 3D visualization (reads VTK from foamToVTK) | `pip install pyvista` |

---

## PyFoam: Running Cases Programmatically

```python
from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

# Clone tutorial and modify velocity
import shutil
import os

src = os.path.join(os.environ['FOAM_TUTORIALS'],
                   'incompressible/simpleFoam/pitzDaily')

for velocity in [5.0, 10.0, 20.0]:
    case_dir = f'pitzDaily_U{velocity}'
    shutil.copytree(src, case_dir, dirs_exist_ok=True)

    # Modify inlet velocity using PyFoam
    sol = SolutionDirectory(case_dir)
    sol['0']['U']['boundaryField']['inlet']['value'] = \
        f'uniform ({velocity} 0 0)'
    sol['0']['U'].writeFile()

    # Run blockMesh
    mesh_runner = UtilityRunner(
        argv=['blockMesh', '-case', case_dir],
        silent=True
    )
    mesh_runner.start()

    # Run simpleFoam
    solver_runner = BasicRunner(
        argv=['simpleFoam', '-case', case_dir],
        silent=False,
        logname='log.simpleFoam'
    )
    solver_runner.start()

print("All cases complete!")
```

---

## fluidfoam: Reading Field Data

```python
import fluidfoam
import numpy as np
import matplotlib.pyplot as plt

case_dir = 'pitzDaily'

# Read mesh coordinates
x, y, z = fluidfoam.readmesh(case_dir)

# Read a scalar field (pressure at latest time)
p = fluidfoam.readsurfacescalars(case_dir, 'latestTime', 'p')

# Read a vector field (velocity)
Ux, Uy, Uz = fluidfoam.readvector(case_dir, 'latestTime', 'U')

# Plot velocity magnitude in a slice
speed = np.sqrt(Ux**2 + Uy**2)
plt.tricontourf(x, y, speed, levels=50, cmap='viridis')
plt.colorbar(label='|U| (m/s)')
plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.title('Velocity magnitude')
plt.savefig('velocity.png', dpi=150)
plt.show()
```

---

## Ofpp: Lightweight OpenFOAM Reader

```python
import Ofpp

mesh = Ofpp.FoamMesh('myCase')

# Access cell centers
print(mesh.cell_centres)        # numpy array shape (nCells, 3)

# Read a field
U_field = Ofpp.parse_field_all('myCase/0.5/U')
print(U_field['internalField'])  # numpy array shape (nCells, 3)
```

---

## Automated Parameter Study

```python
import subprocess
import numpy as np
import shutil
import os

def run_case(Re):
    """Run cavity case at given Reynolds number."""
    nu = 1e-3 / Re        # kinematic viscosity for Re = U*L/nu, U=1, L=0.1
    case = f'cavity_Re{Re}'
    
    shutil.copytree('cavity_base', case, dirs_exist_ok=True)
    
    # Modify transportProperties
    with open(f'{case}/constant/transportProperties', 'r') as f:
        content = f.read()
    content = content.replace('nu              0.01',
                              f'nu              {nu:.6e}')
    with open(f'{case}/constant/transportProperties', 'w') as f:
        f.write(content)
    
    # Run
    subprocess.run(['blockMesh', '-case', case], check=True, capture_output=True)
    result = subprocess.run(
        ['icoFoam', '-case', case],
        capture_output=True, text=True
    )
    
    # Extract max velocity from last timestep
    import Ofpp
    U = Ofpp.parse_field_all(f'{case}/0.5/U')
    Umag = np.linalg.norm(U['internalField'], axis=1)
    return Umag.max()

reynolds_numbers = [10, 100, 400, 1000]
for Re in reynolds_numbers:
    Umax = run_case(Re)
    print(f'Re = {Re:5d}  Umax = {Umax:.4f} m/s')
```

---

## Exercise 8C — Automated Study

Write a Python script that:
1. Runs the pitzDaily simpleFoam tutorial for 5 different inlet velocities: 1, 5, 10, 20, 50 m/s
2. Extracts the drag force from each run's `postProcessing/forces1/0/force.dat`
3. Plots Cd vs. Re on a log-log scale
4. Fits a power law `Cd = a * Re^b` to the data

---

## Key Takeaways

- Python + OpenFOAM = powerful automation: parameter sweeps, optimization, CI/CD.
- PyFoam: manipulates case files, runs solvers, parses logs.
- fluidfoam / Ofpp: read OpenFOAM field data directly into NumPy arrays.
- Use `subprocess.run()` for simple case execution; PyFoam for complex workflows.
- pyvista + foamToVTK enables full 3D visualization in Python (no ParaView needed).
