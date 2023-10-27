# Author: Leonardo lorenzato, Matteo Lorenzato
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

# math
import math

# deque
from collections import deque

# sys
import sys

#####################################################################################################
#            Options                                                                                #
#####################################################################################################

# Set print array with max size
np.set_printoptions(threshold=sys.maxsize)

#####################################################################################################
#            Classes                                                                              #
#####################################################################################################

class MyCandlesAry:
    def __init__(self, ary_open, ary_close, ary_high, ary_low):
        self.open = ary_open
        self.close = ary_close
        self.high = ary_high
        self.low = ary_low


class EMA:
    def __init__(self, window):
        self.i = 0
        self.memo_data_valid = False
        self.index_data_valid = 0
        self.window = window
        self.alpha = 2 / (self.window + 1)
        self.ma_weight = 1 / self.window
        self.ema = 0.0

    def update(self, data_in):
        '''
        This function calculates the exponential moving average of an input element
        '''
        # Initialize output as NaN
        data_out = np.NaN
        # Check if data is valid, i.e. not NaN
        if not np.isnan(data_in):
            data_valid = True
            if not self.memo_data_valid:
                # Save the index of the first valid element
                self.index_data_valid = self.i
        else:
            data_valid = False
        # Check if there are invalid values between valid values
        if self.memo_data_valid and not data_valid:
            raise ValueError('NaN found in valid array data')
        # Start calculation when data is valid
        if data_valid:
            # After self.window number of valid values start to update the EMA
            if self.i > (self.window-1) + self.index_data_valid:
                self.ema = ((data_in - self.ema) * self.alpha) + self.ema
            else:
                # At the first valid input data calculate the SMA once
                self.ema = (data_in * self.ma_weight) + self.ema
            # Return output after self.window valid values
            if self.i >= (self.window-1) + self.index_data_valid:
                data_out = self.ema
        # Save if current data is valid or not
        self.memo_data_valid = data_valid
        # Increase the loop index
        self.i += 1
        return data_out


class Diff:
    def __init__(self):
        self.i = 0
        self.memo_data_valid = False
        self.index_data_valid = 0
        self.window = 2
        self.data_prev = np.NaN
        self.diff = None

    def update(self, data_in):
        '''
        This function calculates the difference between two values
        '''
        # Initialize output as NaN
        data_out = np.NaN
        # Check if data is valid, i.e. not NaN
        if not np.isnan(data_in):
            data_valid = True
            if not self.memo_data_valid:
                # Save the index of the first valid element
                self.index_data_valid = self.i
        else:
            data_valid = False
        # Check if there are invalid values between valid values
        if self.memo_data_valid and not data_valid:
            raise ValueError('NaN found in valid array data')
        # Start calculation when data is valid
        if data_valid:
            # Return output after self.window valid values
            if self.i >= (self.window-1) + self.index_data_valid:
                self.diff = data_in - self.data_prev
                data_out = self.diff
            self.data_prev = data_in
        # Save if current data is valid or not
        self.memo_data_valid = data_valid
        # Increase the loop index
        self.i += 1
        return data_out


class STD:
    def __init__(self, window):
        self.i = 0
        self.memo_data_valid = False
        self.index_data_valid = 0
        self.window = window
        self.data = deque([0.0] * window, maxlen=window)
        self.mean = self.variance = self.stdev = 0.0

    def update(self, data_in):
        '''
        This function calculates the standard deviation of an input element
        '''
        # Initialize output as NaN
        data_out = np.NaN
        # Check if data is valid, i.e. not NaN
        if not np.isnan(data_in):
            data_valid = True
            if not self.memo_data_valid:
                # Save the index of the first valid element
                self.index_data_valid = self.i
        else:
            data_valid = False
        # Check if there are invalid values between valid values
        if self.memo_data_valid and not data_valid:
            raise ValueError('NaN found in valid array data')
        # Start calculation when data is valid
        if data_valid:
            new_mean = self.mean + (data_in - self.data[0]) / self.window
            self.variance += (data_in - self.data[0]) * ((data_in - new_mean) + (self.data[0] - self.mean)) / self.window
            self.stdev = math.sqrt(abs(self.variance))
            self.data.append(data_in)
            self.mean = new_mean
            # Return output after self.window valid values
            if self.i >= (self.window-1) + self.index_data_valid:
                data_out = self.stdev
        # Save if current data is valid or not
        self.memo_data_valid = data_valid
        # Increase the loop index
        self.i += 1
        return data_out


