# Author: Leonardo lorenzato, Matteo Lorenzato
# Date: 2023-08-26


#####################################################################################################
#            This module contains the data frame data calculations                                  #
#####################################################################################################

#####################################################################################################
#            Import section                                                                         #
#####################################################################################################

# Config
import config

# Numpy
import numpy as np

# Pandas
import pandas as pd

# Datetime
from datetime import datetime, timedelta

# Context manager
from contextlib import contextmanager

# itertools
import itertools

# Colorama
from colorama import Fore

# OS
import os 

# Files management
from core_lib import MyFileManagement


#####################################################################################################
#            Classes                                                                              #
#####################################################################################################

class MyDataframe:
    def __init__(self, name, dataframe):
        self.name = name
        self.df = dataframe


class WeightedAsset(MyDataframe):
    def __init__(self, name, dataframe, weight=0.5):
        super(WeightedAsset, self).__init__(name, dataframe)
        self.weight = weight

class MyStartEndDate:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

class WeightedFund:
    '''
    This class describes a fund as a weighted asset, intended as istance of WeightedAsset class
    and a dictionary of tickers which are WeightedAsset objects
    '''
    def __init__(self, weighted_asset):
        # String with fund name
        self.name = weighted_asset.name
        # weighted_asset is intended as object of WeightedAsset class
        self.weighted_asset = weighted_asset
        # Tickers are intended as objects of WeightedAsset class
        self.tickers = {}

class WeightedFundCollection:
    '''
    This class contains a collection of funds intended as istances of WeightedFund objects
    '''
    def __init__(self, name):
        # String with fund collection name
        self.name = name
        # weighted_asset is intended as object of WeightedAsset class
        self.weighted_asset = WeightedAsset(name, None, 1.0)
        # Funds are intended as objects of Fund class
        self.funds = {}

    def add_fund(self, weighted_asset):
        '''
        Add fund object to funds dictionary given a parameters set that represents the new fund to add
        '''
        self.funds[weighted_asset.name] = WeightedFund(weighted_asset)

    def add_ticker_to_fund(self, fund_name, ticker):
        '''
        Add ticker to a specific fund given a parameters set that represents the new ticker to add
        '''
        self.funds[fund_name].tickers[ticker.name] = ticker

    def add_tickers_to_fund(self, fund_name, tickers_list):
        '''
        Add a list of tickers to a specific fund given a list of weighted assets that represents the list of tickers to add
        '''
        for ticker in tickers_list:
            self.add_ticker_to_fund(fund_name, ticker)

    def get_funds_obj(self):
        '''
        Get a list with WeightedFund objects with all funds contained in the fund collection
        '''
        return [fund for fund in self.funds.values()]
    
    def get_funds(self):
        '''
        Get a list with all funds contained in the fund collection
        '''
        return [fund.weighted_asset for fund in self.funds.values()]

    def get_funds_name(self):
        '''
        Get a list with all funds names contained in the fund collection
        '''
        return [fund.name for fund in self.funds.values()]

    def get_tickers(self, fund_name):
        '''
        Get a list with all tickers contained in the specified fund 
        '''
        return [ticker for ticker in self.funds[fund_name].tickers.values()]

    def get_tickers_name(self, fund_name):
        '''
        Get a list with all tickers names contained in the specified fund 
        '''
        return [ticker.name for ticker in self.funds[fund_name].tickers.values()]

    def update_fund_df(self, fund_name, df):
        self.funds[fund_name].weighted_asset.df = df

    def update_ticker_df(self, fund_name, ticker_name, df):
        self.funds[fund_name].tickers[ticker_name].df = df

    def print_collection(self):
        '''
        Print entire fund collection
        '''
        print(Fore.LIGHTYELLOW_EX + 'Weighted fund collection' + ' ' + self.name + ': ' + Fore.RESET)
        for fund in self.funds.values():
            tickers_names = [ticker for ticker in fund.tickers.keys()]
            print('\t' + Fore.LIGHTCYAN_EX + fund.name + Fore.RESET + ':' + ' ' + ', '.join(tickers_names))

