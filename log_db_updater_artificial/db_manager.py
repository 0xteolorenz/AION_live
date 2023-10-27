# Author:  Matteo Lorenzato
# Date: 2023-08-26


import log_objects as lo
import sqlite3
import json
from sqlite3 import Connection, Cursor
import logging

logging.basicConfig(level=logging.INFO)

def add_table(db_path: str, table_name: str, column_names: list):
    '''
    Add a new table to an SQLite database.

    Parameters:
    db_path (str): Path to the SQLite database.
    table_name (str): Name of the new table to be created.
    column_names (list): A list of strings representing column names to be added in the new table.
    '''

    # Connect to the database
    conn = sqlite3.connect(db_path)

    # Create a cursor for the connection
    c = conn.cursor()

    # Create columns with provided names, each column is of type TEXT
    columns = ','.join([f'{name} TEXT' for name in column_names])
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
    c.execute(create_table_query)

    # Commit the changes made to db and close all connections and cursors
    conn.commit()

    c.close()
    conn.close()


def process_log(log_list: list, sql_command: str, db_path: str):
    '''
    Process a list of logs, create API logs from them, and execute SQL commands for each log.

    Parameters:
    log_list : list
        List of logs to be processed.
    sql_command : str
        SQL command to be executed for each log.
    connection : sqlite3.Connection
        SQLite connection to be used for committing the transaction.
    cursor : sqlite3.Cursor
        SQLite cursor to be used for executing SQL commands.
    '''
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for log in log_list:
        if log is None:  # Skip if the log is None
            continue
        cursor.execute(sql_command, (json.dumps(log),))  # Execute the SQL command for the log
        logging.info('Log created on:' + log["exchange"] + log["symbol"] + log["algorithm"] + log["timeframe"])  # Print the log
    conn.commit()  # Commit the transaction
    conn.close()


def create_log(LogClass: object, log_params: dict) -> dict:
    '''
    Create a log using a log class and parameters.

    Parameters:
    LogClass : class
        The log class to be used for creating the log.
    log_params : list
        The parameters to be passed to the log class.

    Returns:
    dict
        A dictionary representation of the created log.
    '''
    log = LogClass(*log_params).to_dict()  # Create a log and convert it to a dictionary
    return log


def process_dict_list(dict_list: list, process_func) -> list:
    '''
    Process a dictionary using a function and return a list of results.

    Parameters:
    dict_list : dict
        The dictionary to be processed.
    process_func : function
        The function to be used for processing the dictionary.

    Returns:
    list
        A list of results from processing the dictionary.
    '''
    log_list = []
    for key, value in dict_list.items():
        log_list.append(process_func(value))  # Process each value in the dictionary and add it to the list
    return log_list


def close_db_connections(conn: Connection, conn_backup: Connection):
    '''
    Commit changes and close SQLite connections to a main database and a backup database.

    Parameters:
    conn : sqlite3.Connection
        SQLite connection to the main database.
    conn_backup : sqlite3.Connection
        SQLite connection to the backup database.
    '''
    conn.commit()  # Commit changes to main database
    conn_backup.commit()  # Commit changes to backup database
    conn.close()  # Close connection to main database
    conn_backup.close()  # Close connection to backup database

def check_open_long(row_list: list) -> bool:
    '''
    Check if opening a long position
    '''
    return row_list[-1]["open_pos_perc"] > 0 and row_list[-2]["open_pos_perc"] <= 0

def check_open_short(row_list: list) -> bool:
    '''
    Check if opening a short position
    '''
    return row_list[-1]["open_pos_perc"] < 0 and row_list[-2]["open_pos_perc"] >= 0

def check_close_long_pos(row_list: list) -> bool:
    '''
    Check if closing a long position
    '''
    return row_list[-1]["open_pos_perc"] == 0 and row_list[-2]["open_pos_perc"] > 0

def check_close_short_pos(row_list: list) -> bool:
    '''
    Check if closing a short position
    '''
    return row_list[-1]["open_pos_perc"] == 0 and row_list[-2]["open_pos_perc"] < 0

def check_stoploss_change(row_list: list) -> bool:
    '''
    Check if stop loss value has changed
    '''
    return (row_list[-1]["stop_loss_level"] is not None and row_list[-1]["stop_loss_level"] != '') and row_list[-1]["stop_loss_level"] != row_list[-2]["stop_loss_level"]