class MA:
    def __init__(self, window):
        self.i = 0
        self.memo_data_valid = False
        self.index_data_valid = 0
        self.window = window
        self.data = deque([0.0] * window, maxlen=window)
        if window > 0:
            self.ma_weight = 1 / self.window
        else:
            self.ma_weight = 1
        self.ma = 0.0

    def update(self, data_in):
        '''
        This function calculates the exponential moving average of an input element
        '''
        # Initialize output as NaN
        data_out = np.NaN
        # Check if data is valid, i.e. not NaN
        if not np.isnan(data_in):
            data_valid = True
            if not self.memo_data_valid:
                # Save the index of the first valid element
                self.index_data_valid = self.i
        else:
            data_valid = False
        # Check if there are invalid values between valid values
        if self.memo_data_valid and not data_valid:
            raise ValueError('NaN found in valid array data')
        # Start calculation when data is valid
        if data_valid:
            # At the first valid input data calculate the SMA once
            self.ma = self.ma + (data_in - self.data[0]) / self.window
            self.data.append(data_in)
            # Return output after self.window valid values
            if self.i >= (self.window-1) + self.index_data_valid:
                data_out = self.ma
        # Save if current data is valid or not
        self.memo_data_valid = data_valid
        # Increase the loop index
        self.i += 1
        return data_out


class SetValueIfGreater:
    def __init__(self, value_if_false, value_if_true):
        self.i = 0
        self.memo_data_valid = False
        self.index_data_valid = 0
        self.value_if_false = value_if_false
        self.value_if_true = value_if_true

    def check(self, data_in, data_ref):
        '''
        This function tests tests if a value is greeater than a reference value
        '''
        # Initialize output as NaN
        data_out = np.NaN
        # Check if data is valid, i.e. not NaN
        if not np.isnan(data_in):
            data_valid = True
            if not self.memo_data_valid:
                # Save the index of the first valid element
                self.index_data_valid = self.i
        else:
            data_valid = False
        # Check if there are invalid values between valid values
        if self.memo_data_valid and not data_valid:
            raise ValueError('NaN found in valid array data')
        # Start calculation when data is valid
        if data_valid:
            if not np.isnan(data_ref):
                if data_in > data_ref:
                    data_out = self.value_if_true
                else:
                    data_out = self.value_if_false
        # Save if current data is valid or not
        self.memo_data_valid = data_valid
        # Increase the loop index
        self.i += 1
        return data_out


class Crossunder:
    def __init__(self):
        self.i = 0
        self.memo_data_valid = False
        self.index_data_valid = 0
        self.prev_data_in = np.NaN
        self.prev_data_ref = np.NaN

    def check(self, data_in, data_ref):
        '''
        This function tests tests if there was a crossunder between two values
        '''
        # Initialize output as NaN
        data_out = np.NaN
        # Check if data is valid, i.e. not NaN
        if not np.isnan(data_in):
            data_valid = True
            if not self.memo_data_valid:
                # Save the index of the first valid element
                self.index_data_valid = self.i
        else:
            data_valid = False
        # Check if there are invalid values between valid values
        if self.memo_data_valid and not data_valid:
            raise ValueError('NaN found in valid array data')
        # Start calculation when data is valid
        if data_valid:
            if not np.isnan(self.prev_data_in) and not np.isnan(self.prev_data_ref) and not np.isnan(data_ref):
                if (data_in < data_ref) and (self.prev_data_in >= self.prev_data_ref):
                    data_out = True
                else:
                    data_out = False
        # Save current input data and current reference data
        self.prev_data_in = data_in
        self.prev_data_ref = data_ref
        # Save if current data is valid or not
        self.memo_data_valid = data_valid
        # Increase the loop index
        self.i += 1
        return data_out


class Crossover:
    def __init__(self):
        self.i = 0
        self.memo_data_valid = False
        self.index_data_valid = 0
        self.prev_data_in = np.NaN
        self.prev_data_ref = np.NaN

    def check(self, data_in, data_ref):
        '''
        This function tests tests if there was a crossover between two values
        '''
        # Initialize output as NaN
        data_out = np.NaN
        # Check if data is valid, i.e. not NaN
        if not np.isnan(data_in):
            data_valid = True
            if not self.memo_data_valid:
                # Save the index of the first valid element
                self.index_data_valid = self.i
        else:
            data_valid = False
        # Check if there are invalid values between valid values
        if self.memo_data_valid and not data_valid:
            raise ValueError('NaN found in valid array data')
        # Start calculation when data is valid
        if data_valid:
            if not np.isnan(self.prev_data_in) and not np.isnan(self.prev_data_ref) and not np.isnan(data_ref):
                if (data_in > data_ref) and (self.prev_data_in <= self.prev_data_ref):
                    data_out = True
                else:
                    data_out = False
        # Save current input data and current reference data
        self.prev_data_in = data_in
        self.prev_data_ref = data_ref
        # Save if current data is valid or not
        self.memo_data_valid = data_valid
        # Increase the loop index
        self.i += 1
        return data_out


