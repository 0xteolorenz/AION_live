#!/bin/bash

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Execute each Python script in its own tmux session
tmux new-session -s session_AION_db_writer "python3 '$DIR/AION_artificial_dbdata_writer/artificial_AIon_db_writer.py'"
tmux new-session -s session_log_db_updater "python3 '$DIR/log_db_updater_artificial/main.py'"
tmux new-session -s session_api_manager "python3 '$DIR/api_manager_artificial/main.py'"
