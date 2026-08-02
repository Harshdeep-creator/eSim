# eSim 2.5 — Ubuntu 25.04 Compatibility Work

Branch: `ubuntu-25.04-esim-fixes`  
Fork: based on FOSSEE/eSim `installers` branch  
Environment: Ubuntu 25.04 (WSL2)

## Objective

Identify dependency and installer compatibility issues while installing eSim 2.5 on Ubuntu 25.04, fix installer/packaging problems where possible, and document validation.

## Ubuntu version

- Ubuntu 25.04 (Plucky Puffin)
- Tested under WSL2 on Windows 11

## Issues found

1. Missing `library/kicadLibrary.tar.xz` in the Ubuntu installer package
2. Premature installer exit via `exit 0` inside `installKicad()`
3. NGHDL installer did not recognize Ubuntu 25.04
4. Missing `unzip` dependency during NGHDL/archive extraction
5. Deprecated `libcanberra-gtk-module` dependency
6. GHDL configure rejected LLVM 20.1 on Ubuntu 25.04
7. Manual LLVM patch was lost on every fresh GHDL extract
8. Existing NGHDL source directory could block reinstallation
9. GHDL was rebuilt even when already installed
10. Missing Verilator source archive in NGHDL packaging resources
11. Missing `~/Desktop` on WSL during desktop integration (environment)
12. Missing `images/logo.png`
13. Missing `Ubuntu/src` application sources required by the launcher

## Issues fixed (in this branch)

| Area | Fix |
|---|---|
| `install-eSim.sh` | Close missing `fi` in `run_version_script` (syntax/control-flow) |
| `install-eSim-25.04.sh` | Replace `exit 0` with `return 0` in `installKicad()`; install `unzip`; overlay tracked NGHDL scripts after `nghdl.zip` extract |
| `nghdl-scripts/install-nghdl.sh` | Map Ubuntu 25.04 to `install-nghdl-24.04.sh` |
| `nghdl-scripts/install-nghdl-24.04.sh` | Use `libcanberra-gtk3-module`; auto-patch GHDL configure for LLVM 20.1; install `unzip`; skip GHDL rebuild when GHDL is already usable; safer reinstall `rm -rf` before move |
| Packaging | Add `library/kicadLibrary.tar.xz`, `images/logo.png`, and `Ubuntu/src` (GUI sources) |

Environment-only workarounds (documented in the full report, not installer commits): creating `~/Desktop` on WSL; one-time cleanup of leftover NGHDL directories when needed.

## Files modified / added

- `Ubuntu/install-eSim.sh`
- `Ubuntu/install-eSim-scripts/install-eSim-25.04.sh`
- `Ubuntu/nghdl-scripts/install-nghdl.sh`
- `Ubuntu/nghdl-scripts/install-nghdl-24.04.sh`
- `Ubuntu/images/logo.png`
- `Ubuntu/library/kicadLibrary.tar.xz`
- `Ubuntu/src/` (application sources required by `/usr/bin/esim`)
- `Ubuntu/.gitignore`
- `README-Ubuntu-25.04.md`

## Why `nghdl-scripts/` instead of committing `nghdl.zip`

The installer runs `unzip -o nghdl.zip`, which would overwrite scripts committed inside `Ubuntu/nghdl/`.

The cleaner upstream-friendly approach used here:

1. Keep reviewable script fixes under `Ubuntu/nghdl-scripts/`
2. After extracting `nghdl.zip`, copy those scripts over the extracted copies
3. Avoid committing the large `nghdl.zip` / extracted GHDL / Verilator trees

Runtime still requires a local `Ubuntu/nghdl.zip` packaging archive (unchanged expectation of the installer). The zip does not need to be in git for script review.

## Validation

After applying the fixes:

- Installer completes with “eSim Installed Successfully”
- `ghdl`, `verilator`, and `ngspice` are available
- `esim` launches the eSim 2.5 GUI
- Repeated installs skip GHDL rebuild when GHDL is already installed

## How to reproduce

```bash
# On Ubuntu 25.04
git clone https://github.com/Harshdeep-creator/eSim.git
cd eSim
git checkout ubuntu-25.04-esim-fixes
cd Ubuntu

# Place packaging archive expected by the installer (not stored in this branch):
#   nghdl.zip
# Optional PDK archive if testing SKY130 stage:
#   library/sky130_fd_pr.tar.xz

chmod +x install-eSim.sh
./install-eSim.sh --install
esim
```

## Notes for evaluators

- Full chronological investigation with evidence/screenshots is in the submission report (sections 10.1–10.16).
- `library/sky130_fd_pr.tar.xz` is an upstream packaging resource, not part of the Ubuntu 25.04 script defects fixed here, and is intentionally not committed.
