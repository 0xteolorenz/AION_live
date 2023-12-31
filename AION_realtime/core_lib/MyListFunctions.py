# Author:  Matteo Lorenzato
# Date: 2023-08-26


#####################################################################################################
#            This module contains a collections of list management functions                        #
#####################################################################################################

#####################################################################################################
#            Import section                                                                         #
#####################################################################################################

#####################################################################################################
#            Options                                                                                #
#####################################################################################################

#####################################################################################################
#            Classes                                                                              #
#####################################################################################################

class MyCandles:
    def __init__(self, list_open, list_close, list_high, list_low):
        self.open = list_open
        self.close = list_close
        self.high = list_high
        self.low = list_low

class MyCandle:
     def __init__(self, candle_open, candle_close, candle_high, candle_low):
        self.open = candle_open
        self.close = candle_close
        self.high = candle_high
        self.low = candle_low

