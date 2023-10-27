# Author:  Matteo Lorenzato
# Date: 2023-08-26


from abc import ABC, abstractmethod
import sqlite3
import db_manager as dbm
import os
import logging

logging.basicConfig(level=logging.INFO)

# Columns to select from database algo data
OPEN_POSITION_PERC = "open_pos_perc"
TAKE_PROFIT_TARGETS_PRICE = "take_profit_levels"
STOP_LOSS_TARGET_PRICE = "stop_loss_level"
PRICE_OPEN_POSITION = "open_pos_price"
LIMIT_OPEN_POSITION_TARGETS_PRICE = "open_pos_limit_levels"
CANDLE_CLOSE_PRICE = "close"
DATE = "date"


class ExchangeNotSupportedError(Exception):
    '''
    Exchange not supported error
    '''
    pass


class StrategyLog(ABC):
    """
    The base abstract class to be inherited by log classes of various types like open position, 
    close position, take profit, stop loss, funding fee, maker trading fee and taker trading fee logs.
    
    Methods
    -------
        __init__(self, exchange, market_type, symbol, price, qty_perc, state, comment)
            Initializes an instance with the given parameters
        
        get_symbol(self, asset, asset_ref, market_type)
            Method to create unified symbol parameter base of type of market
            
        to_dict(self)
            Abstract method which is implemented by all the inherited subclasses
        
    Attributes
    ----------
        strategy_id:
            a unique id auto-generated using the uuid library for each instance of StrategyLog
    
        exchange:
            the type of the exchange used by the strategy
            
        market_type:
            the market type whether spot market or futures market..
            
        symbol:
            the crypto currency pair selected e.g. BTC/USD
            
        price:
            The Price where the Order executes. 
        
        quantity_percentage:
            Percentage of position to use to open/close.

        note:
            An optional parameter that can be added to add any additional details.
    """

    def __init__(self, exchange, date, market_type, asset, asset_ref, price, qty_perc, state, comment, algorithm, timeframe):
        self.date = date                                                # Date of log
        self.exchange = exchange                                        # Type of exchange Used
        self.market_type = market_type                                  # Type of Market
        self.symbol = self.get_symbol(asset, asset_ref, market_type)    # Symbol Used (Symbol Pair)
        self.price = price                                              # The price at which order is executed
        self.qty_perc = qty_perc                                        # Quantity percentage
        self.state = state                                              # State - Executed, Partially-Executed, Cancelled or Pending
        self.comment = comment                                          # Additional Comments
        self.algorithm = algorithm                                      # Algorithm type name
        self.timeframe = timeframe                                      # Algorithm timeframe

    def get_symbol(self, asset, asset_ref, market_type):
        if market_type == 'spot':
            return str(asset + "/" + asset_ref)
        elif market_type == 'futureperp':
            return str(asset + "/" + asset_ref + ":" + asset_ref)
        elif  market_type == 'inverseperp':
            return str(asset + "/" + asset_ref + ":" + asset)
        else:
            return {"message": "Market type non supported or wrong."}

    @abstractmethod
    def to_dict(self):
        pass  # This is an abstract function which is implemented in the subclasses


class StrategyOpenPositionLog(StrategyLog):

    def __init__(self, exchange: str, market_type: str, date: str, asset: str, asset_ref: str, side: str, order_type: str, qty_perc: float, price: float, reduce_only: bool, stop_price: float, state: str, comment: str, algorithm : str, timeframe: str):
        super().__init__(exchange, date, market_type, asset, asset_ref, price, qty_perc, state, comment, algorithm, timeframe)
        self.side = side
        self.order_type = order_type
        self.reduce_only = reduce_only
        self.stop_price = stop_price

    def to_dict(self):
        strategy_dict = {
            "date": self.date,
            "exchange": self.exchange,
            "market_type": self.market_type,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "qty_perc": self.qty_perc,  # assuming qty_perc and not qty needs to be added
            "price": self.price,
            "reduceOnly": self.reduce_only,
            'stopPrice': self.stop_price,
            "state": self.state,
            "comment": self.comment,
            "algorithm": self.algorithm,
            "timeframe": self.timeframe
        }
        return strategy_dict



