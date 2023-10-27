@echo off
REM Get the directory of the current script
SET DIR=%~dp0

REM Execute the Python scripts in new command prompt windows
start cmd /k python "%DIR%CTMP-master\main.py"
start cmd /k python "%DIR%AION_realtime\main.py"
start cmd /k python "%DIR%log_db_updater\main.py"
start cmd /k python "%DIR%api_manager\main.py"
