#!/bin/bash
# SteamOS_Emu_M3U_Crafter.sh

# Get the directory of the script so it always runs relative to itself
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Run the Python script
python3 "$SCRIPT_DIR/SteamOS_Emu_M3U_Crafter.py"