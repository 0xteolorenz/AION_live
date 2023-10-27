# Author:  Matteo Lorenzato
# Date: 2023-08-26


# Numpy
from types import GenericAlias
import numpy as np

# Pandas
import pandas as pd

# Datetime
import datetime

# Context manager
from contextlib import contextmanager

# File management
from core_lib import MyFileManagement

# Dataframe management
from core_lib import MyDataFrameManagement

# Itertools
import itertools

class MyPerformanceObject:
    '''
    This class is describes an object that contains summary performance data
    '''

    def __init__(self, name, start_date, end_date, net_profit_perc, max_drawdown_perc, max_drawdown_date,
                 profitable_pos_perc, total_positions, 
                 profitable_pos_long_perc, total_positions_long, profitable_pos_short_perc, total_positions_short, 
                 buy_hold, max_buy_hold_drawdown_perc):
        # Object name
        self.name = name
        # Start date
        self.start_date = start_date
        # End date
        self.end_date = end_date
        # Net profit in percentage
        self.net_profit_perc = net_profit_perc
        # Max drawdown in percentage
        self.max_drawdown_perc = max_drawdown_perc
        # Max drawdown date
        self.max_drawdown_date = max_drawdown_date
        # Profitable potions in percentage
        self.profitable_pos_perc = profitable_pos_perc
        # Total positions inside the date range
        self.total_positions = total_positions
        # Profitable long potions in percentage
        self.profitable_pos_long_perc = profitable_pos_long_perc
        # Total long positions inside the date range
        self.total_positions_long = total_positions_long
        # Profitable short potions in percentage
        self.profitable_pos_short_perc = profitable_pos_short_perc
        # Total short positions inside the date range
        self.total_positions_short = total_positions_short
        # Buy and hold net profit
        self.buy_hold = buy_hold
        # Max Buy and hold drawdown in percentage
        self.max_buy_hold_drawdown_perc = max_buy_hold_drawdown_perc

    def to_dataframe(self):
        '''
        This function creates a dataframe with object attribute
        '''
        data = {'Start date': [self.start_date],
                'End date': [self.end_date],
                'Net Profit': [self.net_profit_perc],
                'Max Drawdown [%]': [self.max_drawdown_perc],
                'Max Drawdown Date': [self.max_drawdown_date],
                'Profit. Pos. [%]': [self.profitable_pos_perc],
                'Tot. Pos.': [self.total_positions],
                'Profit. Longs [%]': [self.profitable_pos_long_perc],
                'Tot. Longs': [self.total_positions_long],
                'Profit. Shorts [%]': [self.profitable_pos_short_perc],
                'Tot. Shorts': [self.total_positions_short],
                'Buy&Hold': [self.buy_hold],
                'Buy&Hold Drawdown [%]': [self.max_buy_hold_drawdown_perc]}
        df = pd.DataFrame(data, index=[self.name])
        return df


class Drawdown():
    def __init__(self, init_cap):
        # Initial capital
        self.init_cap = init_cap
        # Maximum capital
        self.max_cap = init_cap
        # Drawdown in percentage respect to maximum capital
        self.drawdown_perc = 0.0
        # Actiual drawdown capital
        self.memo_drawdown_cap = 0.0
        # Save net profit
        self.memo_net_profit = 0.0

    def update(self, net_profit):
        '''
        This function returns the drawdown percentage
        '''
        # When another maximum value for capital is found then overwrite the maximum capital
        if net_profit > self.memo_net_profit and net_profit + self.init_cap > self.max_cap:
            self.max_cap = net_profit + self.init_cap
        # Update actual drawdown capital  when capital il less than its maximum value
        if net_profit < self.memo_net_profit or net_profit + self.init_cap < self.max_cap:
            self.memo_drawdown_cap = self.memo_drawdown_cap + (
                    net_profit - self.memo_net_profit)
            self.drawdown_perc = (self.memo_drawdown_cap * 100) / self.max_cap
        # Reset drawdown when drawdown capital reaches the maximum capital previously found
        elif self.memo_drawdown_cap >= self.max_cap:
            self.memo_drawdown_cap = 0.0
            self.drawdown_perc = 0.0
        else:
            self.memo_drawdown_cap = 0.0
            self.drawdown_perc = 0.0
        # Save net profit
        self.memo_net_profit = net_profit

        return self.drawdown_perc