#####################################################################################################
#            Functions                                                                              #
#####################################################################################################

@contextmanager
def extrapolate_data_frame(dir_name):
    pass
    # Data file path
    dir_path = MyFileManagement.get_directory_path(dir_name, config.program_data_path)
    file_list = os.listdir(dir_path)
    if len(file_list) > 1:
        raise RuntimeError('More than one file found at: ' + dir_path)
    for f in file_list:
        file_path = dir_path + os.sep + f
        if not os.path.isfile(file_path):
            raise FileNotFoundError('No file found at location: ' + file_path)

    # Read csv file
    df = pd.read_csv(file_path)

    date_list = []
    # Write date column in the same datetime format
    for element in df['date']:
        date_list.append(datetime.strptime(element, '%Y-%m-%d %H:%M:%S'))
    # Replace date column with datetime list
    df['date'] = date_list
    
    try:
        yield df
    finally:
        df.iloc[0:0]


def get_dataframe_from_start_end_date(my_start_end_date, df):
    # Start date index (if not found returns 0)
    start_date_index = df['date'].eq(my_start_end_date.start_date).idxmax()
    # End date index (if not found returns 0)
    end_date_index = df['date'].eq(my_start_end_date.end_date).idxmax()
    if end_date_index == 0:
        end_date_index = len(df.index) - 1
    # Select a subset of the complete dataframe
    df = df.iloc[start_date_index:(end_date_index + 1)]
    # Rearrange indexes
    df.reset_index(drop=True, inplace=True)
    return df

def calc_max_value(column):
    '''
    This function calculates the maximum value and its index in a dataframe column
    '''
    max_value = column.max()
    max_value_index = column.idxmax()
    return max_value, max_value_index


def calc_min_value(column):
    '''
    This function calculates the minimum value and its index in a dataframe column
    '''
    min_value = column.min()
    min_value_index = column.idxmin()
    return min_value, min_value_index


def profitable_pos_perc(open_pos_list, net_profit):
    '''
    This function calculates percentage of profitable positions
    '''
    ary_open_pos = np.array(open_pos_list)
    ary_net_profit = np.array(net_profit)
    op_memo = 0
    position_is_open = False
    total_positions = 0
    total_positions_long = 0
    total_positions_short = 0
    positions_profit = 0
    positions_loss = 0
    positions_profit_long = 0
    positions_profit_short = 0
    net_profit_memo = 0
    i_start = 0
    i = i_start
    for _ in itertools.repeat(None, len(ary_open_pos)-i_start):
        if ary_open_pos[i] != op_memo:
            if position_is_open:
                total_positions += 1
                if ary_open_pos[i] < op_memo:
                    total_positions_long += 1
                else:
                    total_positions_short += 1
                if ary_net_profit[i] > net_profit_memo:
                    positions_profit +=  1
                    if ary_open_pos[i] < op_memo:
                        positions_profit_long += 1
                    else:
                        positions_profit_short += 1
                if ary_net_profit[i] < net_profit_memo:
                    positions_loss += 1
                position_is_open = False
            if ary_open_pos[i] != 0 and not position_is_open:
                net_profit_memo = ary_net_profit[i]
                position_is_open = True
        op_memo = ary_open_pos[i]
        i += 1
    # Calculate percentage of positions in profit
    if total_positions > 0:
        positions_profit_perc = positions_profit / total_positions * 100
    else:
        positions_profit_perc = 0
    # Calculate percentage of long positions in profit
    if total_positions_long > 0:
        positions_profit_long_perc = positions_profit_long / total_positions_long * 100
    else:
        positions_profit_long_perc = 0
    # Calculate percentage of short positions in profit
    if total_positions_short > 0:
        positions_profit_short_perc = positions_profit_short / total_positions_short * 100
    else:
        positions_profit_short_perc = 0
    return positions_profit_perc, total_positions, positions_profit_long_perc, total_positions_long, positions_profit_short_perc, total_positions_short