def check_takeprofit_change(row_list: list) -> bool:
    '''
    Check if take profit value has changed
    '''
    return (row_list[-1]["take_profit_levels"] is not None or row_list[-1]["take_profit_levels"] != '') and row_list[-1]["take_profit_levels"] != row_list[-2]["take_profit_levels"]

def check_open_position_change(row_list: list) -> bool:
    '''
    Check if open position value has changed
    '''
    return (row_list[-1]["open_pos_limit_levels"] is not None or row_list[-1]["open_pos_limit_levels"] != '') and row_list[-1]["open_pos_limit_levels"] != row_list[-2]["open_pos_limit_levels"]

def process_row(row_list: list, table_info: dict) -> list:
    '''
    Function to process a row of data and create logs based on the data and its relation to previous rows.

    Parameters:
    row_list : list of dict
        List of rows in the form of dictionaries, ordered by date in ascending order.
    table_info : TableInfo
        Object that stores various details about the table that the rows belong to.

    Returns:
    list
        A list of logs generated by processing the row.
    '''

    # Initialize an empty list to store the logs
    log_list = []

    # The most recent order is the last in the list
    order_info = row_list[-1]

    # Check if a long position should be opened
    if check_open_long(row_list):
        # If so, create a log for closing a short position and opening a long one
        log_list.append(create_log(lo.StrategyClosePositionLog, 
                                        [table_info["exchange"], 
                                        table_info["market"], 
                                        order_info['date'], 
                                        table_info["symbol"], 
                                        table_info["base_currency"], 
                                        'buy', 
                                        'market', 
                                        100, 
                                        order_info['close'], 
                                        True, 
                                        None, 
                                        'filled', 
                                        'closeshort', 
                                        table_info["algorithm_name"], 
                                        table_info["timeframe"]]))
        
        log_list.append(create_log(lo.StrategyOpenPositionLog, 
                                        [table_info["exchange"], 
                                        table_info["market"], 
                                        order_info['date'], 
                                        table_info["symbol"], 
                                        table_info["base_currency"], 
                                        'buy', 
                                        'market', 
                                        abs(order_info['open_pos_perc']), 
                                        order_info['close'], 
                                        False, 
                                        None, 
                                        'filled', 
                                        'openlong', 
                                        table_info["algorithm_name"], 
                                        table_info["timeframe"]]))

# Check if a short position should be opened
    if check_open_short(row_list):
        # If so, create a log for closing a long position and opening a short one
        log_list.append(create_log(lo.StrategyClosePositionLog, 
                                        [table_info["exchange"], 
                                        table_info["market"], 
                                        order_info['date'], 
                                        table_info["symbol"], 
                                        table_info["base_currency"], 
                                        'sell', 
                                        'market', 
                                        100, 
                                        order_info['close'], 
                                        True, 
                                        None, 
                                        'filled', 
                                        'closelong', 
                                        table_info["algorithm_name"], 
                                        table_info["timeframe"]]))
        
        log_list.append(create_log(lo.StrategyOpenPositionLog, 
                                        [table_info["exchange"], 
                                        table_info["market"], 
                                        order_info['date'],
                                        table_info["symbol"], 
                                        table_info["base_currency"], 
                                        'sell', 
                                        'market', 
                                        abs(order_info['open_pos_perc']), 
                                        order_info['close'], 
                                        False, 
                                        None, 
                                        'filled', 
                                        'openshort', 
                                        table_info["algorithm_name"], 
                                        table_info["timeframe"]]))
    
    if check_close_long_pos(row_list):
        #If so, create a log for closing long position
        log_list.append(create_log(lo.StrategyClosePositionLog, 
                                        [table_info["exchange"], 
                                        table_info["market"], 
                                        order_info['date'], 
                                        table_info["symbol"], 
                                        table_info["base_currency"], 
                                        'sell', 
                                        'market', 
                                        100, 
                                        order_info['close'], 
                                        True, 
                                        None, 
                                        'filled', 
                                        'closelong', 
                                        table_info["algorithm_name"], 
                                        table_info["timeframe"]]))    
    if check_close_short_pos(row_list):
        # If so, create a log for closing a short position 
        log_list.append(create_log(lo.StrategyClosePositionLog, 
                                        [table_info["exchange"], 
                                        table_info["market"], 
                                        order_info['date'], 
                                        table_info["symbol"], 
                                        table_info["base_currency"], 
                                        'buy', 
                                        'market', 
                                        100, 
                                        order_info['close'], 
                                        True, 
                                        None, 
                                        'filled', 
                                        'closeshort', 
                                        table_info["algorithm_name"], 
                                        table_info["timeframe"]]))


