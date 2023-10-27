# Author:  Matteo Lorenzato
# Date: 2023-08-26


#####################################################################################################
#            This module contains a collections of array management functions                        #
#####################################################################################################

#####################################################################################################
#            Import section                                                                         #
#####################################################################################################

# Numpy
import numpy as np

# itertools
import itertools

# MyArrayFunctions
from core_lib import MyAryFunctions

from abc import ABC, abstractmethod

import json
#####################################################################################################
#            Classes                                                                                #
#####################################################################################################

class LimitOrder(ABC):

    def __init__(self, ary_price_level, ary_order_percentage, type_pos):
        self.level = ary_price_level
        self.type_pos = type_pos
        self.percent = ary_order_percentage

    @abstractmethod
    def to_dict(self):
        pass

class TakeProfit(LimitOrder):
    def __init__(self, ary_price_level, ary_order_percentage, type_pos):
        super().__init__(ary_price_level, ary_order_percentage, type_pos)

    def to_dict(self):
        result = {}
        for i in range(len(self.level)):
            result[i] = {'type_pos': self.type_pos, 'price': self.level[i], 'percent': self.percent[i]}
        return json.dumps(result)

class OpenPosLimit(LimitOrder):
    def __init__(self, ary_price_level, ary_order_percentage, type_pos):
        super().__init__(ary_price_level, ary_order_percentage, type_pos)

    def to_dict(self):
        result = {}
        for i in range(len(self.level)):
            result[i] = {'type_pos': self.type_pos, 'price': self.level[i], 'percent': self.percent[i]}
        return json.dumps(result)

class OpenPos():
    def __init__(self):
        # Memorize last open pos
        self.memo_open_pos = None
        # Memorize if long position active
        self.memo_long_pos_open = False
        # Memorize if short position active
        self.memo_short_pos_open = False
        # Memorize quantity of opened position
        self.memo_position_qty_open = 0

    def update(self, price_ref, condition_open_long, condition_close_long, condition_open_short, condition_close_short, stop_loss, consent_check=False):

        position_qty_open = self.memo_position_qty_open
        # Do you care about giving consent to opening/closing condition check?
        # (ex. open long positions only if previous position is a short one)
        consent_check = consent_check

         # If Long -> 100 else Short -> -100
        open_long_consent = (self.memo_open_pos == 's' or self.memo_open_pos is None) or not consent_check
        open_short_consent = (self.memo_open_pos == 'l' or self.memo_open_pos is None) or not consent_check

        # Check if act position touches stop loss
        if position_qty_open > 0:
            if price_ref.low <= stop_loss:
                position_qty_open = 0
                self.memo_long_pos_open = False
        elif position_qty_open < 0:
            if price_ref.high >= stop_loss:
                position_qty_open = 0
                self.memo_short_pos_open = False

        # Long close condition
        if condition_close_long and open_short_consent and self.memo_long_pos_open:
            position_qty_open = 0
            self.memo_long_pos_open = False
        # Short close condition
        if condition_close_short and open_long_consent and self.memo_short_pos_open:
            position_qty_open = 0
            self.memo_short_pos_open = False
        # Long open condition
        if condition_open_long and open_long_consent and not self.memo_long_pos_open:
            position_qty_open = 100
            self.memo_open_pos = 'l'
            self.memo_long_pos_open = True
        # Short open condition
        if condition_open_short and open_short_consent and not self.memo_short_pos_open:
            position_qty_open = -100
            self.memo_open_pos = 's'
            self.memo_short_pos_open = True

        self.memo_position_qty_open = position_qty_open

        return position_qty_open


