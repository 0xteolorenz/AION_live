# Author: Leonardo lorenzato
# Date: 2023-08-26


#####################################################################################################
#            This module contains a collections of files management functions                       #
#####################################################################################################

#####################################################################################################
#            Import section                                                                         #
#####################################################################################################
# Config module
import config

import os

import time

#####################################################################################################
#            Classes                                                                              #
#####################################################################################################

class SharedObjToPlot(object):
    '''
    This class creates the object to share between processes
    '''
    def __init__(self, data_ready,
                 ticker_df_list_GLAS, ticker_df_list_FLAS,
                 fund_analyzed_GLAS, fund_analyzed_FLAS,
                 fund_AIonHedge):
        # Data ready status
        self.data_ready = data_ready
        # Asset lists with dataframe
        self.ticker_df_list_GLAS = ticker_df_list_GLAS
        self.ticker_df_list_FLAS = ticker_df_list_FLAS
        self.fund_analyzed_GLAS = fund_analyzed_GLAS
        self.fund_analyzed_FLAS = fund_analyzed_FLAS
        self.fund_AIonHedge = fund_AIonHedge

class JSON_hook(dict):

    def __init__(self, d):
        for key, value in zip(d.keys(), d.values()):
            self.__dict__[key] = value
            self[key] = value

#####################################################################################################
#            Functions                                                                              #
#####################################################################################################

def write_to_csv(df, file_directory, file_name, mode='w', index=False, header=True):
    '''
    This function is used to write a dataframe into csv file
    Warning: using mode='a' append new data each iteration
    '''

    csv_file_path = file_directory + file_name + '.csv'
    while True:
        try: 
            df.to_csv(csv_file_path, mode=mode,  index=index, header=header, encoding='utf-8')
            break 
        except IOError:
            time.sleep(0.5)


def my_df_to_csv(df, file_name):
    '''
    This function is used to create a file with the dataframe of a given asset
    '''
    write_to_csv(df, config.program_results_path + '/', file_name)


def clear_pickle(file):
    '''
    This function clears a pickle file
    '''
    open(file, "w").close()


def get_file_path(file_name, file_extension, directory):
    '''
    Get file path and directory given file name and starting directory
    '''
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            file_path = subdir + os.sep + file
            file_name_to_search = file_name + file_extension
            if file == file_name_to_search:
                return subdir, file_path
    raise FileNotFoundError('No file ' + file_name + file_extension + ' ' + 'in' + ' ' + directory)


def get_directory_path(dir_name, parent_dir):
    '''
    Get direcrory path given directory name and parent directory
    '''
    for subdir, dirs, files in os.walk(parent_dir):
        dir_list = os.listdir(subdir)
        if dir_name in dir_list and not os.path.isfile(os.path.join(subdir, dir_name)):
            return os.path.join(subdir, dir_name)
    raise FileNotFoundError('No directory' + dir_name + ' ' + 'in' + ' ' + parent_dir) 
