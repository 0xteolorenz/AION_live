# Author:  Matteo Lorenzato
# Date: 2023-08-26

import sqlite3
import json
import time
import ccxt
import os
import threading

# Global variables
current_open_pos_perc = {'ETH/USDT': 100, 'BTC/USDT': 100}
DATABASE_NAMES = ['ByBit_futureperp_BTC_USDT_1m_FLAS', 'ByBit_futureperp_ETH_USDT_1m_FLAS']
path_to_dbs = os.path.join('AION_artificial_dbdata_writer','databases')#'AION_artificial_dbdata_writer',

exchange = getattr(ccxt, 'bybit')()
exchange.timeout = 15000

def create_db(path, db_name):
    db_name_complete = db_name + ".db"
    db_path = os.path.join(path, db_name_complete)
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        create_table_sql = '''
            CREATE TABLE IF NOT EXISTS Results (
                id INTEGER PRIMARY KEY,
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
        conn.commit()
        conn.close()

    return db_path

def extract_symbol_from_db_name(db_name: str) -> str:
    parts = db_name.split("_")
    base_currency = parts[2]
    quote_currency = parts[3]
    return f"{base_currency}/{quote_currency}"

def insert_data_to_db(db_path: str, data: tuple):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

def clear_all_dbs(path: str):
    for filename in os.listdir(path):
        if filename.endswith(".db"):
            db_path = os.path.join(path, filename)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Results")
            conn.commit()
            conn.close()

def get_latest_price(exchange_name, symbol):
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']

def calculate_take_profits(open_price, type_pos):
    take_profits = {}
    percentages = [20, 50, 70]
    direction = 1 if type_pos == "l" else -1
    for i, percent in enumerate(percentages):
        take_profits[str(i)] = {
            "type_pos": type_pos,
            "price": round(open_price * (1 + direction * (percent/100)), 5),
            "percent": percent
        }
    return take_profits

def insert_data_periodically():
    global current_open_pos_perc

    while True:
        for db_name in DATABASE_NAMES:
            symbol = extract_symbol_from_db_name(db_name)
            OpenPosPerc = current_open_pos_perc.get(symbol, 100)
            opp = 0
            market = 'cc'
            if market == 'market':
                opp = 0
            else:
                opp = -100
            # Alternate the OpenPosPerc value for the next iteration
            current_open_pos_perc[symbol] = opp if OpenPosPerc == 100 else 100

            openpos_price = get_latest_price('bybit', symbol)
            type_pos = "l" if OpenPosPerc == 100 else "s"
            FibLevelTP = json.dumps(calculate_take_profits(openpos_price, type_pos))
            StopLossLevel = round(openpos_price * (1 + (1 if OpenPosPerc < 0 else -1) * 0.10), 5)
            OpenPosLimitlevels = json.dumps({i: {"type_pos": "l", "price": 100, "percent": 50} for i in range(2)})
            close = openpos_price
            date = int(time.time())
            row = (None, date, None, None, None, close, None, OpenPosPerc, OpenPosLimitlevels, StopLossLevel, FibLevelTP, None, None, close, None, None, None, None)
            db_path = os.path.join(path_to_dbs, db_name + ".db")
            insert_data_to_db(db_path, row)
            print(row)

        time.sleep(60)  # Insert a new row every minute


def main():
    # Ensure the directory exists
    if not os.path.exists(path_to_dbs):
        os.makedirs(path_to_dbs)

    # Create databases and clear old data
    for db_name in DATABASE_NAMES:
        create_db(path_to_dbs, db_name)
    clear_all_dbs(path_to_dbs)

    # Use a separate thread to periodically insert data
    insertion_thread = threading.Thread(target=insert_data_periodically)
    insertion_thread.start()

    # This will keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping data insertion.")

'''market_selected = input("Select the type of market you want to simulate (future or market): ")
market = str(market_selected)'''

if __name__ == "__main__":
    main()