class HodlProfit:
        def __init__(self, init_cap):
            self.init_cap = init_cap
            self.memo_total_profit_hodl = init_cap
            self.total_profit_hodl = 0.0
            self.memo_close_price = 0.0

        def update(self, close_price):
            '''
            This function calculates the buy and hold net profit
            '''
            if self.memo_close_price != 0.0:
                self.total_profit_hodl = self.memo_total_profit_hodl + self.memo_total_profit_hodl * (
                        (close_price - self.memo_close_price) * 100 / self.memo_close_price) / 100
                # Update hodl capital
                self.memo_total_profit_hodl = self.total_profit_hodl
                # Save close price
                self.memo_close_price = close_price
                # Return net profit (sub initial capital)
                return (self.total_profit_hodl - self.init_cap)
            else:
                # Save close price
                self.memo_close_price = close_price
                return 0.0

class ProfitLoss:
    def __init__(self, init_cap, general, params):
        self.init_cap = init_cap
        self.init_cap_act_pos = init_cap
        self.realized_pl = init_cap
        self.unrealized_pl = 0.0
        self.n_contracts = 0.0
        self.memo_open_pos_price = 0.0
        self.memo_open_pos_perc = 0.0
        self.pl_perc = 0.0
        self.fees_value = 0.0
        self.pl_collateral = 0.0
        self.pl_collateral_tp = 0.0
        self.memo_i = 0
        self.cum_profit = init_cap
        self.last_cum_profit = init_cap
        self.net_profit = 0.0
        self.general = general
        self.params = params

    def get_pl(self):
        return self.pl_perc

    def get_contracts(self):
        return self.n_contracts

    def get_realized_pl(self):
        return self.realized_pl

    def get_unrealized_pl(self):
        return self.unrealized_pl

    def get_pl_collateral(self):
        return self.pl_collateral

    def get_fees(self):
        return self.fees_value

    def get_net_profit(self):
        return self.net_profit
    
    def get_cum_profit(self):
        return self.cum_profit
    
    def get_openposprice(self):
        return self.memo_open_pos_price


    def update(self, i, open_pos_perc, tp_limit_price, close_price, limit_order_tp):
        '''
        7/4/22
        open_pos_perc: actual position percentage
        tp_limit_price: limit order price target of actual position
        close_price: actual close price
        oc_fee: market order fee in percentage
        tp_fee: limit order fee in percentage
        funding_fee: funding fee in percentage
        limit_order_tp: if true we use limit order else market order at candle close

        With this function we calc all parameters that we need to build the entire profit&loss list of the position, it
        works during a change in open position percentage, but we could add fees or other particular capital changes too.
        Function is divided in blocks, each block is a different event that causes a change in our total capital.
        Total capital is composed of: initial capital, realized profit or loss and unrealized profit or loss.
        - First block: first we calc the actual candle percentage ideally just a moment before it closes or, if
        during this candle there is an order limit (as take profit or stop loss), the candle percentage since limit order
        target.
        - Second block: now with candle percentage we can obtain the actual position unrealized profit and loss value in
        absolute value (in example: $) just a moment before a specific event is going to happen.
        - Third block: here we add all events that we need they happen before an open_pos_perc changes or regardless of it
        like funding fees if there aren't events during this candle (worst case scenario).
        - Fourth block: this block contains all calc that we need during a change open_pos_perc, in other words when we
        close actual position partially or fully returning a profit or a loss in our act_cap (= sum of initial capital,
        actual realized profit or loss, actual unrealized profit or loss and actual unrealized profit or loss).
        IMPORTANT: now, if there was a limit order, we recalc the unrealized_pl at the candle close.
        - Fifth block: we check if the event occurred before was a swap (close act pos and open a new pos in the same candle
        close) or a stop loss, so we reset or update our capital parameters.
        - Sixth block: this event happens only if there wasn't an open position before this one, like the first position
        or after a stop loss, so here in example we can set the amount of capital to use for the actual trade.
        - Seventh block: Here we obtain the net percentage p/l after all events that we need to calc net profit.
        '''

        # Resetting triggers
        is_swap = False
        is_tp = False
        is_stop_loss = False
        trigger_position_qty_change = False

        
        # First block
        if ((open_pos_perc != 0 and self.memo_open_pos_price != 0) or (
                open_pos_perc == 0 and self.memo_open_pos_perc != 0)) and i != self.memo_i:
            # Compound interest of actual position one moment before candle closes (ideally)
            self.pl_collateral = self.memo_open_pos_perc / abs(self.memo_open_pos_perc) * (
                    close_price - self.memo_open_pos_price) / self.memo_open_pos_price
            self.pl_collateral_tp = self.memo_open_pos_perc / abs(self.memo_open_pos_perc) * (
                    tp_limit_price - self.memo_open_pos_price) / self.memo_open_pos_price

            # Second block
            # Set unrealized_pl before any events
            if limit_order_tp and close_price != tp_limit_price:
                self.unrealized_pl = self.init_cap_act_pos * abs(self.memo_open_pos_perc) / 100 * (
                        1 + self.pl_collateral_tp)  - self.fees_value
            else:
                self.unrealized_pl = self.init_cap_act_pos * abs(self.memo_open_pos_perc) / 100 * (
                        1 + self.pl_collateral) - self.fees_value

            # Third block
            # Calc funding fees
            if i % 8 == 0:
                loc_funding_fees = self.unrealized_pl * self.general.funding_fees / 100
                self.fees_value += loc_funding_fees
                self.unrealized_pl += - loc_funding_fees

        # Fourth block
        # Change of position direction or percentage event
        if open_pos_perc != self.memo_open_pos_perc:
            
            # Check if it is a swap
            if (self.memo_open_pos_perc > 0 and open_pos_perc < 0) or (
                    self.memo_open_pos_perc < 0 and open_pos_perc > 0):
                is_swap = True

            elif open_pos_perc == 0 and self.memo_open_pos_perc != 0:
                is_stop_loss == True

            else:
                is_tp = True

            # Close/Partial close position event.
            # If swap calculates only the unrealized and realized pl of the closing position
            if self.memo_open_pos_price != 0:
                # Save if a profit or loss occurs
                trigger_position_qty_change = True
                if is_swap:
                    actual_open_pos = 0
                else:
                    actual_open_pos = open_pos_perc
                    self.n_contracts *= (1 - ((abs(self.memo_open_pos_perc) - abs(actual_open_pos)) * 100 / (
                            abs(self.memo_open_pos_perc) * 100)))
                # Calc event p/l (Total/partial close position)
                # Calc the exit capital based on open position changes
                exit_cap = self.unrealized_pl * (
                        (abs(self.memo_open_pos_perc) - abs(actual_open_pos)) / abs(self.memo_open_pos_perc))
                # Use market order fees if is a swap
                if is_swap:
                    fees = exit_cap * (self.general.tr_fees_oc / 100)
                # Use limit order fees if is a take profit or a stop loss
                else:
                    
                    fees = exit_cap * (self.general.tr_fees_tp / 100)
            
                # Update cumulative profit
                self.last_cum_profit = self.cum_profit
                self.cum_profit += exit_cap - fees - self.init_cap_act_pos * (
                            (abs(self.memo_open_pos_perc) - abs(actual_open_pos)) / 100)
                # Update unrealized_pl and realized_pl
                self.realized_pl += exit_cap - fees
                self.unrealized_pl += - exit_cap
                
                # Update unrealized_pl if there was a take profit
                if is_tp:
                    self.unrealized_pl = self.init_cap_act_pos * abs(open_pos_perc) / 100 * (1 + self.pl_collateral) - self.fees_value

                
                # # If swap updates only the unrealized and realized pl of the opening position
                if is_swap:
                    self.memo_open_pos_price = close_price
                    self.fees_value = self.realized_pl * self.general.tr_fees_oc / 100
                    # Copy realized pl into unrealized pl
                    self.unrealized_pl = self.realized_pl * (1 - self.general.tr_fees_oc / 100)
                    self.n_contracts = self.unrealized_pl / close_price
                    self.init_cap_act_pos = self.realized_pl
                    # Update realized pl considering fees
                    self.realized_pl *= 100 - abs(open_pos_perc)

                # Fifth block
                # Resetting if there is not a position open (stop loss)
                if open_pos_perc == 0 and self.memo_open_pos_perc != 0:
                    self.memo_open_pos_price = 0
                    self.fees_value = 0

            # Sixth block
            # Open position if there is no other position opened
            if open_pos_perc != 0 and self.memo_open_pos_perc == 0:
                self.n_contracts = (self.realized_pl * abs(open_pos_perc) / 100) / close_price
                self.fees_value = self.realized_pl * self.general.tr_fees_oc / 100
                self.unrealized_pl = (self.realized_pl * abs(open_pos_perc) / 100)  - self.realized_pl * self.general.tr_fees_oc / 100
                self.init_cap_act_pos = self.realized_pl
                self.realized_pl *= 100 - abs(open_pos_perc)
                self.memo_open_pos_price = close_price

        ####################################################################################
        #                    here we can add a withdrawal block from realized_pl           #
        ####################################################################################
            
        # Seventh block
        # Update unrealized profit&loss
        # Calc net percentage profit/loss for net-profit
        if trigger_position_qty_change:
            # Calculate profit and loss
            self.pl_perc = ((self.cum_profit - self.last_cum_profit) / self.last_cum_profit) * 100
            # Calculate net profit
            self.net_profit = self.cum_profit - self.init_cap

        self.memo_open_pos_perc = open_pos_perc
        self.memo_i = i
    


