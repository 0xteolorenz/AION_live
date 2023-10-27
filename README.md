# AION_live
## Overview

AION_live is a comprehensive algorithmic trading platform designed to manage, execute, and log trading decisions in real-time. This suite integrates personal strategies, precise execution, and specific logging to offer an all-in-one solution for modern trading needs.

## Table of Contents
- [Disclaimer](#warning-disclaimer)
- [Directory Structure & Features](#directory-structure--features)
- [Installation](#installation)
- [Parameters Configuration](#parameters-configuration)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## :warning: Disclaimer

This project is in an early stage of development. While we are working to extend its capabilities, cleaning the code and resolving bugs, please use it with caution.

### Development Background
This script, in essence, is the culmination of practical needs rather than an academic exercise. While I have not pursued a formal academic degree in development, the driving force behind this creation is the real-world demand to navigate the complexities of algorithmic trading. I sought to build a tool that can operate independently without leaning on platforms like TradingView or third-party services handling its webhook signals.

**Development Disclaimer**:

- Syntax & Structure: There might be instances of syntax errors or parts of the code that do not adhere to conventional programming paradigms. These inconsistencies arise from a pragmatic approach to problem-solving rather than strictly following established coding standards.

- Code Efficiency: Some sections of the codebase might not be optimized for performance, and there's room for improvements in terms of efficiency and scalability.

- Continuous Improvement: While we strive to enhance and rectify the areas of concern, users are advised to exercise caution, especially when deploying the code in mission-critical environments.

- Collaboration Welcome: If you come across any part of the code that you believe can be improved, be it in terms of syntax, structure, or functionality, your contributions will be immensely valuable. Together, we can shape this into a more robust and efficient tool.

Thank you for your patience, understanding, and support as we work diligently to enhance the features and correct any irregularities present in the project.

## Directory Structure & Features

### AION_artificial_dbdata_writer:
The AION_artificial_dbdata_writer module is responsible for creating and managing artificial data related to market databases. It's especially designed to simulate and inject data periodically, offering a seamless integration with other modules of the AION system.

#### Features:
- **Database Management**: 
    - Automatically creates SQLite databases as per predefined naming conventions.
    - Clears old data from databases every time running the script, ensuring that you always have the latest simulated data.
- **Data Insertion**: 
    - Uses the [CCXT library](https://github.com/ccxt/ccxt), to fetch the latest price from the 'bybit' exchange for given symbols (e.g., ETH/USDT, BTC/USDT).
    - Periodically inserts simulated data, including attributes like open, close prices, take profit levels, stop loss levels, etc., every minute.
- **Multi-threading**: 
    - Utilizes Python's threading capabilities to ensure smooth, uninterrupted data insertion while the main thread remains responsive.
- **Flexible Configuration**:
    -Comes with pre-configured symbols and database names, but can be easily modified for different market symbols or databases. (check [Parameters Configuration](#parametersconfiguration))
    -Calculates and alternates between long and short positions for market simulations.

### CTMP:
CTMP is a Python3 tool designed to fetch OHLCV market data for multiple ticker pairs, storing the data in SQLite databases. This facilitates backtesting, trading algorithm sourcing, and statistical analysis of ticker price/volume. It leverages the CCXT library and other trading libraries for data retrieval from exchanges.

#### Features:
**See documentation**: [CTMP library](https://github.com/leolorenzato/CTMP)

### AION_realtime:
The AION_realtime program is a script designed to monitor database tables for new rows, execute algorithms on these new rows, and update a separate database with the results of the algorithm.

#### Features:
- **Database Monitoring**:
    - AION_realtime continuously tracks [CTMP](https://github.com/leolorenzato/CTMP) SQLite databases for new data rows in financial data tables.
- **Algorithm Execution**:
    - On detecting fresh data, it runs selected trading algorithms (see algorithm example in [Parameters Configuration](#parametersconfiguration)) leveraging parameters sourced from JSON configuration files.
- **Multi-threaded Execution**:
    - Each algorithm with its parameters runs on a separate thread, enabling simultaneous, real-time processing.
- **Results Storage**:
    - After processing, algorithms results are saved in a separate SQLite database.
- **Dynamic Database Management**:
    - Automatic database creation if a required database doesn't exist.

### Log_db_updater:
log_db_updater is a Python script designed to manage and back up logs from databases used in financial algorithm execution, primarily focusing on algorithmic decisions extracted from the AION_realtime system.

#### Features:
- **AION_realtime Integration**: 
    - The script scans through the *AION_realtime* directory, seeking out SQLite databases that represent algorithmic decisions.
- **Order Logs Structure**: 
    - Transforms raw algorithmic decisions into a structured and readable log format that captures details like exchange, market type, order type, price, and more. This structured log provides a clear representation of algorithmic trading decisions.
- **Database Backups**:
    - Automatically creates timestamped backups of the specified logs database and stores them in a backup folder.
- **Table Management**:
    - Post backup, it deletes all tables from the logs database (with specific exceptions) ensuring a lean and efficient database.
- **Dynamic Log Handling**:
    - For each discovered database in the AION_realtime system, it sets up corresponding tables in the logs backup database.
- **Threaded Processing**:
    - Utilizes Python's threading module to process tables in the logs backup database in parallel, ensuring timely data updates.
- **Real-time Monitoring**:
    - Actively monitors database files for any modifications and processes the tables instantly upon detecting a change.
- **Order Log Structure**:
    - The script uses a specific log structure to translate the raw algorithmic decisions into readable logs:
        *date*: Timestamp of the order
        *exchange*: Exchange on which the order is placed
        *market_type*: Type of market (e.g., spot, futures)
        *symbol*: Trading pair or asset symbol
        *side*: Buy/Sell indication
        *order_type*: Type of order (e.g., market, limit)
        *qty_perc*: Percentage of quantity for the order
        *price*: Order price
        *reduceOnly*: Flag to indicate if the order is reduce-only
        *stopPrice*: Stop price for stop orders
        *state*: Current state of the order
        *comment*: Specific orders description
        *algorithm*: Name/ID of the algorithm making the decision
        *timeframe*: Timeframe for the algorithm (e.g., 1H, 4H)

#### Log_db_updater_artificial:
It is a similar variant of *log_db_updater* designed for testing purposes. This script fetches new data rows from *AION_artificial_dbdata_writer* instead of *AION_realtime*. It is used from *Api_manager_artificial*.


### Api_manager:
The API Manager is a Flask-based application that leverages SQLAlchemy for database interactions and SocketIO for real-time communications. Primarily, it's responsible for managing and broadcasting updates read from ***log_db_updater*** database to the registered users in real time.

#### Features:
- **Real-time Data Broadcast**: 
    - Uses SocketIO to broadcast data updates to authenticated users in real-time. (see [AION_client](https://github.com/0xteolorenz/AION_client) for the official user client to manage trading signals from *api_manager* sockets)
- **Secure Authentication System**: 
    - Contains routes for signing up, logging in, and updating user details for web account managing. Passwords are hashed using werkzeug.security.
- **Data Management with SQLAlchemy**: 
    - Uses SQLAlchemy for database interactions, both for user-related data and caching data updates.
- **Webhook System**: 
    - Each user has an associated webhook URL.
- **SocketIO Event Handlers**:
    - Handles client connections and broadcasts updates to specific rooms (each user has a dedicated room).
- **Routes**:
    - *Authentication*:
        - /sign_up_form: Renders the sign-up form.
        - /sign_in: Handles the sign-up process and updates users if necessary.
        - /login_for_websocket: Handles websocket login based on provided credentials.
        - /login: Renders the login page and handles authentication.
        - /logout: Logs out the user.
    - *User Management*:
        - /<string:user_id>/AccountHome: Renders the account home page for authenticated users.
        - /<string:user_id>/update_account: Provides functionality for users to update their account details
- **Configuration parameters**: 
    - see in [Parameters Configuration](#parametersconfiguration) *api_manager* section.

#### Api_manager_artificial:
It is a similar variant of *api_manager* designed for testing purposes. This manager fetches new data rows from *log_db_updater_artificial* and interfaces with *AION_artificial_dbdata_writer* instead of *AION_realtime* and *log_db_updater*.

#### :warning: Disclaimer
The code provided contains hardcoded credentials and secrets for demonstration purposes only. It is STRONGLY recommended that you DO NOT deploy or use this code in a production environment or any public-facing server.

**Recommended Usage**:

- *Localhost ONLY*: Please ensure you use this code exclusively in a local development environment.
- *Replace Hardcoded Secrets*: Before considering any form of deployment, make sure to replace all hardcoded credentials and secrets with a secure secrets management system or environment-specific configurations.
- *Add Proper Security Measures*: Before any deployment or external exposure, implement appropriate security measures, including authentication, authorization, and data protection.

**Risks of Ignoring This Disclaimer**:

- Unauthorized access to sensitive data or systems.
- Potential breaches of data privacy regulations.
- Exposing critical infrastructure to vulnerabilities and threats.
- Always prioritize security best practices when working with sensitive data and systems. This code is provided "as is" without any guarantees or assurances. Use at your own risk.


## Installation
To use *AION_live* follow these steps:

1. Clone the repository to your local machine:
    ```bash
    git clone https://github.com/0xteolorenz/AION_live.git
    ```

2. Navigate to the repository directory:
    ```bash
    cd AION_live/AION_live
    ```

4. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

5. Configure all scripts paramaters as needed (see [Parameters Configuration](#parametersconfiguration)).

6. Give chmod permission to the specific .sh file in base of your OS. (NOT NEEDED FOR WINDOWS OS)
   Example:
    ```bash
    chmod +x ./AION_runner_linux_test.sh
    ```

7. To start the project:
   Linux:
    ```bash
    ./AION_runner_linux_test.sh
    ```
   MacOs:
   ```bash
    ./AION_runner_macOS_test.sh
    ```
   Windows:
   ```bash
    ./AION_runner_windows_test.bat
    ```

## Parameters Configuration
Configure the program as follows:

### 1.CTMP:
1. Go to params folder inside CTMP directory.
2. Select the exchange folders you want to use to download price data.
3. Check if the *exhange.json* file inside the exchange folders exist then verify if *enable* paramenter is setted to True.
Example:
    ```json
    {   
        "name": "ByBit",
        "enable": true
    }
    ```
4. Now select *tickers* folder inside the exchange folder and add every ticker json file for each ticker you want to download. The json files name have to follow this structure: **TICKERNAME_TIMEFRAME_MARKETTYPE.json**.
Example:
    ```json
    {   
        "asset": "BTC",
        "asset_ref": "USDT",
        "ticker_interval": "1h",
        "asset_type": "spot",
        "start_date": 
            {
                "day": 1,
                "month": 1,
                "year": 2020
            },
        "end_date": 
            {
                "day": 1,
                "month": 1,
                "year": 2030
            }
    }   
    ```
### 2. AION_realtime:
1. Go to params folder inside AION_realtime directory.
2. Modify the *main.py* in base of which algorithm you want to run as in example:
    ```python
    from algorithms.algo1 import algo1

    # Mapping of algorithm names to their classes
    ALGO_CLASS_MAP = {
        'algo1': algo1
    }
    ```
    Remeber that each algorithm must have its params .json file in *params/funds/asset* folder and the algorithm python script in *algorithms* folder.
    Every keys inside *ALGO_CLASS_MAP* must have the same name of the algorithm folder where there are the tickers parameters json files.
3. The base structure of the params .json file must be this:
   ```json
      {   
        "algorithm_name": "algo1",
        "asset": "BTC",
        "asset_ref": "USDT",
        "ticker_interval": "1h",
        "exchange": "ByBit",
        "type": "spot",
        "tr_fees_oc": 0.0, #only for backtest
        "tr_fees_tp": 0.0, #only for backtest
        "funding_fees": 0.0, #only for backtest
        "parameters": 
            {
                "fund_weight": 
                    {   
                        "value": 1.0,
                        "set_range_percent": false,
                        "subsets": [],
                        "range_perc": null,
                        "min_value": null, 
                        "max_value": null
                    },
                "price_filter": 
                    {   
                        "value": "close",
                        "set_range_percent": null,
                        "subsets": [],
                        "range_perc": null,
                        "min_value": null, 
                        "max_value": null
                    },
                ...
                "parameter1": 
                    {   
                        "value": #default parameter value,
                        "set_range_percent": #range of variation for backtest (null for AION_live),
                        "subsets": #list of subsets groups for backtest ([] for AION_live),
                        "range_perc": #range of variation for backtest (null for AION_live),
                        "min_value": #min param value for backtest (null for AION_live), 
                        "max_value": #max parma value for backtest (null for AION_live)
                    },
                ...
                ...
                ...
            }
        }     
    ```
4. The base structure for creating a algorithm for AION_live is this:
    ```python
        # BaseAlgo.py

        import numpy as np
        import pandas as pd
        import time
        from core_lib import BaseFunctions, BaseIndicators

        class BaseAlgo:
            def __init__(self, df, general_data, params):
                self.params = params
                self.general = general_data
                self.init_df = df.copy()
                self.df = df.copy()

                if not 'date' in df.columns:
                    raise KeyError('Date column named date expected in input dataframe')

                self.i = 0
                self.build()

            def build(self):
                # Define core attributes and indicators
                self.coreAttribute1 = BaseFunctions.SomeFunction(self.params.some_parameter)
                self.coreIndicator1 = BaseIndicators.SomeIndicator()

            def update(self):
                start_time = time.time()
                i = self.i
                # Update and calculation logic
                value1 = self.coreAttribute1.update(self.df['some_column'][i])
                condition1 = self.coreIndicator1.check(value1)

                self.i += 1

                # Performance logging
                exe_time = time.time() - start_time

                # Calc execution averagime time
                self.avg_exe_time += (time.time() - start_time) / self.i

            def update_dataframe(self):
                # Save data and results into the dataframe
                pass

            def to_dataframe(self):
                self.update_dataframe()
                return self.df

            def reinit(self):
                self.__init__(self.init_df, self.general, self.params)

            def update_all(self):
                for _ in range(len(self.df)):
                    self.update()

            def reinit_df(self, df):
                self.init_df = df
                self.reinit()

            def reinit_params(self, params):
                self.params = params
                self.reinit()

            def reinit_general_data(self, general_data):
                self.general = general_data
                self.reinit()

            @staticmethod
            def some_utility_function():
                pass
    ```
    It's important to note that the *BaseAlgo* structure provided here is a generalized adaptation and simplification of a more intricate algorithm that we've developed. While this representation captures the core essence and structure of our original algorithm, there are areas that can be enhanced, streamlined, or better structured.

    This rendition is not necessarily the most efficient or intuitive. However, it's designed to strike a balance between simplicity and functionality. For those looking for a more exhaustive and potentially optimized structure, we recommend referring to the algo1.py script.

    The **algo1.py** script offers a more comprehensive structure, ideal for users keen on delving deeper into the nuances of algorithm development and optimization. The provided algorithm is an exemplification of a two EMAs crossover/crossunder trading strategy. Specifically, when the EMA_fast crosses over the EMA_slow, it triggers a market-long position, which is then closed when the EMA_fast crosses under the EMA_slow. We always welcome contributions and suggestions to enhance the code's structure and functionality.

    Your comprehension of our approach and the subsequent direction for users on how to navigate our provided structure is appreciated. If there are any further details or intricacies, please do not hesitate to share.


### 3. log_db_updater:
It hasn't got any parameters to set up. It creates automatically every table for each algorithm running on *AION_realtime*.

### 4. api_manager:
1. Modify the sever host, you can decide where running the Flask app:
    ```python
    # Server configuration
    SERVER_HOST = 'localhost'
    HOST_PORT = 5000
    GENERIC_CODE = '0000'  # replace this with your generic code
    ```
2. Decide wich logs tables you want to elaborate from *logs_db_updater* database:
    ```python
    # Initialize list of tables
    tables: List[str] = ["ByBit_spot_BTC_USDT_1h_algo1",
     "ByBit_spot_ETH_USDT_1h_algo1",
     ... # populate this with your table names
    ]
    ```
3. Once the script is running, you'll need to sign up on the server host. To do this, navigate to **localhost:5000/sign_up_form**. From there, you can choose which algo tables you wish to receive through the AION_client.


## Contributing
Contributions to this project are welcome. If you'd like to contribute, please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your feature or bug fix: 
    ```bash
    git checkout -b feature/your-feature-name
    ```
3. Commit your changes: 
    ```bash
    git commit -m 'Add some feature'
    ```
4. Push to your branch: 
    ```bash
    git push origin feature/your-feature-name
    ```
5. Submit a pull request to the main repository.

## Acknowledgments

A heartfelt thank you to the following:

- **CCXT Library Creators**: This project owes a great deal to the [CCXT Library](https://github.com/ccxt/ccxt), an exceptional piece of work that has significantly streamlined the process of interfacing with various cryptocurrency exchanges. Their dedication to maintaining and enhancing the library is commendable and has been invaluable to the development of AION_live.

- **[leolorenzato](https://github.com/leolorenzato)**: Special recognition goes to my coding partner, who developed the [CTMP script](https://github.com/leolorenzato/CTMP) and contributed in **AION_backtest** project. Your expertise and dedication have been instrumental in shaping the functionality and efficiency of this project.

I'd like to extend my gratitude to everyone who has offered feedback, suggestions, or code improvements. Your contributions, big or small, have made a positive impact and helped make AION_live what it is today.


## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

