# Author:  Matteo Lorenzato
# Date: 2023-08-26


import subprocess
import threading
import os
import queue

# Get program path
program_path = os.getcwd()

output_queue = queue.Queue()

def run_script(script, show_output):
    process = subprocess.Popen(["python3", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    while True:
        line = process.stdout.readline().strip()
        if show_output and line:
            output_queue.put(line)
        if process.poll() is not None:
            break

def print_output():
    while True:
        line = output_queue.get()
        if line == "TERMINATE":
            break
        print(line)

# List of scripts you want to run
scripts = [
    program_path + os.sep + 'CTMP-master' + os.sep + 'main.py',
    program_path + os.sep + 'AION_realtime' + os.sep + 'main.py',
    program_path + os.sep + 'AION_artificial_dbdata_writer' + os.sep + 'artificial_AIon_db_writer.py',
    program_path + os.sep + 'log_db_updater' + os.sep + 'main.py',
    program_path + os.sep + 'log_db_updater_artificial' + os.sep + 'main.py',
    program_path + os.sep + 'api_manager' + os.sep + 'main.py',
    program_path + os.sep + 'api_manager_artificial' + os.sep + 'main.py'

]

print("Available scripts:")
for idx, script in enumerate(scripts, 1):
    print(f"{idx}. {script}")

selected_indexes = input("Enter the index numbers of the scripts you want to run, separated by spaces (e.g. '3 4'): ")
selected_indexes = [int(i) for i in selected_indexes.split() if 0 < int(i) <= len(scripts)]

output_thread = threading.Thread(target=print_output)
output_thread.start()

threads = []
for idx in selected_indexes:
    show_output = int(input(f"Show output for {scripts[idx-1]}? (1 for yes, 0 for no): ")) == 1
    thread = threading.Thread(target=run_script, args=(scripts[idx-1], show_output))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

output_queue.put("TERMINATE")
output_thread.join()

print("All selected scripts have been run.")
