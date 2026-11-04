#!/bin/sh
# Ark Out The Park - Raspberry Pi starter.
# Makes sure Python 3 exists, then hands over to the installer
# (Ark-Out-The-Park-Setup.py), which senses your Pi model and your
# Raspberry Pi OS version and takes it from there.
DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found - trying to install it ..."
  sudo apt-get update && sudo apt-get install -y python3
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install it with: sudo apt-get install python3"
  exit 1
fi

python3 "$DIR/Ark-Out-The-Park-Setup.py" "$@"