class StopLoss():
    def __init__(self):
        # Memorize previous stop loss level
        self.price = 0.0
        # Memorize trailing stop loss treshold
        self.memo_trailing_threshold = 0.0
        # Memorize quantity of opened position
        self.memo_position_qty_open = None

    def update(self, price_ref, open_pos,
                     stop_loss_long, stop_loss_short, trailing_enable=False):
        '''
        This function returns if a long/short position is opened
        It also returns the stop loss level
        '''

        # Define if trailing stop is enabled
        trailing_enable = trailing_enable

        # Copy previous data
        position_qty_open = open_pos

        # Check stop loss levels, if reached then the position open array will be modified and set to zero
        # Long positions
        if position_qty_open > 0:
            # Calculate new stop loss level when position is opened and price is higher than previous maximum price
            if self.memo_position_qty_open > 0 and price_ref.close > self.memo_trailing_threshold and trailing_enable:
                stop_loss_level = price_ref.close - price_ref.close * stop_loss_long / 100
                trailing_threshold = price_ref.close
                # Save trailing stop loss treshold
                self.memo_trailing_threshold = trailing_threshold
            # Calculates the stop loss price when it opens a position
            elif self.memo_position_qty_open <= 0:
                stop_loss_level = price_ref.close - price_ref.close * stop_loss_long / 100
                self.price = stop_loss_level
                trailing_threshold = price_ref.close
                # Save trailing stop loss treshold
                self.memo_trailing_threshold = trailing_threshold
            else:
                stop_loss_level = self.price
            # Check every new data if stop loss is reached
            if price_ref.low <= self.price and self.memo_position_qty_open > 0:
                stop_loss_level = 0.0
        # Short positions
        elif position_qty_open < 0:
            # Calculate new stop loss level when position is opened and price is higher than previous maximum price
            if self.memo_position_qty_open < 0 and price_ref.close < self.memo_trailing_threshold and trailing_enable:
                stop_loss_level = price_ref.close + price_ref.close * stop_loss_short / 100
                trailing_threshold = price_ref.close
                # Save trailing stop loss treshold
                self.memo_trailing_threshold = trailing_threshold
            # Calculates the stop loss price when it opens a position
            if self.memo_position_qty_open >= 0:
                stop_loss_level = price_ref.close + price_ref.close * stop_loss_short / 100
                self.price = stop_loss_level
                trailing_threshold = price_ref.close
                # Save trailing stop loss treshold
                self.memo_trailing_threshold = trailing_threshold
            else:
                stop_loss_level = self.price
            # Check every new data if stop loss is reached
            if price_ref.high >= self.price and self.memo_position_qty_open < 0:
                stop_loss_level = 0.0
        elif position_qty_open == 0 and self.memo_position_qty_open == 0:
            stop_loss_level = 0.0
        else:
            stop_loss_level = self.price

        # Save previous opened position quantity
        self.memo_position_qty_open = position_qty_open
        # Save previous stop loss level
        self.price = stop_loss_level
        # Write NaN in stop loss level array if it's equal to zero, this is used only for plotting purpose
        if stop_loss_level == 0.0 or stop_loss_level is None:
            stop_loss_level = np.NaN

        return stop_loss_level