# Check if the stop loss level has changed
    if check_stoploss_change(row_list):
        # If so, create a log for setting the stop loss
        log_list.append(create_log(lo.StrategyStopLossProfitLog, 
                                        [table_info["exchange"], 
                                        table_info["market"], 
                                        order_info['date'], 
                                        table_info["symbol"], 
                                        table_info["base_currency"], 
                                        'sell' if order_info['open_pos_perc'] > 0 else 'buy', 
                                        'limit', 100, order_info['stop_loss_level'], 
                                        True, 
                                        order_info['stop_loss_level']*(1.0001 if order_info['open_pos_perc'] > 0 else 0.9999),
                                        'unfilled', 
                                        'set stoploss', 
                                        table_info["algorithm_name"], 
                                        table_info["timeframe"]]))

    # Check if the take profit levels have changed
    if check_takeprofit_change(row_list):
        # If so, create logs for each new take profit level
        takeprofit_dict_list = json.loads(order_info['take_profit_levels'])
        log_list.extend(process_dict_list(takeprofit_dict_list, 
                                                lambda value: create_log(lo.StrategyTakeProfitLog, 
                                                                        [table_info["exchange"], 
                                                                        table_info["market"], 
                                                                        order_info['date'], 
                                                                        table_info["symbol"], 
                                                                        table_info["base_currency"], 
                                                                        'sell' if value['type_pos'] == "l" else 'buy', 
                                                                        'limit', 
                                                                        value['percent'], 
                                                                        value['price'], 
                                                                        True, 
                                                                        None, 
                                                                        'unfilled', 
                                                                        'set take profit', 
                                                                        table_info["algorithm_name"], 
                                                                        table_info["timeframe"]]) if (value['type_pos'] == "l" and value['price'] > order_info['open_pos_price']) or (value['type_pos'] == "s" and value['price'] < order_info['open_pos_price']) else do_nothing()))
    
    # Check if the levels at which to open a position have changed
    if check_open_position_change(row_list):
        # If so, create logs for each new open position level:
        open_pos_limit_list = json.loads(order_info['open_pos_limit_levels'])
        log_list.extend(process_dict_list(open_pos_limit_list, 
                                                lambda value: create_log(lo.StrategyOpenPositionLog, 
                                                                        [table_info["exchange"], 
                                                                        table_info["market"], 
                                                                        order_info['date'], 
                                                                        table_info["symbol"], 
                                                                        table_info["base_currency"], 
                                                                        'buy' if value['type_pos'] == "l" else 'sell', 
                                                                        'limit', 
                                                                        value['percent'], 
                                                                        value['price'], 
                                                                        False, 
                                                                        None if value['price'] <= order_info['open_pos_price'] else value['price']*0.999, 
                                                                        'filled', 
                                                                        'openlong limit' if value['type_pos'] == "l" else 'openshort limit', 
                                                                        table_info["algorithm_name"], 
                                                                        table_info["timeframe"]]) if value else do_nothing()))
    # Return the list of logs
    return log_list


def do_nothing():
    pass

def get_dict_table_info(table_name: str) -> dict:
        # Assume table names are formatted like exchange_market_symbol_basecurrency_timeframe_algorithmname
        # Extract information from the table name
        exchange, market, symbol, base_currency, timeframe, algorithm_name = table_name.split('_')
        # Return the table information in the form of a dictionary
        table_info = {
            'name': table_name,
            'exchange': exchange,
            'market': market,
            'symbol': symbol,
            'base_currency': base_currency,
            'timeframe': timeframe,
            'algorithm_name': algorithm_name
        }
        return table_info


def process_table_data(table_mgr):
    table_info = table_mgr.check_new_data()
    if table_info:
        #print("Table info:" + table_info['name'])
        insert_query = f"INSERT INTO {table_info['name']} (logs) VALUES (?)"
        rows = (table_mgr.get_last_rows(2))  # get the last n rows
        #print(rows)
        log_list = process_row(rows, table_info)
        print("___LOGS___", flush=True)
        print(log_list, flush=True)
        process_log(log_list, insert_query, table_mgr.db_backup_path)