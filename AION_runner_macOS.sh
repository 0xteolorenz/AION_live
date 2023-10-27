#!/bin/bash

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Execute the Python scripts in new terminal windows
osascript -e "tell app \"Terminal\" to do script \"python3 '$DIR/CTMP-master/main.py'\""
osascript -e "tell app \"Terminal\" to do script \"python3 '$DIR/AION_realtime/main.py'\""
osascript -e "tell app \"Terminal\" to do script \"python3 '$DIR/log_db_updater/main.py'\""
osascript -e "tell app \"Terminal\" to do script \"python3 '$DIR/api_manager/main.py'\""