def calc_drawdown(net_profit_list, weight_init_cap):
    ary_net_profit = np.array(net_profit_list)
    memo_init_cap = weight_init_cap
    max_cap_test = memo_init_cap
    ary_drawdown = np.empty([len(ary_net_profit)])
    ary_drawdown[:] = 0
    ary_drawdown_perc = np.empty(len(ary_drawdown))
    ary_drawdown_perc[:] = 0
    i_start = 1
    i = i_start
    for _ in itertools.repeat(None, len(ary_net_profit)-i_start):
        if ary_net_profit[i] > ary_net_profit[i - 1] and ary_net_profit[i] + memo_init_cap > max_cap_test:
            max_cap_test = ary_net_profit[i] + memo_init_cap
        if ary_net_profit[i] < ary_net_profit[i - 1] or ary_net_profit[i] + memo_init_cap < max_cap_test:
            ary_drawdown[i] = ary_drawdown[i - 1] + (
                    ary_net_profit[i] - ary_net_profit[i - 1])
            ary_drawdown_perc[i] = (ary_drawdown[i] * 100) / max_cap_test
        elif ary_drawdown[i] >= max_cap_test:
            ary_drawdown[i] = 0
            ary_drawdown_perc[i] = 0
        i += 1
    return ary_drawdown_perc.tolist()