#####################################################################################################
#            Functions                                                                              #
#####################################################################################################

def max_min_finder_fib(lst, start, end):
    '''
    This function calculates indexes for absolute minimum and maximum in an array
    '''
    max_value = lst[start]
    min_value = lst[start]
    index_max = start
    index_min = start

    for t in range(start, end):
        if lst[t] > max_value:
            max_value = lst[t]
            index_max = t

        if lst[t] < min_value:
            min_value = lst[t]
            index_min = t

    return index_max, index_min


def get_tp_lev_and_perc_compressed(ary_tp_levels, ary_fib_levels_percentage, ary_mask):
    '''
    This function gives an array with tp levels compressed at the beginning of the array,
    an array with percentage of each selected level, compressed in the same way as with levels array
    and total levels number
    '''
    ary_tp_levels_set = np.empty(len(ary_tp_levels))
    ary_tp_levels_set[:] = np.NaN
    ary_tp_levels_perc_set = np.empty(len(ary_tp_levels))
    ary_tp_levels_perc_set[:] = np.NaN
    levels_number = 0
    i_start = 0
    i = i_start
    for _ in itertools.repeat(None, len(ary_tp_levels)-i_start):
        if ary_mask[i]:
            ary_tp_levels_set[levels_number] = ary_tp_levels[i]
            ary_tp_levels_perc_set[levels_number] = ary_fib_levels_percentage[i]
            levels_number += 1
        i += 1
    return ary_tp_levels_set, ary_tp_levels_perc_set, levels_number


def get_tp_levels_from_params_list(params):
    '''
    This function gives 4 arrays:
    - take profit levels for long positions
    - take profit levels percentage for long positions
    - take profit levels for short positions
    - take profit levels percentage for short positions
    '''
    ary_tp_level_long = np.array(
        [params.tp_long_1 > 0.0,
         params.tp_long_2 > 0.0,
         params.tp_long_3 > 0.0,
         params.tp_long_4 > 0.0,
         params.tp_long_5 > 0.0,
         params.tp_long_6 > 0.0,
         params.tp_long_7 > 0.0,
         params.tp_long_8 > 0.0,
         params.tp_long_9 > 0.0,
         params.tp_long_10 > 0.0,
         params.tp_long_11 > 0.0,
         params.tp_long_12 > 0.0]
    )
    ary_tp_level_percentage_long = np.array(
        [params.tp_long_1,
         params.tp_long_2,
         params.tp_long_3,
         params.tp_long_4,
         params.tp_long_5,
         params.tp_long_6,
         params.tp_long_7,
         params.tp_long_8,
         params.tp_long_9,
         params.tp_long_10,
         params.tp_long_11,
         params.tp_long_12]
    )
    ary_tp_level_short = np.array(
        [params.tp_short_1 > 0.0,
         params.tp_short_2 > 0.0,
         params.tp_short_3 > 0.0,
         params.tp_short_4 > 0.0,
         params.tp_short_5 > 0.0,
         params.tp_short_6 > 0.0,
         params.tp_short_7 > 0.0,
         params.tp_short_8 > 0.0,
         params.tp_short_9 > 0.0,
         params.tp_short_10 > 0.0,
         params.tp_short_11 > 0.0,
         params.tp_short_12 > 0.0]
    )
    ary_tp_level_percentage_short = np.array(
        [params.tp_short_1,
         params.tp_short_2,
         params.tp_short_3,
         params.tp_short_4,
         params.tp_short_5,
         params.tp_short_6,
         params.tp_short_7,
         params.tp_short_8,
         params.tp_short_9,
         params.tp_short_10,
         params.tp_short_11,
         params.tp_short_12]
    )

    return ary_tp_level_long, ary_tp_level_percentage_long, ary_tp_level_short, ary_tp_level_percentage_short




