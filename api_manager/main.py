# Author:  Matteo Lorenzato
# Date: 2023-08-26


from flask import Flask, jsonify, request, render_template, redirect, url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import join_room, leave_room, socketio, SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Float
import threading
import time
import json
import requests
from uuid import uuid4
from typing import List, Dict
import os

# Define terminal colors for visual cues
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
END_COLOR = '\033[0m'

# Create a new Flask web server instance
app = Flask(__name__)
app.secret_key = 'PorcoDio!!' # Replace 'your_secret_key' with a real secret key for session handling in Flask

# Configure SocketIO for real time communication
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=600, ping_interval=300)

# Configure the SQLAlchemy database URI for the main application and binding for user data
# Specify SQLite DB path
# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)

db_backup_path = os.path.abspath(os.path.join(parent_dir, "log_db_updater", "db_backup.db"))
users_db_path = os.path.abspath(os.path.join(script_dir, "users.db"))

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_backup_path}'
app.config['SQLALCHEMY_BINDS'] = {
    'users': f'sqlite:///{users_db_path}'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable event system in SQLAlchemy

# Initialize the SQLAlchemy extension with the application instance
db = SQLAlchemy(app)

# Server configuration
SERVER_HOST = 'localhost'
HOST_PORT = 5000
GENERIC_CODE = '0000'  # replace this with your generic code

# User blacklist
USER_BLACK_LIST = []

# Define User model
class User(db.Model):
    __bind_key__ = 'users'
    id = db.Column(db.Integer)
    id_user = db.Column(db.String(36), index=True, unique=True, default=lambda: str(uuid4()), primary_key=True)    
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    tables = db.Column(db.String(500))  # Tables this user can access, comma separated
    ip_address = db.Column(db.String(500))  # User's IP address
    is_active = db.Column(db.Boolean, default=True)  # User's active status
    old_cache = []

    @property
    def webhook(self) -> str:
        '''Get the webhook URL for the user.'''
        return f"http://{SERVER_HOST}:{HOST_PORT}/{self.id_user}/alerts_hub"
    
    def set_password(self, password: str) -> None:
        '''
        Set the hashed password for the user.

        Args:
            password (str): The plain-text password provided by the user.
        '''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        '''
        Verify a password against the stored hash.

        Args:
            password (str): The plain-text password provided for check.

        Returns:
            bool: True if the password matches, False otherwise.
        '''
        return check_password_hash(self.password_hash, password)

    def add_table(self, table: str) -> None:
        '''
        Add a table to the user's accessible tables.

        Args:
            table (str): The name of the table to add.
        '''
        if self.tables:
            self.tables = ','.join([self.tables, table])
        else:
            self.tables = table

    def set_ip(self, ip_address: str) -> None:
        '''
        Set the IP address for the user.

        Args:
            ip_address (str): The IP address to set for the user.
        '''
        self.ip_address = ip_address
    
    def set_is_active(self, instance: bool) -> None:
        '''
        Set the user's active status.

        Args:
            instance (bool): The status to set for the user.
        '''
        self.is_active = instance

    def remove_table(self, table: str) -> None:
        '''
        Remove a table from the user's accessible tables.

        Args:
            table (str): The name of the table to remove.
        '''
        if self.tables and table in self.tables.split(','):
            tables = self.tables.split(',')
            tables.remove(table)
            self.tables = ','.join(tables)





# Create an SQLAlchemy engine instance
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

# Create a MetaData instance and bind it to the engine
metadata = MetaData()
metadata.bind = engine

# Create a sessionmaker and bind it to the engine
Session = sessionmaker(bind=engine)

# Initialize list of tables
tables: List[str] = ["ByBit_spot_ETH_USDT_1h_algo1", "ByBit_spot_BTC_USDT_1h_algo1"]  # populate this with your table names

# Initialize a dictionary to store the cache for each table
cache: Dict[str, List] = {table: [] for table in tables}

# Define LastProcessedDate model
class LastProcessedDate(db.Model):
    __tablename__ = 'last_processed_date'

    table_name = db.Column(db.String, primary_key=True)  # name of the table
    last_processed_date = db.Column(db.Float)  # last processed date for the table

# Define a class for a meta table
class MetaTable:
    def __init__(self, table: str):
        self.table = Table(table, metadata, autoload_with=engine)
        last_processed = LastProcessedDate.query.filter_by(table_name=table).first()
        if last_processed is None:
            # If no entry found, create a new one with the current timestamp
            self.last_processed_date = time.time()
            db.session.add(LastProcessedDate(table_name=table, last_processed_date=self.last_processed_date))
            db.session.commit()
        else:
            # Otherwise, retrieve the last processed date from the database
            self.last_processed_date = last_processed.last_processed_date

    def fetch_new_rows(self):
        '''
        Function to fetch new rows from the table and update the cache.
        '''
        with app.app_context():  # push an application context
            session = Session()
            result = session.query(self.table).filter(text('json_extract(logs, "$.date") > :date')).params(date=self.last_processed_date).all()
            if result:
                self.last_processed_date = max(json.loads(row.logs)['date'] for row in result)
                LastProcessedDate.query.filter_by(table_name=self.table.name).update({LastProcessedDate.last_processed_date: self.last_processed_date})
                db.session.commit()
                cache[self.table.name] = [json.loads(row.logs) for row in result]  # overwrite old data with new one
            session.close()

# Function to create all tables in the database
def create_db():
    with app.app_context():  # push an application context
        db.create_all()  # Create all database tables

# Function to get a list of MetaTable instances for the provided tables
def get_meta_tables(tables: List[str]) -> List[MetaTable]:
    '''
    Get a list of MetaTable instances for the provided tables.

    Args:
    - tables (List[str]): The names of the tables

    Returns:
    - List[MetaTable]: A list of MetaTable instances.
    '''
    with app.app_context():  # push an application context
        return [MetaTable(table) for table in tables]

meta_tables: List[MetaTable] = get_meta_tables(tables)


@socketio.on('connect')
def handle_connect():
    '''
    Event handler for new client connections.
    '''
    user_id = request.args.get('user_id')
    user_saved = User.query.filter_by(id_user=user_id).first()
    if user_id and user_saved and user_saved.is_active:
        join_room(user_id)  # Join the room with the received user ID
        print(GREEN + f"User {user_id} has joined their room." + END_COLOR, flush=True)
        socketio.emit('connected', {'message': 'Connected successfully'}, room=user_id)  # Emit a success message to the client's room
    else:
        print(RED + "User ID not found in cookies or does not match the session. Cannot join room." + END_COLOR, flush=True)
        socketio.emit('connection_error', {'error': 'Invalid user ID'})  # Emit an error message to the client
        socketio.emit('disconnect')  # Emit a disconnect event to disconnect the client


def send_updates(table_name: str, updates: List[Dict]):
    '''
    Function to send updates to a specific table.

    Args:
    - table_name (str): The name of the table
    - updates (List[Dict]): The updates to send
    '''
    with app.app_context():
        users = User.query.filter(User.tables.contains(table_name)).all()
        active_users = [user for user in users if user.is_active]
        print(GREEN+"!!!!!!Try to send alerts to websockets!!!!!!"+END_COLOR, flush=True)
        for user in active_users:
            print(YELLOW+"send:" + user.username + "/" + table_name+END_COLOR, flush=True)
            try:
                print(YELLOW+f"Sending updates to {user.webhook}"+END_COLOR, flush=True)
                socketio.emit('new_updates', {'data': updates}, room=user.id_user)  # Emit the updates to the user's room
                print(updates)
                user.old_cache.extend(updates)
                print(GREEN+f"Updates sent successfully to {user.webhook}"+END_COLOR, flush=True)
            except requests.exceptions.RequestException as e:
                print(RED+f"Failed to send updates to webhook {user.webhook}: {str(e)}"+END_COLOR, flush=True)
            except Exception as e:
                print(RED+f"An error occurred while sending updates to webhook {user.webhook}: {str(e)}"+END_COLOR, flush=True)

def update_cache(metatable: MetaTable):
    '''
    Function to update the cache of a given table.

    Args:
    - metatable (MetaTable): The meta table object
    '''
    old_cache = {table: [] for table in tables}
    while True:
        metatable.fetch_new_rows()
        if old_cache[metatable.table.name] != cache[metatable.table.name]:
            send_updates(metatable.table.name, cache[metatable.table.name])
            old_cache[metatable.table.name] = cache[metatable.table.name].copy()
        time.sleep(0.1)


# Route for the sign up form
@app.route('/sign_up_form', methods=['GET'])
def sign_up_form():
    '''
    This function returns the sign up form template.
    '''
    return render_template('sign_up.html')  # assuming the HTML file is named 'sign_up.html' and is located in the 'templates' folder

# Route for sign in
@app.route('/sign_in', methods=['POST'])
def sign_in():
    '''
    This function handles the sign in route, handles POST request to sign in user.

    Form Data Args:
    - username (str): The username to sign in.
    - password (str): The password to sign in.
    - code (str): The generic code for validation.
    - tables (str): A comma-separated string of table names.
    '''
    username: str = request.form.get('username')
    password: str = request.form.get('password')
    generic_code: str = request.form.get('code')
    tables: List[str] = request.form.get('tables', []).split(',')  # If 'tables' is a comma-separated string

    existing_user = User.query.filter_by(webhook=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400

    user = User.query.filter_by(username=username).first()

    if user and not generic_code:
        user.tables = ','.join(tables)
        db.session.commit()
        return jsonify({'message': 'User updated successfully.'}), 200

    if generic_code and generic_code == GENERIC_CODE:
        if user:
            user.set_password(password)
            user.tables = ','.join(tables)
        else:
            user = User(username=username, tables=','.join(tables))
            user.set_password(password)
            db.session.add(user)
        db.session.commit()
        return render_template('login.html', message= 'User created/updated successfully.')

    return render_template('sign_up.html', message=  'Invalid request.')

# Route for login for websocket
@app.route('/login_for_websocket', methods=['POST'])
def login_for_websocket():
    '''
    This function manages the login route for websocket, handles POST request to authenticate user.

    JSON Args:
    - username (str): The username to authenticate.
    - password (str): The password to authenticate.
    '''
    if request.method == 'POST':
        data = request.get_json()
        username: str = data['username']
        password: str = data['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.id_user not in USER_BLACK_LIST:
            user.set_is_active(True)
            user_ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            user.set_ip(user_ip_address)
            db.session.commit()
            print(GREEN + 'Login successful!', 'success' + user_ip_address + END_COLOR, flush=True)
            return jsonify({'user_id': user.id_user})
        else:
            print(RED + 'Invalid username or password', 'error' + END_COLOR, flush=True)
    return jsonify({'error': 'Invalid request'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    This function manages the login route, handles POST request to authenticate user.

    Form Data Args:
    - username (str): The username to authenticate.
    - password (str): The password to authenticate.
    '''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.id_user not in USER_BLACK_LIST:
            session['user_id'] = user.id_user
            session['tables'] = user.tables
            user.set_is_active(False)
            user_ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            user.set_ip(user_ip_address)
            db.session.commit()
            print(GREEN+'Login successful!', 'success' + user_ip_address+END_COLOR, flush=True)
            return redirect(url_for('account_home', user_id=user.id_user))
        else:
            print(RED+'Invalid username or password', 'error'+END_COLOR, flush=True)
    
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    '''
    This function clears all session data and redirects to the login page.
    '''
    session.clear()
    print(GREEN+'You have been logged out successfully.', 'success'+END_COLOR, flush=True)
    return redirect(url_for('login'))

@app.route('/<string:user_id>/AccountHome', methods=['GET', 'POST'])
def account_home(user_id):
    '''
    This function manages the AccountHome route.

    Args:
    - user_id (str): The user id to validate session and render the account home page.
    '''
    if not session.get('user_id'):
        print(RED+'Access denied', 'error'+END_COLOR, flush=True)
        return redirect(url_for('login'))
    
    if user_id != session.get('user_id'):
        print(RED+'Access denied', 'error'+END_COLOR, flush=True)
        return redirect(url_for('login'))

    return render_template('account_home.html', user_id=user_id)

@app.route('/<string:user_id>/update_account', methods=['GET', 'POST'])
def update_account(user_id):
    '''
    This function manages the update_account route, handles POST request to update account.

    Args:
    - user_id (str): The user id to validate session and update account.

    Form Data Args:
    - new_password (str): The new password to set.
    - new_tables (str): The new tables to set.
    - new_webhook (str): The new webhook to set.
    '''
    if not session.get('user_id') or session.get('user_id') != user_id:
        print(YELLOW+'Please log in to access your account.', 'error'+END_COLOR, flush=True)
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        print(RED+'User not found.', 'error'+END_COLOR, flush=True)
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        new_tables = request.form.get('new_tables')
        new_webhook = request.form.get('new_webhook')

        if new_password:
            user.set_password(new_password)
        if new_tables:
            if isinstance(new_tables, list):
                user.tables = ','.join(new_tables)
            else:
                user.tables = new_tables
        if new_webhook:
            user.webhook = new_webhook

        db.session.commit()

        print(GREEN+'Successfully updated account details.', 'success'+END_COLOR, flush=True)

    return render_template('update_account.html', user_id=user_id)
    

def get_logs(table_name):
    '''
    This function fetches the logs from the cache based on the table name.

    Args:
    - table_name (str): The table name to fetch the logs.
    '''
    if table_name not in cache:
        return jsonify({'error': 'table not found'}), 404
    else:
        return jsonify(cache[table_name])
    
@app.route('/<string:user_id>/alerts_hub', methods=['GET', 'POST'])
def alerts_hub(user_id):
    '''
    This function manages the alerts_hub route, handles POST request to update alerts hub data.

    Args:
    - user_id (str): The user id to validate session and update alerts hub data.
    '''
    if request.method == 'POST':
        new_webhook_data = request.get_json()
        return redirect(url_for('alerts_hub', user_id=user_id))

    if not session.get('user_id') or session.get('user_id') != user_id:
        print(YELLOW+'Please log in to access your account.', 'error'+END_COLOR, flush=True)
        return redirect(url_for('login'))
    
    user = User.query.filter(User.id_user.contains(user_id)).first()
    if not user:
        webhook_data = []
    else:
        webhook_data = user.old_cache

    return render_template('alerts_hub.html', user_id=user_id, webhook_data=webhook_data)



if __name__ == '__main__':
    create_db()

    cache_update_threads = []
    for mt in meta_tables:
        thread = threading.Thread(target=update_cache, args=(mt,))
        thread.daemon = True
        cache_update_threads.append(thread)
        thread.start()
    socketio.run(app, host=SERVER_HOST, port=HOST_PORT)




