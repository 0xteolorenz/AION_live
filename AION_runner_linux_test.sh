#!/bin/bash

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Execute the Python scripts in new terminal windows
gnome-terminal -- python3 "$DIR/AION_artificial_dbdata_writer/artificial_AIon_db_writer.py"
gnome-terminal -- python3 "$DIR/log_db_updater_artificial/main.py"
gnome-terminal -- python3 "$DIR/api_manager_artificial/main.py"
