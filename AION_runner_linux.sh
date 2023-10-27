#!/bin/bash

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Execute the Python scripts in new terminal windows
gnome-terminal -- python3 "$DIR/CTMP-master/main.py"
gnome-terminal -- python3 "$DIR/AION_realtime/main.py"
gnome-terminal -- python3 "$DIR/log_db_updater/main.py"
gnome-terminal -- python3 "$DIR/api_manager/main.py"
