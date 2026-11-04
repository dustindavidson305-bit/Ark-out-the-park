#!/usr/bin/env python3
"""
Builds Ark-Out-The-Park-Setup.py — the installer for Ark Out The Park.

The Setup file is a single self-contained Python program with the whole
app (ark_out_the_park.py) embedded as a compressed payload. Run it ON a
Raspberry Pi: it senses the Pi model and the Raspberry Pi OS version,
shows the compatibility verdict, installs the app (command + menu
entry), and offers to run the full RetroArch installation.

Usage:  python3 build_installer.py
"""

import base64
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP_SRC = HERE / "ark_out_the_park.py"
OUT = HERE / "Ark-Out-The-Park-Setup.py"

TEMPLATE = r'''#!/usr/bin/env python3
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

PAYLOAD_B64 = "@@PAYLOAD@@"


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
'''


def main():
    app_bytes = APP_SRC.read_bytes()
    payload = base64.b64encode(zlib.compress(app_bytes, 9)).decode("ascii")
    chunks = [payload[i:i + 76] for i in range(0, len(payload), 76)]
    payload_block = "(\n" + "\n".join(f'    "{c}"' for c in chunks) + "\n)"
    setup_src = TEMPLATE.replace('PAYLOAD_B64 = "@@PAYLOAD@@"',
                                 "PAYLOAD_B64 = " + payload_block)
    compile(setup_src, str(OUT), "exec")  # syntax check before writing
    OUT.write_text(setup_src, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes); "
          f"embedded app is {len(app_bytes):,} bytes.")


if __name__ == "__main__":
    main()
