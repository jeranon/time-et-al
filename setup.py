import os
import json

directories = [
    "data",
    "data/config",
    "data/logs",
    "data/reference",
    "data/time_scans"
]

files_with_initial_data = {
    "data/config/config.json": {
        "pay_period": {
            "start_date": "2023-01-01",
            "duration_days": 14
        },
        "work_day": {
            "start_hour": 8
        }
    },
    "data/reference/server_ip.json": {
        "ip": "0.0.0.0"
    },
    "data/reference/employees.json": {},
    "data/reference/clients.json": [],
    "data/reference/transaction_counter.txt": "0"
}

for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

for file_path, initial_data in files_with_initial_data.items():
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            if isinstance(initial_data, dict) or isinstance(initial_data, list):
                json.dump(initial_data, file, indent=4)
            else:
                file.write(initial_data)
        print(f"Created file: {file_path} with initial data")

print("Setup completed. Required directories and files have been created.")
