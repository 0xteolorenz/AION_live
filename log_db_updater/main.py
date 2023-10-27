# Author:  Matteo Lorenzato
# Date: 2023-08-26


import db_manager as dbm
import log_objects as lo
import sqlite3
import threading
import time
import os
import shutil
from datetime import datetime

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)

LOGS_DATABASE = os.path.join(script_dir, 'db_backup.db')
BACKUPS_FOLDER = os.path.join(script_dir, 'Logs_backups')
DB_table_mgr_list = []
file_mod_lst = []

def backup_and_delete_all_tables(db_name, backup_folder):
    # Create a timestamped backup file name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = f"{backup_folder}/{timestamp}_backup.db"

    # Copy the original database to the backup file
    shutil.copy2(db_name, backup_file)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()

    # Filter out the 'last_processed_date' table from the list of tables
    filtered_tables = [table[0] for table in tables if table[0] != 'last_processed_date']

    for table in filtered_tables:
        c.execute(f"DROP TABLE IF EXISTS {table};")

    conn.commit()
    conn.close()

def main():
    # Call the function with the name of your database and the folder where you want to save the backup
    backup_and_delete_all_tables(LOGS_DATABASE, BACKUPS_FOLDER)

    column_names = ['logs',]
    
    root_dir = os.path.join(parent_dir, 'AION_realtime', 'db_algo_data')    
    print("ROOT:"+ root_dir)
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            #print(file)
            # Skip files that are not databse
            if not file.endswith('.db'):
                continue
            # Skip files .DS_Store for macOS
            if file == '.DS_Store':
                continue
            algo_database_path = os.path.join(root_dir, file)
            algo_database_name, _ = os.path.splitext(file)
            print("Database Found:" + algo_database_name, flush=True)
            dbm.add_table(LOGS_DATABASE, algo_database_name, column_names)   # Setup backup database tables according to algo database
            file_mod_lst.append(lo.FileModificationTime(algo_database_path))
            DB_table_mgr_list.append(lo.DBTableManager(algo_database_path, algo_database_name, "Results", LOGS_DATABASE))  

    while(True):
        while True:
            #print("I'm waiting for changes...")
            for file_mod in file_mod_lst:
                if file_mod.has_changed():
                    break
                else:
                    time.sleep(0.1)  # Replace 'n' with the number of seconds you want to wait
                    continue
            break
        # No need to create a new connection for each task, use the one in DBTableManager
        dbm_thread_list = []
        for table_mgr in DB_table_mgr_list:
            dbm_thread_list.append(threading.Thread(target=dbm.process_table_data, args=(table_mgr,)))
        for _ in dbm_thread_list:
            _.daemon = True
        for _ in dbm_thread_list:
            _.start()
        for _ in dbm_thread_list:
            _.join()


if __name__ == "__main__":
    main()

