@echo off
REM Get the directory of the current script
SET DIR=%~dp0

REM Execute the Python scripts in new command prompt windows
start cmd /k python "%DIR%AION_artificial_dbdata_writer\artificial_AIon_db_writer.py"
start cmd /k python "%DIR%log_db_updater_artificial\main.py"
start cmd /k python "%DIR%api_manager_artificial\main.py"
