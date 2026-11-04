#!/usr/bin/env python3
"""
Smoke tests for Ark Out The Park — no Raspberry Pi required.

Detection is driven off fixture files (tests/fixtures/) through the
ARK_* environment overrides, and installs run with --dry-run so nothing
on the machine changes.

Run:  python3 tests/smoke_test.py
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
APP = ROOT / "ark_out_the_park.py"
FIX = HERE / "fixtures"

FAILURES = []


def run(args, model, osrel, rpi_issue=True, home=None):
    env = dict(os.environ)
    env["ARK_MODEL_FILE"] = str(FIX / model)
    env["ARK_OS_RELEASE_FILE"] = str(FIX / osrel)
    env["ARK_CPUINFO_FILE"] = str(FIX / "model_none.txt")
    env["ARK_RPI_ISSUE_FILE"] = str(FIX / "rpi_issue.txt") if rpi_issue \
        else str(FIX / "no_such_file.txt")
    if home:
        env["HOME"] = str(home)
    return subprocess.run([sys.executable, str(APP)] + args,
                          capture_output=True, text=True, env=env,
                          timeout=60)


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else
                                                  f" — {detail}"))
    if not cond:
        FAILURES.append(name)


def detect_case(name, model, osrel, want_text, want_rc, rpi_issue=True):
    r = run(["detect"], model, osrel, rpi_issue)
    check(name, r.returncode == want_rc and want_text in r.stdout,
          f"rc={r.returncode} out={r.stdout.strip()[:160]}")


def main():
    detect_case("Pi 5 + Trixie -> tier A", "model_pi5.txt", "os_trixie.txt",
                "Raspberry Pi 5 Model B Rev 1.1 (tier A)", 0)
    detect_case("Pi 4 + Bookworm -> tier A", "model_pi4.txt",
                "os_bookworm.txt", "(tier A)", 0)
    detect_case("Pi 3 + Bullseye -> tier B", "model_pi3.txt",
                "os_bullseye.txt", "(tier B)", 0)
    detect_case("Pi Zero W + Buster -> tier D + legacy warning",
                "model_pizero.txt", "os_buster.txt", "(tier D)", 0)
    r = run(["detect"], "model_pizero.txt", "os_buster.txt")
    check("Buster shows legacy note", "legacy" in r.stdout.lower(),
          r.stdout.strip()[:160])
    detect_case("Not a Pi -> incompatible", "model_none.txt",
                "os_debian.txt", "No Raspberry Pi detected", 2,
                rpi_issue=False)

    with tempfile.TemporaryDirectory() as tmp:
        r = run(["--dry-run", "install"], "model_pi5.txt", "os_trixie.txt",
                home=tmp)
        out = r.stdout
        check("Dry-run install rc=0", r.returncode == 0,
              f"rc={r.returncode} err={r.stderr.strip()[:200]}")
        check("Dry-run plans apt retroarch",
              "apt-get install -y retroarch" in out, out[:200])
        check("Dry-run plans N64 core on tier A",
              "libretro-mupen64plus" in out, "")
        check("Dry-run plans PS1 core on tier A",
              "libretro-pcsx-rearmed" in out, "")
        check("Easter egg rides the progress bar",
              "lick my nuts you saucy pickle fucker" in out, "")
        check("Dry-run writes config (shown)",
              'video_driver = "vulkan"' in out, out[-400:])
    r = run(["--dry-run", "install"], "model_none.txt", "os_debian.txt",
            rpi_issue=False)
    check("Dry-run install refuses a non-Pi",
          r.returncode == 1 and "Not compatible" in r.stdout,
          f"rc={r.returncode}")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURE(S): {', '.join(FAILURES)}")
        return 1
    print("All smoke tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