def create_stat_obj(weighted_asset, stat_title, write_to_csv=False):
    '''
    This function takes an input queue with asset, creates a .csv file with every asset dataframe
    and creates an object with performance results
    '''

    # Ticker to csv
    if write_to_csv:
        MyFileManagement.my_df_to_csv(weighted_asset.df, stat_title)
    # Create performance object
    start_date = weighted_asset.df['date'].iloc[0]
    end_date = weighted_asset.df['date'].iloc[-1]
    # Net profit [%]
    net_profit_perc = weighted_asset.df['NetProfit'].iloc[-1]
    net_profit_perc = round(net_profit_perc, 4)
    # Net profit [%]
    buy_hold_perc = weighted_asset.df['Buy&Hold'].iloc[-1]
    buy_hold_perc = round(buy_hold_perc, 4)
    # Max drawdown [%]
    max_drawdown_perc, max_drawdown_date = MyDataFrameManagement.calc_min_value(weighted_asset.df['Drawdown'])
    max_drawdown_perc = round(max_drawdown_perc, 4)
    max_drawdown_date = weighted_asset.df.at[max_drawdown_date, 'date']
    max_drawdown_date = datetime.date(max_drawdown_date.year, max_drawdown_date.month, max_drawdown_date.day)
    # Max buy and hold drawdown [%]
    max_buy_hold_drawdown_perc, _ = MyDataFrameManagement.calc_min_value(weighted_asset.df['Buy&Hold Drawdown'])
    max_buy_hold_drawdown_perc = round(max_buy_hold_drawdown_perc, 4)
    # Percentage of profitable positions, lost positions and total number of positions
    if 'OpenPos' in weighted_asset.df.columns:
        profitable_positions_perc, total_positions, profitable_positions_long_perc, total_positions_long, profitable_positions_short_perc, total_positions_short = \
            MyDataFrameManagement.profitable_pos_perc(weighted_asset.df['OpenPos'], weighted_asset.df['NetProfit'])
        profitable_positions_perc = round(profitable_positions_perc, 3)
        profitable_positions_long_perc = round(profitable_positions_long_perc, 3)
        profitable_positions_short_perc = round(profitable_positions_short_perc, 3)
    else:
        # If asset is fund then no data available for positions
        profitable_positions_perc = None
        total_positions = None
        profitable_positions_long_perc = None
        total_positions_long = None
        profitable_positions_short_perc = None
        total_positions_short = None
    # Create performance object
    perf_obj_name = stat_title
    performance_object = MyPerformanceObject(perf_obj_name,
                                                start_date,
                                                end_date,
                                                net_profit_perc,
                                                max_drawdown_perc,
                                                max_drawdown_date,
                                                profitable_positions_perc,
                                                total_positions,
                                                profitable_positions_long_perc,
                                                total_positions_long,
                                                profitable_positions_short_perc,
                                                total_positions_short,
                                                buy_hold_perc,
                                                max_buy_hold_drawdown_perc)
    
    return performance_object.to_dataframe()
    