class OpenPosPerc():
    def __init__(self):
        # Memorize if take profit has been done
        self.tp_set = False
        # Current take profit index
        self.tp_index = 0
        # Take profit to be used
        self.tp_index_test = 0
        # Memorize data reference used for triggering a take profit
        self.memo_data_open_pos = 0
        # Save open position status
        self.memo_open_pos = 0
        # Memorize refence data
        self.memo_data_in = 0
        # Save opened position percentage
        self.memo_open_pos_perc = 0
        # Save take profit object
        self.memo_obj_tp_level = None
        # Save stoploss status
        self.sl_done = False

    def update(self, i, data_in, last_stop_loss_price, obj_tp_level, open_pos, tp_price_list, candle_close_price, candle_low_price, candle_high_price, pl, limit_order_tp, repeat_tp=False, disable_check_open_pos=False):
        '''
        This function gives an array that tells the percentage of a long/short position that is opened
        '''

        if self.memo_open_pos > 0 and candle_low_price < last_stop_loss_price:
            # Set close price to limit order price of stoploss
            self.sl_done = True
            price_for_limit_orders = last_stop_loss_price
            pl.update(i, 0, price_for_limit_orders, candle_close_price, limit_order_tp)
                
        if self.memo_open_pos < 0 and candle_high_price > last_stop_loss_price:
            # Set close price to limit order price of stoploss
            self.sl_done = True
            price_for_limit_orders = last_stop_loss_price
            pl.update(i, 0, price_for_limit_orders, candle_close_price, limit_order_tp)

        open_pos_perc = open_pos
        price_for_limit_orders = candle_close_price
        
        # Open or swap
        if (open_pos != self.memo_open_pos) or (open_pos != 0 and self.sl_done):
            self.tp_set = False
            self.tp_index = 0
            self.tp_index_test = 0
            self.sl_done = False
            # If there is a change in position then memorize data from data array
            if open_pos_perc != 0:
                self.memo_data_open_pos = data_in.close
        else:
            if not self.sl_done:
                # keep previous open pos perc if take profit has been done
                if self.tp_set:
                    open_pos_perc = self.memo_open_pos_perc
                # Check if take profit has been reached
                if self.tp_index < obj_tp_level.percent.size:
                    k_start = self.tp_index
                    k = k_start
                    for _ in itertools.repeat(None, obj_tp_level.percent.size-k_start):
                        # Long positions
                        if self.memo_open_pos_perc > 0:
                            if open_pos > 0 \
                                    and obj_tp_level.level[k] <= data_in.high \
                                    and self.memo_data_in < self.memo_obj_tp_level.level[k] \
                                    and (obj_tp_level.level[k] > self.memo_data_open_pos or disable_check_open_pos):
                                open_pos_perc = open_pos_perc - (
                                        open_pos_perc * obj_tp_level.percent[k] / 100)
                                # Set close price to limit order price of take profit
                                price_for_limit_orders = tp_price_list[k]
                                #pl update
                                pl.update(i, open_pos_perc, price_for_limit_orders, candle_close_price, limit_order_tp)
                                self.tp_set = True
                                # Select if a take profit can be used again or not
                                if not repeat_tp:
                                    self.tp_index_test = k + 1
                        # Short positions
                        if self.memo_open_pos_perc < 0:
                            if open_pos < 0 \
                                    and obj_tp_level.level[k] >= data_in.low \
                                    and self.memo_data_in > self.memo_obj_tp_level.level[k] \
                                    and (obj_tp_level.level[k] < self.memo_data_open_pos or disable_check_open_pos):
                                open_pos_perc = open_pos_perc + (
                                        abs(open_pos_perc) * obj_tp_level.percent[k] / 100)
                                # Set close price to limit order price of take profit
                                price_for_limit_orders = tp_price_list[k]
                                #pl update
                                pl.update(i, open_pos_perc, obj_tp_level.level[k], candle_close_price, limit_order_tp)

                                self.tp_set = True
                                # Select if a take profit can be used again or not
                                if not repeat_tp:
                                    self.tp_index_test = k + 1
                        k += 1
        # Save open position status
        self.memo_open_pos = open_pos
        # Take profit index
        self.tp_index = self.tp_index_test
        # Save refence data
        self.memo_data_in = data_in.close
        # Save opened position percentage
        self.memo_open_pos_perc = open_pos_perc
        # Save take profit object
        self.memo_obj_tp_level = obj_tp_level
            
        #pl update
        pl.update(i, open_pos_perc, price_for_limit_orders, candle_close_price, limit_order_tp)

        return open_pos_perc, price_for_limit_orders