class StrategyClosePositionLog(StrategyLog):

    def __init__(self, exchange: str, market_type: str, date: str, asset: str, asset_ref: str, side: str, order_type: str, qty_perc: float, price: float, reduce_only: bool, stop_price: float, state: str, comment: str, algorithm : str, timeframe: str):
        super().__init__(exchange, date, market_type, asset, asset_ref, price, qty_perc, state, comment, algorithm, timeframe)
        self.side = side
        self.order_type = order_type
        self.reduce_only = reduce_only
        self.stop_price = stop_price


    def to_dict(self):
        strategy_dict = {
            "date": self.date,
            "exchange": self.exchange,
            "market_type": self.market_type,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "qty_perc": self.qty_perc,  # assuming qty_perc and not qty needs to be added
            "price": self.price,
            "reduceOnly": self.reduce_only,
            'stopPrice': self.stop_price,
            "state": self.state,
            "comment": self.comment,
            "algorithm": self.algorithm,
            "timeframe": self.timeframe
        }
        return strategy_dict

class StrategyTakeProfitLog(StrategyLog):

    def __init__(self, exchange: str, market_type: str, date: str, asset: str, asset_ref: str, side: str, order_type: str, qty_perc: float, price: float, reduce_only: bool, stop_price: float, state: str, comment: str, algorithm : str, timeframe: str):
        super().__init__(exchange, date, market_type, asset, asset_ref, price, qty_perc, state, comment, algorithm, timeframe)
        self.side = side
        self.order_type = order_type
        self.reduce_only = reduce_only
        self.stop_price = stop_price


    def to_dict(self):
        strategy_dict = {
            "date": self.date,
            "exchange": self.exchange,
            "market_type": self.market_type,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "qty_perc": self.qty_perc,  # assuming qty_perc and not qty needs to be added
            "price": self.price,
            "reduceOnly": self.reduce_only,
            'stopPrice': self.stop_price,
            "state": self.state,
            "comment": self.comment,
            "algorithm": self.algorithm,
            "timeframe": self.timeframe
        }
        return strategy_dict

class StrategyStopLossProfitLog(StrategyLog):

    def __init__(self, exchange: str, market_type: str, date: str, asset: str, asset_ref: str, side: str, order_type: str, qty_perc: float, price: float, reduce_only: bool, stop_price: float, state: str, comment: str, algorithm : str, timeframe: str):
        super().__init__(exchange, date, market_type, asset, asset_ref, price, qty_perc, state, comment, algorithm, timeframe)
        self.side = side
        self.order_type = order_type
        self.reduce_only = reduce_only
        self.stop_price = stop_price


    def to_dict(self):
        strategy_dict = {
            "date": self.date,
            "exchange": self.exchange,
            "market_type": self.market_type,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "qty_perc": self.qty_perc,  # assuming qty_perc and not qty needs to be added
            "price": self.price,
            "reduceOnly": self.reduce_only,
            'stopPrice': self.stop_price,
            "state": self.state,
            "comment": self.comment,
            "algorithm": self.algorithm,
            "timeframe": self.timeframe
        }
        return strategy_dict


class StrategyFundingFeeLog(StrategyLog):

    def __init__(self, exchange: str, market_type: str, date: str, asset: str, asset_ref: str, qty_perc: float, price: float, state: str, comment: str, algorithm : str, timeframe: str):
        super().__init__(exchange, date, market_type, asset, asset_ref, price, qty_perc, state, comment, algorithm, timeframe)
    
    def to_dict(self):
        strategy_dict = {
            'type': 'Funding Fee',
            "date": self.date,
            "exchange": self.exchange,
            'market type': self.market_type,
            "symbol": self.symbol,
            'quantity percent': self.qty_perc,
            'price': self.price,
            'state': self.state,
            'comment': self.comment,
            "algorithm": self.algorithm,
            "timeframe": self.timeframe
        }
        return strategy_dict


