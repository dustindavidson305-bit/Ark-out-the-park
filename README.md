# Ark Out The Park

**RetroArch for your Raspberry Pi — installed properly, in one go.**
By **Delukz**.

Run it on your Pi and Ark does the rest:

1. **Senses your exact Raspberry Pi model** (from the device tree) and
   checks what it can handle — Pi 5 / 4 / 400 / CM4 get the full set,
   Pi 3 and Zero 2 W get a strong set, Pi 2 gets the basics, and the
   original Zero gets the lightest cores with a fair warning.
2. **Senses your Raspberry Pi OS version** (Bookworm / Trixie fully
   supported, Bullseye supported, Buster flagged as legacy) and your
   CPU architecture (32-bit or 64-bit).
3. **Downloads and installs everything needed** from the official
   Raspberry Pi OS / Debian repositories: RetroArch itself, the asset
   and core-info configuration packages, and the right **libretro
   cores** for your model (Game Boy, NES, SNES, GBA, Genesis, Atari —
   plus PlayStation on Pi 3+ and Nintendo 64 on Pi 4/5), and adds your
   user to the video/input/audio groups RetroArch needs.
4. **Writes a tuned RetroArch config** for your Pi (video driver,
   threaded video, buildbot core-updater URLs for your architecture),
   creates a `~/RetroArk/roms` folder skeleton, and verifies the
   install. Watch the progress bar — there's an easter egg in it.

No games or BIOS files are included — add your own legally-owned
backups to `~/RetroArk/roms`.

## Install

On your Raspberry Pi (with Raspberry Pi OS running):

```sh
bash Setup-Pi.sh
```

…or directly:

```sh
python3 Ark-Out-The-Park-Setup.py
```

The installer senses your Pi model and Pi OS version, shows you the
compatibility verdict, installs the `ark-out-the-park` command, and
offers to install RetroArch right away. Everything after that:

```sh
ark-out-the-park            # menu
ark-out-the-park detect     # model / OS / compatibility report
ark-out-the-park install    # full RetroArch install
ark-out-the-park config     # rewrite the RetroArch config
ark-out-the-park uninstall  # remove Ark's config + ROM folders
ark-out-the-park --dry-run install   # print every step, change nothing
```

## Compatibility at a glance

| Pi model | Tier | Cores |
|----------|------|-------|
| Pi 5, Pi 4, Pi 400, CM4 | A | Everything incl. PS1 + N64 |
| Pi 3 / 3B+ / 3A+, Zero 2 W | B | Everything incl. PS1 |
| Pi 2 | C | 8/16-bit set |
| Pi 1, Zero, Zero W | D | Lightest 8-bit cores, with warnings |
| Anything else | — | Refuses (unless `--force`) |

## Tests

No Pi needed — detection runs off fixtures and installs are dry-run:

```sh
python3 tests/smoke_test.py
```

## Developer

Built by **Delukz** — Ark Out The Park v1.0.0 (2026), MIT-licensed
(see `LICENSE`). RetroArch and the libretro cores are installed from
your OS repositories at install time and remain under their own
licenses.
