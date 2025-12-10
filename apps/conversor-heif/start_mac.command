#!/bin/bash

# Conversor HEIC + PDF a JPG - macOS Double-Click Launcher
# This file can be double-clicked in Finder to start the application

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Open Terminal and run the startup script
osascript -e "
tell application \"Terminal\"
    activate
    do script \"cd '$SCRIPT_DIR' && ./start.sh\"
end tell
"