@contextmanager
def fund_analizer(asset_fund_list):
    # Net profit
    columns_sum_net_profit = 0
    # Buy&Hold
    columns_sum_buy_hold = 0
    loc_df = pd.DataFrame(index=asset_fund_list[0].df.index)
    loc_df['date'] = asset_fund_list[0].df['date'].values
    for asset_df in asset_fund_list:
        loc_df[asset_df.name + ' ' + 'NetProfit'] = asset_df.df['NetProfit'].values
        columns_sum_net_profit = columns_sum_net_profit + loc_df[asset_df.name + ' ' + 'NetProfit'] * asset_df.weight
    loc_df['NetProfit'] = columns_sum_net_profit
    # Drawdown
    for asset_df in asset_fund_list:
        loc_df[asset_df.name + ' ' + 'Drawdown'] = asset_df.df['Drawdown'].values
    loc_df['Drawdown'] = calc_drawdown(loc_df['NetProfit'], 100.0)  # This considers 100 as initial capital
    for asset_df in asset_fund_list:
        loc_df[asset_df.name + ' ' + 'Buy&Hold'] = asset_df.df['Buy&Hold'].values
        columns_sum_buy_hold = columns_sum_buy_hold + loc_df[asset_df.name + ' ' + 'Buy&Hold'] * asset_df.weight
    loc_df['Buy&Hold'] = columns_sum_buy_hold
    for asset_df in asset_fund_list:
        loc_df[asset_df.name + ' ' + 'Buy&Hold Drawdown'] = calc_drawdown(loc_df[asset_df.name + ' ' + 'Buy&Hold'],
                                                                          100.0)
    loc_df['Buy&Hold Drawdown'] = calc_drawdown(loc_df['Buy&Hold'], 100.0)  # This considers 100 as initial capital
    try:
        yield loc_df
    finally:
        loc_df.iloc[0:0]


