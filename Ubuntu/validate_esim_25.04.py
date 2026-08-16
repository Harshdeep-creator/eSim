#!/usr/bin/env python3
"""Post-install checks for eSim 2.5 on Ubuntu 25.04.

This script is used after running the Ubuntu installer. It does not install
packages. It reports whether the OS, packaging files, launcher, GUI sources,
and simulation tools expected by eSim are present.

Usage (from the Ubuntu installer directory):
    python3 validate_esim_25.04.py
"""

import os
import shutil
import subprocess
import sys


EXPECTED_UBUNTU = "25.04"


def run_cmd(args):
    try:
        proc = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=20,
        )
        out = (proc.stdout or "").strip()
        return proc.returncode, out
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)


def read_os_release():
    data = {}
    path = "/etc/os-release"
    if not os.path.isfile(path):
        return data
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key] = value.strip().strip('"')
    return data


def check_ubuntu():
    info = read_os_release()
    version = info.get("VERSION_ID", "unknown")
    name = info.get("PRETTY_NAME", "unknown")
    ok = version == EXPECTED_UBUNTU
    detail = "%s (VERSION_ID=%s)" % (name, version)
    if not ok:
        detail += " — expected Ubuntu %s" % EXPECTED_UBUNTU
    return ok, detail


def check_command(name, version_args=None):
    path = shutil.which(name)
    if not path:
        return False, "%s not found in PATH" % name
    if version_args:
        code, out = run_cmd([name] + version_args)
        first = out.splitlines()[0] if out else ""
        if code != 0 and not first:
            return True, path
        return True, "%s (%s)" % (path, first)
    return True, path


def check_file(path, label):
    if os.path.isfile(path):
        return True, path
    return False, "%s missing: %s" % (label, path)


def check_python_syntax(path):
    if not os.path.isfile(path):
        return False, "Application.py not found"
    code, out = run_cmd([sys.executable, "-m", "py_compile", path])
    if code == 0:
        return True, "python3 -m py_compile passed"
    return False, out or "syntax check failed"


def main():
    ubuntu_dir = os.path.dirname(os.path.abspath(__file__))
    application = os.path.join(ubuntu_dir, "src", "frontEnd", "Application.py")
    logo = os.path.join(ubuntu_dir, "images", "logo.png")
    kicad_lib = os.path.join(ubuntu_dir, "library", "kicadLibrary.tar.xz")
    launcher = "/usr/bin/esim"
    config = os.path.join(os.path.expanduser("~"), ".esim", "config.ini")

    checks = []

    def add(name, result):
        ok, detail = result
        checks.append((name, ok, detail))

    add("Ubuntu 25.04", check_ubuntu())
    add("Python 3", (True, sys.version.split()[0]))
    add("KiCad library archive", check_file(kicad_lib, "kicadLibrary.tar.xz"))
    add("Application logo", check_file(logo, "logo.png"))
    add("GUI source Application.py", check_file(application, "Application.py"))
    add("Application.py syntax", check_python_syntax(application))
    add("eSim launcher /usr/bin/esim", check_file(launcher, "esim"))
    add("eSim config ~/.esim/config.ini", check_file(config, "config.ini"))
    add("ghdl", check_command("ghdl", ["--version"]))
    add("verilator", check_command("verilator", ["--version"]))
    add("ngspice", check_command("ngspice", ["-v"]))
    add("llvm-config", check_command("llvm-config", ["--version"]))

    print("eSim 2.5 Ubuntu 25.04 validation")
    print("Working directory: %s" % ubuntu_dir)
    width = max(len(name) for name, _, _ in checks)
    failed = 0
    for name, ok, detail in checks:
        status = "OK" if ok else "FAIL"
        if not ok:
            failed += 1
        print("%s  %-*s  %s" % (status, width, name, detail))

    # Packaging and GUI sources are required even before a full install.
    critical = [
        "Ubuntu 25.04",
        "KiCad library archive",
        "Application logo",
        "GUI source Application.py",
        "Application.py syntax",
    ]
    critical_failed = [name for name, ok, _ in checks if name in critical and not ok]

    if critical_failed:
        print("Critical packaging/GUI checks failed: %s" % ", ".join(critical_failed))
        print("Install-time tools (ghdl/verilator/ngspice/esim) are reported above.")
        return 1

    if failed:
        print(
            "%d check(s) failed. If the installer has not been run yet, "
            "launcher and simulator tools may still be missing." % failed
        )
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
