#!/bin/bash
#!/bin/bash

# Get the directory of the current script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Execute each Python script in a new tmux session
tmux new-session -s CTMP "python3 '$DIR/CTMP-master/main.py'"
tmux new-session -s AION_live "python3 '$DIR/AION_realtime/main.py'"
tmux new-session -s AION_log "python3 '$DIR/log_db_updater/main.py'"
tmux new-session -s AION_server "python3 '$DIR/api_manager/main.py'"
