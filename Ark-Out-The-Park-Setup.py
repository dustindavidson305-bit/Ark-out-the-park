#!/usr/bin/env python3
# Ark Out The Park - installer (for Raspberry Pi / Raspberry Pi OS).
#
# One file: it senses which Raspberry Pi it is running on and which
# version of Raspberry Pi OS is installed, shows the compatibility
# verdict, installs the Ark app (command + applications-menu entry),
# and offers to run the full RetroArch installation right away.
# The app itself is embedded below as a compressed payload.
#
#   Install:    python3 Ark-Out-The-Park-Setup.py [--yes]
#   Uninstall:  python3 Ark-Out-The-Park-Setup.py --uninstall

import base64
import os
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

APP_NAME = "Ark Out The Park"
APP_VERSION = "1.0.0"
APP_FILE = "ark_out_the_park.py"

PAYLOAD_B64 = (
    "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"
)


def app_source():
    return zlib.decompress(base64.b64decode(PAYLOAD_B64)).decode("utf-8")


def locations():
    home = Path.home()
    base = home / ".local" / "share" / "ark-out-the-park"
    return home, base


def make_executable(path):
    try:
        os.chmod(path, os.stat(path).st_mode | 0o111)
    except OSError:
        pass


def uninstall():
    home, base = locations()
    for p in (home / ".local" / "bin" / "ark-out-the-park",
              home / ".local" / "share" / "applications"
              / "ark-out-the-park.desktop"):
        try:
            p.unlink()
        except OSError:
            pass
    shutil.rmtree(base, ignore_errors=True)
    print(APP_NAME + " app removed from " + str(base))
    print("(Your RetroArch install and ~/RetroArk folders were kept.)")


def main():
    if sys.version_info < (3, 9):
        print("Python 3.9 or newer is required.")
        return 1
    if "--uninstall" in sys.argv:
        uninstall()
        return 0
    home, base = locations()
    print("=" * 64)
    print(APP_NAME + " " + APP_VERSION + " - installer")
    print("Sensing your Raspberry Pi and Raspberry Pi OS version...")
    print("=" * 64)
    (base).mkdir(parents=True, exist_ok=True)
    app = base / APP_FILE
    app.write_text(app_source(), encoding="utf-8")
    make_executable(app)
    bin_dir = home / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    link = bin_dir / "ark-out-the-park"
    try:
        if link.exists() or link.is_symlink():
            link.unlink()
        os.symlink(app, link)
    except OSError:
        link.write_text('#!/bin/sh\nexec python3 "' + str(app) + '" "$@"\n',
                        encoding="utf-8")
        make_executable(link)
    apps_dir = home / ".local" / "share" / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    (apps_dir / "ark-out-the-park.desktop").write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Ark Out The Park\n"
        "Comment=Install RetroArch on your Raspberry Pi\n"
        "Exec=" + str(app) + "\n"
        "Terminal=true\n"
        "Categories=Utility;\n",
        encoding="utf-8")
    try:
        shutil.copyfile(Path(__file__).resolve(),
                        base / "Ark-Out-The-Park-Setup.py")
    except OSError:
        pass
    print()
    print("App installed to " + str(base))
    print("Checking this Pi:")
    print()
    sys.stdout.flush()
    det = subprocess.run([sys.executable, str(app), "detect"])
    print()
    run_now = "--yes" in sys.argv
    if not run_now and sys.stdin.isatty():
        try:
            run_now = input("Install RetroArch now? [Y/n]: ").strip() \
                .lower() in ("", "y", "yes")
        except EOFError:
            run_now = False
    if run_now:
        print()
        return subprocess.run([sys.executable, str(app), "install"]).returncode
    print("When you're ready:  ark-out-the-park install")
    print("Uninstall the app:   python3 Ark-Out-The-Park-Setup.py "
          "--uninstall")
    return 0 if det.returncode in (0, 2) else det.returncode


if __name__ == "__main__":
    sys.exit(main())
