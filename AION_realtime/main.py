# Author:  Matteo Lorenzato
# Date: 2023-08-26


import sqlite3
from datetime import datetime
import pytz
import pandas as pd
import threading
import time
import json
import os
import copy
from box import Box
from algorithms.algo1 import algo1

# Define terminal colors for visual cues
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
END_COLOR = '\033[0m'

# Mapping of algorithm names to their classes
ALGO_CLASS_MAP = {
    'algo1': algo1
}

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)

TICKER_DB_PATH = os.path.join(parent_dir, 'CTMP-master', 'db')

class DatabaseTracker:
    def __init__(self, algo_db_path, data_db_path, algo_db_name, data_db_name, n):
        self.algo_db_path = algo_db_path
        self.algo_db_name = algo_db_name
        self.data_db_path = data_db_path
        self.table_name = data_db_name
        self.n = n
        self.last_date = self.get_last_date()

    def get_last_date(self):
        utc_now = datetime.now(pytz.utc)
        return utc_now.strftime('%Y-%m-%d %H:%M:%S') + utc_now.strftime('%z')[:3] + ':' + utc_now.strftime('%z')[3:]

    def get_new_rows(self):
        while True:
            conn = sqlite3.connect(self.data_db_path)
            
            # First, check if there's a new date greater than last_date
            df_check = pd.read_sql_query(f"SELECT * FROM {self.table_name} WHERE date > '{self.last_date}' ORDER BY date ASC LIMIT 1", conn)
            
            if not df_check.empty:
                new_date = df_check['date'].values[0]
                # Then, get the most recent n rows with date less than or equal to the new_date
                df_new = pd.read_sql_query(f"SELECT * FROM (SELECT * FROM {self.table_name} WHERE date <= '{new_date}' ORDER BY date DESC LIMIT {self.n}) ORDER BY date ASC", conn)
                self.last_date = df_new['date'].iloc[-1]  # Get the date of the first row since we are ordering in descending
                if not df_new.empty:
                    print(GREEN+"GET NEW CANDLE"+END_COLOR, flush=True)
                    conn.close()
                    return df_new
                else:
                    conn.close()
                    time.sleep(1)  # Sleep for a while to prevent excessive CPU usage
            else:
                conn.close()
                time.sleep(1)  # Sleep for a while to prevent excessive CPU usage


def run_algo_on_new_row(algo_class, db_tracker, parameters):
    while True:
        # Check if there is a new row
        new_row_df = db_tracker.get_new_rows()  # This will block until new rows are found()  # Implement this function

        if new_row_df is not None:
            #print(new_row_df)
            # Instantiate the algo with the new df
            algo = algo_class(new_row_df, parameters, parameters.parameters)

            # Run the algo
            algo.update_all()

            # Get the updated df
            result_df = algo.to_dataframe()
            last_result = result_df.tail(1)

            # Write result_df to the results database
            # Specify the relative path to the directory where the database file is located
            relative_dir = os.path.join(script_dir, 'db_algo_data')

            db_name = db_tracker.algo_db_name + ".db"

            algo_db_path = os.path.join(relative_dir, db_name)  

            conn_result = sqlite3.connect(algo_db_path)
            #print(algo_db_path)
            last_result.to_sql("Results", conn_result, if_exists='append', index=False)
            conn_result.commit()
            conn_result.close()

        # Sleep for a while to prevent excessive CPU usage
        time.sleep(1)

def check_db_exist(db_name):
    return os.path.exists(db_name)

def create_db(path, db_name):
    db_name_complete = db_name + ".db"
    db_path = os.path.join(path, db_name_complete)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    create_table_sql = '''
        CREATE TABLE IF NOT EXISTS Results (
            id REAL,
            date DATETIME,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            open_pos_perc REAL,
            open_pos_limit_levels TEXT,
            stop_loss_level REAL,
            take_profit_levels TEXT,
            close_for_limit_orders REAL,
            profit_loss REAL,
            open_pos_price REAL,
            NET_PROFIT REAL,
            DRAWDOWN REAL,
            BuyHold_NET_PROFIT REAL,
            BuyHold_DRAWDOWN REAL
        )
    '''
    cursor.execute(create_table_sql)
    conn.close()

    return db_path

def determine_database(parameters):
    db_name = parameters.exchange + "_" + parameters.type + "_" + parameters.asset + "_" + parameters.asset_ref + "_" + parameters.ticker_interval + "_" + parameters.algorithm_name
    path = os.path.join(script_dir, 'db_algo_data')
    if not check_db_exist(db_name):
        db_path = create_db(path, db_name)
    else:
        db_path = path + "/" + db_name + ".db"
    
    return db_name, db_path

def value_keys_only(d):
    if isinstance(d, dict):
        if 'value' in d:
            return d['value']
        else:
            return {k: value_keys_only(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [value_keys_only(i) for i in d]
    else:
        return d
    

parameters = {}
threads = []
root_dir_lst = []
# Directory where the parameter files are stored
for key in ALGO_CLASS_MAP:
    root_dir_lst.append(os.path.join(script_dir, 'params', 'funds', 'assets', key, 'assets'))
    
for root_dir in root_dir_lst:
    # Iterate over all subfolders in the root directory
    for subdir, dirs, files in os.walk(root_dir):
        print(YELLOW+f"Checking in directory: {subdir}"+END_COLOR, flush=True)  # print the directory it's checking

        for file in files:
            # Skip files that are not JSON
            if not file.endswith('.json'):
                continue
            # Skip files .DS_Store for macOS
            if file == '.DS_Store':
                continue
            print(GREEN+f"Found file: {file}"+END_COLOR, flush=True)  # print all files it finds

            # Check if the file is a JSON file
            if file.endswith('.json'):
                # Load algo parameters from json file
                try:
                    with open(os.path.join(subdir, file)) as f:
                        parameters = json.load(f)
                        simplified_data = value_keys_only(parameters)
                        params = Box(simplified_data)
                        #print(params)
                    print(GREEN+"JSON file read successfully"+END_COLOR, flush=True)
                    #print(params.algorithm_name + params.asset)
                except FileNotFoundError:
                    print(RED+"File not found: ", os.path.join(subdir, file)+END_COLOR, flush=True)
                except json.JSONDecodeError:
                    print(RED+"Failed to decode JSON from file: ", os.path.join(subdir, file)+END_COLOR, flush=True)
                except KeyError as e:
                    print(RED+"Missing key in JSON file: "+END_COLOR, e, flush=True)

            algo_db_name, algo_db_path = determine_database(params)
            data_db_name = params.exchange + "_" + params.asset + "_" + params.asset_ref + ".db"
            table_data_db_name = params.exchange + "_" + params.type + "_" + params.asset + "_" + params.asset_ref + "_" + params.ticker_interval
            db_data_path = TICKER_DB_PATH + os.sep + params.exchange + os.sep + params.asset + "_" + params.asset_ref + os.sep + data_db_name
            #print("DIOCANE: "+  db_data_path)
            db_tracker = DatabaseTracker(algo_db_path, db_data_path , algo_db_name, table_data_db_name, 10000)
            # Get algo class from parameters
            algo_class = ALGO_CLASS_MAP[params.algorithm_name]
            # Start a new thread for each algorithm
            t = threading.Thread(target=run_algo_on_new_row, args=(algo_class, db_tracker, params))
            t.start()
            threads.append(t)

# Wait for all threads to finish
for t in threads:
    t.join()