class TakeProfitPolicy():
    def __init__ (self, policy, n_data_to_check = 0):
        # Loop index
        self.i = 0
        # Auxiliary NaN values array
        self.ary_nan = np.empty(1)
        self.ary_nan[:] = np.NaN
        # Policy type
        self.policy = policy
        if self.policy == 'factor':
            # Number of data to check for take profit calculatrion
            self.n_data_to_check = n_data_to_check
            # Memorize percentage of position that is opened
            self.memo_open_pos = 0
            self.memo_take_profit_obj = TakeProfit(self.ary_nan, self.ary_nan, '')
            self.memo_open_index_long = 0
            self.memo_open_index_long_temp = 0
            self.memo_open_index_short = 0
            self.memo_open_index_short_temp = 0
            self.memo_price_open_long = 0
            self.memo_temp_price_open_long = 0
            self.memo_price_open_short = 0
            self.memo_temp_price_open_short = 0
        self.long_label = 'l'
        self.short_label = 's'

    def calc_tp_obj(self, data_price_ref, data_open_pos, ary_high, ary_low, ary_lev_long, ary_lev_short,
                    ary_levels_long_percent_set, ary_levels_short_percent_set):
        if self.policy == 'factor':
            return self.get_take_profit_obj_w_factor(data_price_ref, data_open_pos, ary_high, ary_low, ary_lev_long, ary_lev_short,
                                                     ary_levels_long_percent_set, ary_levels_short_percent_set)
        elif self.policy == 'reference':
            return self.get_take_profit_obj_w_reference(data_open_pos, ary_lev_long, ary_lev_short,
                                                    ary_levels_long_percent_set, ary_levels_short_percent_set)
        else:
            raise ValueError('Policy type' + ' ' + self.policy + ' ' + 'not allowed.')

    def get_take_profit_obj_w_factor(self, data_price_ref, data_open_pos, lst_high, lst_low, ary_lev_long, ary_lev_short,
                                     ary_levels_long_percent_set, ary_levels_short_percent_set):
        '''
        This function returns a take profit object given asset prices, take profit levels and percentage
        '''

        # Keep previous value
        take_profit_obj = self.memo_take_profit_obj
        if data_open_pos != self.memo_open_pos:
            # Long position closing
            if self.memo_open_pos > 0:
                if self.memo_price_open_long_temp < data_price_ref:
                    self.memo_price_open_long = self.memo_price_open_long_temp
                    self.memo_open_index_long = self.memo_open_index_long_temp
            # Long position opening
            if data_open_pos > 0:
                max_close_long_index, _ = MyAryFunctions.max_min_finder_fib(lst_high, self.memo_open_index_long,
                                                                            (self.i) - self.n_data_to_check)
                _, min_close_long_index = MyAryFunctions.max_min_finder_fib(lst_low, max_close_long_index,
                                                                            (self.i) - self.n_data_to_check)
                take_profit_obj = TakeProfit(
                    calc_tp_prices_fib_extension(self.memo_price_open_long, lst_high[max_close_long_index],
                                                 lst_low[min_close_long_index], ary_lev_long,
                                                 len(ary_lev_long),
                                                 self.long_label), ary_levels_long_percent_set[:], self.long_label)
                self.memo_price_open_long_temp = data_price_ref
                self.memo_open_index_long_temp = self.i
            # Short position closing
            if self.memo_open_pos < 0:
                if self.memo_price_open_short_temp > data_price_ref:
                    self.memo_price_open_short = self.memo_price_open_short_temp
                    self.memo_open_index_short = self.memo_open_index_short_temp
            # Short position opening
            if data_open_pos < 0:
                _, min_close_short_index = MyAryFunctions.max_min_finder_fib(lst_low, self.memo_open_index_short,
                                                                             (self.i) - self.n_data_to_check)
                max_close_short_index, _ = MyAryFunctions.max_min_finder_fib(lst_high, min_close_short_index,
                                                                             (self.i) - self.n_data_to_check)
                take_profit_obj = TakeProfit(
                    calc_tp_prices_fib_extension(self.memo_price_open_short, lst_high[max_close_short_index],
                                                 lst_low[min_close_short_index], ary_lev_short,
                                                 len(ary_lev_short),
                                                 self.short_label), ary_levels_short_percent_set[:], self.short_label)
                self.memo_price_open_short_temp = data_price_ref
                self.memo_open_index_short_temp = self.i
            # Position is closed
            if data_open_pos == 0:
                take_profit_obj = TakeProfit(self.ary_nan, self.ary_nan, '')
        self.memo_open_pos = data_open_pos
        # Save take profit object
        self.memo_take_profit_obj = take_profit_obj
        self.i += 1
        return take_profit_obj

    def get_take_profit_obj_w_reference(self, data_open_pos, ary_lev_long, ary_lev_short,
                                ary_levels_long_percent_set, ary_levels_short_percent_set):
        '''
        This function returns a take profit objects given asset prices, take profit levels and percentage
        Take profit has a dynamic reference (i.e. it's level is given by a reference series of arrays)
        '''

        # Long position opening
        if data_open_pos > 0:
            take_profit_obj = TakeProfit(ary_lev_long, ary_levels_long_percent_set[:], self.long_label)
        # Short position opening
        elif data_open_pos < 0:
            take_profit_obj = TakeProfit(ary_lev_short, ary_levels_short_percent_set[:], self.short_label)
        else:
            # Take profit object array
            take_profit_obj = TakeProfit(self.ary_nan, self.ary_nan, '')

        return take_profit_obj


#####################################################################################################
#            Functions                                                                              #
#####################################################################################################

def calc_tp_prices_fib_extension(open_price, max_price, min_price, ary_tp_level, number_tp, type_pos):
    ary_tp_prices = np.empty(number_tp)
    ary_tp_prices[:] = np.NaN
    i_start = 0
    i = i_start
    for _ in itertools.repeat(None, number_tp-i_start):
        if type_pos == 'l':
            ary_tp_prices[i] = abs(open_price - max_price) * ary_tp_level[i] + min_price
        elif type_pos == 's':
            ary_tp_prices[i] = max_price - abs(open_price - min_price) * ary_tp_level[i]
        i += 1
    return ary_tp_prices