class StrategyMakerTradingFeeLog(StrategyLog):

    def __init__(self, exchange: str, market_type: str, date: str, asset: str, asset_ref: str, qty_perc: float, price: float, state: str, comment: str, algorithm : str, timeframe: str):
        super().__init__(exchange, date, market_type, asset, asset_ref, price, qty_perc, state, comment, algorithm, timeframe)
    
    def to_dict(self):
        strategy_dict = {
            'type': 'Maker Trading Fee',
            "date": self.date,
            "exchange": self.exchange,
            'market type': self.market_type,
            "symbol": self.symbol,
            'quantity percent': self.qty_perc,
            'price': self.price,
            'state': self.state,
            'comment': self.comment,
            "algorithm": self.algorithm,
            "timeframe": self.timeframe
        }
        return strategy_dict


class StrategyTakerTradingFeeLog(StrategyLog):

    def __init__(self, exchange: str, market_type: str, date: str, asset: str, asset_ref: str, qty_perc: float, price: float, state: str, comment: str, algorithm : str, timeframe: str):
        super().__init__(exchange, date, market_type, asset, asset_ref, price, qty_perc, state, comment, algorithm, timeframe)
    
    def to_dict(self):
        strategy_dict = {
            'type': 'Taker Trading Fee',
            "date": self.date,
            "exchange": self.exchange,
            'market type': self.market_type,
            "symbol": self.symbol,
            'quantity percent': self.qty_perc,
            'price': self.price,
            'state': self.state,
            'comment': self.comment,
            "algorithm": self.algorithm,
            "timeframe": self.timeframe
        }
        return strategy_dict


class FileModificationTime:
    def __init__(self, file_path):
        self.file_path = file_path
        self.last_modified = self.get_last_modified()

    def get_last_modified(self):
        # Get the time of the last modification of the file
        t = os.path.getmtime(self.file_path)
        return t

    def has_changed(self):
        current_modified = self.get_last_modified()
        if current_modified != self.last_modified:
            self.last_modified = current_modified
            return True
        return False


class DBTableManager:
    def __init__(self, db_algo_path: str, db_algo_name: str, table_name : str, backup_db_path : str):
        self.db_path = db_algo_path
        self.db_algo_name = db_algo_name
        self.db_backup_path = backup_db_path
        # Table name
        self.table_name = "Results"
        # Define the columns to be selected from the database
        self.columns = [
                        OPEN_POSITION_PERC, 
                        TAKE_PROFIT_TARGETS_PRICE, 
                        STOP_LOSS_TARGET_PRICE, 
                        PRICE_OPEN_POSITION, 
                        LIMIT_OPEN_POSITION_TARGETS_PRICE, 
                        CANDLE_CLOSE_PRICE, 
                        DATE
                        ]
        # Save row count
        self.row_count = 0
        self.table_info = dbm.get_dict_table_info(self.db_algo_name)

    def get_current_row_count(self, cursor) -> list:
        # Execute a SQL command to count the number of rows in the provided table
        cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        # Fetch the count and return it
        return cursor.fetchone()[0]
    
    def check_new_data(self) -> dict[str, str]:
        logging.debug("Checking new data in:" + self.db_path)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        act_count = self.get_current_row_count(cursor)
        if act_count > self.row_count:
            self.row_count = act_count
            logging.debug(f"New data in database: {self.db_path}")
            return self.table_info
        conn.commit()
        conn.close()
        return None

    
    def get_last_rows(self, n: int) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Convert the list of columns to a string format suitable for a SQL query
        columns_str = ', '.join(self.columns)
        # Create a SQL query to select the last n rows from a table, ordering by date
        select_sql = f"SELECT {columns_str} FROM (SELECT {columns_str} FROM {self.table_name} ORDER BY date DESC LIMIT ?) ORDER BY date"
        # Execute the SQL query
        cursor.execute(select_sql, (n,))
        # Get the column names from the cursor description
        columns = [description[0] for description in cursor.description]
        # Fetch all rows from the executed SQL command and convert them to dictionaries
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.commit()
        conn.close()

        return rows 
    
