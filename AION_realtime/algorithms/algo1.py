# Author:  Matteo Lorenzato
# Date: 2023-08-26


#####################################################################################################
#            This module contains the algorithms objects                                            #
#####################################################################################################

#####################################################################################################
#            Import section                                                                         #
#####################################################################################################

import numpy as np
import pandas as pd
import time
import itertools
from core_lib import MyAryFunctions, MyIndicators, MyDataFrameManagement, MyPerformanceManagement, MyListFunctions
from copy import deepcopy
#####################################################################################################
#            Class                                                                             #
#####################################################################################################

class algo1:
    
    global value_when_true, value_when_false, init_cap
    value_when_true = 100.0
    value_when_false = -100.0
    init_cap = 100.0

    def __init__(self, df, general_data, params):

        # Parameters list
        self.params = params

        # General data
        self.general = general_data

        # Pair
        self.pair = self.general.asset + self.general.asset_ref

        # Fund weight
        self.fund_weight = params.fund_weight

        # Initial dataframe
        self.init_df = deepcopy(df)

        # Dataframe
        self.df = deepcopy(df)
        
        if not 'date' in df.columns:
            raise KeyError('Date column named date expected in input dataframe')

        # Data index
        self.i = 0

        # Indicator objects
        self.slow_ema = MyAryFunctions.EMA(params.period_slowMA)
        self.fast_ema = MyAryFunctions.EMA(params.period_fastMA)
        self.crossunder_fast_slow = MyAryFunctions.Crossunder()
        self.crossover_fast_slow = MyAryFunctions.Crossover()
        self.open_pos = MyIndicators.OpenPos()
        self.stop_loss = MyIndicators.StopLoss()
        self.open_pos_perc = MyIndicators.OpenPosPerc()
        
        # Pre-execution time
        self.pre_exe_time = 0.0

        # Updating time
        self.exe_time = 0.0

        # Average updating time
        self.avg_exe_time = 0.0

        # Build object structure
        self.build()

    def build(self):
        # Create candles
        self.candles = MyListFunctions.MyCandles(self.df['open'].tolist(), self.df['close'].tolist(), self.df['high'].tolist(), self.df['low'].tolist())

        # Set price reference array
        if self.params.price_filter == 'oc2':
            self.lst_price_ref = [(close + open)/2 for close, open in zip(self.candles.close, self.candles.open)]
        elif self.params.price_filter == 'hloc4':
            self.lst_price_ref = [(close + open + high + low)/4 for close, open, high, low in zip(self.candles.close, self.candles.open, self.candles.high, self.candles.low)]
        else:
            self.lst_price_ref = self.candles.close

        # Indicators list
        self.lst_ma = []
        self.lst_ma_slow = []
        self.lst_ma_fast = []
        self.lst_crossunder_fast_slow_price = []
        self.lst_crossover_fast_slow_price = []
        self.lst_is_open = []
        self.lst_stop_loss_level = []
        self.lst_open_pos_perc = []            

    def update(self):

        start_time = time.time()

        # Data index
        i = self.i

        # Already available data
        params = self.params
        price_open = self.candles.open[i]
        price_close = self.candles.close[i]
        price_high = self.candles.high[i]
        price_low = self.candles.low[i]
        price_ref = self.lst_price_ref[i]
        
        # Calculate slow moving average
        self.lst_ma_slow.append(self.slow_ema.update(price_close))
        # Calculate fast moving average
        self.lst_ma_fast.append(self.fast_ema.update(price_close))
        # Calculate cross-under of reference price fast and slow moving average with reference price slow moving average
        value_crossunder_fast_slow = self.crossunder_fast_slow.check(self.lst_ma_fast[-1], self.lst_ma_slow[-1])
        if value_crossunder_fast_slow and not np.isnan(value_crossunder_fast_slow):
            self.lst_crossunder_fast_slow_price.append(price_close)
        else:
            self.lst_crossunder_fast_slow_price.append(np.NaN)
        value_crossover_fast_slow = self.crossover_fast_slow.check(self.lst_ma_fast[-1], self.lst_ma_slow[-1])
        if value_crossover_fast_slow and not np.isnan(value_crossover_fast_slow):
            self.lst_crossover_fast_slow_price.append(price_close)
        else:
            self.lst_crossover_fast_slow_price.append(np.NaN)

        # Get arrays for opening/closing conditions
        condition_open_long, condition_close_long, condition_open_short, condition_close_short = \
            get_position_condition(
                                    self.lst_crossunder_fast_slow_price[-1],
                                    self.lst_crossover_fast_slow_price[-1]
                                    )
        
        # Create candle object
        my_candle = MyListFunctions.MyCandle(price_open, price_close, price_high, price_low)
        # Get arrays for opened positions and for stop loss levels
        is_open = self.open_pos.update(my_candle,
                                        condition_open_long, condition_close_long,
                                        condition_open_short, condition_close_short,
                                        self.stop_loss.price, consent_check=False)
        self.lst_is_open.append(is_open)
                                                                         
        # Calculate the percentage of an opened position
        open_pos_perc = is_open
        
        self.lst_open_pos_perc.append(open_pos_perc)
        self.lst_price_for_limit_orders.append([])

        # Calc stoploss level
        stop_loss = self.stop_loss.update(my_candle, is_open, params.sl_long, params.sl_short, trailing_enable=True)
        self.lst_stop_loss_level.append(stop_loss)

        self.i +=1

        # Calc execution total time
        self.exe_time += (time.time() - start_time)

        # Calc execution averagime time
        self.avg_exe_time += (time.time() - start_time) / self.i

    def update_dataframe(self):
        # Save arrays into the dataframe
        #self.df['ma_slow'] = self.lst_ma_slow
        #self.df['ma_fast'] = self.lst_ma_fast
        #self.df['open_pos'] = self.lst_is_open
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['date'] = self.df['date'].apply(lambda x: x.timestamp())
        self.df['stop_loss_level'] = self.lst_stop_loss_level
        self.df['open_pos_perc'] = self.lst_open_pos_perc

    def to_dataframe(self):
        self.update_dataframe()
        return self.df

    def reinit(self):
        self.__init__(self.init_df, self.general, self.params)

    def update_all(self):
        data_length = len(self.df)
        for _ in itertools.repeat(None, data_length):
            self.update()

    def get_exe_time(self):
        return self.exe_time

    def who_am_i(self):
        my_name = self.__class__.__name__ + ' ' + self.pair
        return my_name


def get_position_condition(crossunder_fast_slow_price, crossover_fast_slow_price):
    '''
    This function returns conditions for opening or closing a position
    '''
    condition_close_long = False
    condition_open_long = False

    # Long close condition
    if not np.isnan(crossunder_fast_slow_price):
        condition_close_long = True
    # Long open condition
    if not np.isnan(crossover_fast_slow_price):
        condition_open_long = True

    return condition_open_long, condition_close_long
