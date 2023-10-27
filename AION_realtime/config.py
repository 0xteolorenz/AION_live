# Author:  Matteo Lorenzato
# Date: 2023-08-26


# Sys
import sys

# Pandas
import pandas as pd

import os

# platform
from sys import platform

# Clear terminal output
os.system('cls' if os.name == 'nt' else 'clear')

# Get os platform
platform = platform
# Set version revision
version_date = '2023-2-22'
version_name = 'backtest'
program_major_version = '2'
program_minor_version = '1'
# Get program path
program_path = os.getcwd()
# Set program subfolder path
program_lib_path = program_path + os.sep +'lib'
program_algorithms_path = program_path + os.sep +'algorithms'
program_data_path = program_path + os.sep + 'data'
program_params_path = program_path + os.sep + 'params'
program_results_path = program_path + os.sep + 'results'
program_core_lib_path = program_path + os.sep + 'core_lib'
# Set shared data file
program_shared_file = program_results_path + os.sep + 'results_pickle.p'
# System path
sys.path.append(program_path)
sys.path.append(program_lib_path)
sys.path.append(program_core_lib_path)
sys.path.append(program_data_path)
sys.path.append(program_params_path)
sys.path.append(program_results_path)
sys.path.append(program_algorithms_path)
#print(sys.path)

# Pandas display all columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


