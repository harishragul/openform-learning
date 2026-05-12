# Lesson 1.2 — Installing and Verifying OpenFOAM

## Concept

OpenFOAM is a Linux-native tool. On macOS it runs well inside Docker or a Linux VM. On Windows, WSL2 (Windows Subsystem for Linux) is the recommended path.

### Choose your distribution

**ESI OpenFOAM (openfoam.com)** — recommended for most learners:
```bash
# Ubuntu/Debian (packages)
curl https://dl.openfoam.com/add-apt-repository.sh | sudo bash
sudo apt-get install openfoam2312-default

# Source it
source /usr/lib/openfoam/openfoam2312/etc/bashrc
```

**Foundation OpenFOAM (openfoam.org)**:
```bash
# Ubuntu
sudo sh -c "wget -O - https://dl.openfoam.org/gpg.key | apt-key add -"
sudo add-apt-repository http://dl.openfoam.org/ubuntu
sudo apt-get update
sudo apt-get install openfoam11

source /opt/openfoam11/etc/bashrc
```

**macOS via Docker** (easiest, no VM needed):
```bash
# Pull official image
docker pull opencfd/openfoam-dev:2312
# Run with current directory mounted
docker run -it --rm -v $(pwd):/workdir opencfd/openfoam-dev:2312
```

---

## Verifying Your Installation

After sourcing OpenFOAM, run these checks:

```bash
# Check version
foamVersion
# Expected: OpenFOAM-v2312  (or similar)

# Check solvers are accessible
which simpleFoam
# Expected: /usr/lib/openfoam/openfoam2312/platforms/.../simpleFoam

# Check environment variables are set
echo $FOAM_TUTORIALS
echo $WM_PROJECT_DIR

# Run a quick test — should print usage info
blockMesh -help
```

### Add to ~/.bashrc (so you don't re-source every session)

```bash
echo "source /usr/lib/openfoam/openfoam2312/etc/bashrc" >> ~/.bashrc
```

---

## Key Environment Variables

| Variable | What it points to |
|----------|-------------------|
| `$WM_PROJECT_DIR` | OpenFOAM installation root |
| `$FOAM_TUTORIALS` | Tutorial cases |
| `$FOAM_SRC` | C++ source code |
| `$FOAM_SOLVERS` | Solver executables |
| `$FOAM_UTILITIES` | Utility executables |

---

## Exercise 1B

Run the following and paste the output:

```bash
foamVersion
echo "Tutorials: $FOAM_TUTORIALS"
ls $FOAM_TUTORIALS/incompressible/ | head -10
```

If you get errors, share the exact error message and we'll debug together.

---

## Key Takeaways

- OpenFOAM is Linux-native; use Docker or WSL2 on macOS/Windows.
- Always `source` the OpenFOAM `bashrc` before working — add it to `~/.bashrc`.
- Check the install with `foamVersion` and `which simpleFoam`.
- `$FOAM_TUTORIALS` is your best learning resource — hundreds of worked examples.
