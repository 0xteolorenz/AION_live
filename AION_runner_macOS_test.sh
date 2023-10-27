#!/bin/bash

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Execute the Python scripts in new terminal windows
osascript -e "tell app \"Terminal\" to do script \"python3 '$DIR/AION_artificial_dbdata_writer/artificial_AIon_db_writer.py'\""
osascript -e "tell app \"Terminal\" to do script \"python3 '$DIR/log_db_updater_artificial/main.py'\""
osascript -e "tell app \"Terminal\" to do script \"python3 '$DIR/api_manager_artificial/main.py'\""
