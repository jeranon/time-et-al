import os
import json

def setup_files_and_directories():
    # Define the required directories and their paths
    base_dir = "data"
    reference_dir = os.path.join(base_dir, "reference")
    logs_dir = os.path.join(base_dir, "logs")
    time_scans_dir = os.path.join(base_dir, "time_scans")
    time_scans_2023_dir = os.path.join(time_scans_dir, "2023")

    # List of all directories to ensure they exist
    required_dirs = [base_dir, reference_dir, logs_dir, time_scans_dir, time_scans_2023_dir, os.path.join(base_dir, "config")]

    # Create directories if they don't exist
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Define required JSON files and their default content
    required_files = {
        os.path.join(reference_dir, "employees.json"): [],
        os.path.join(reference_dir, "server_ip.json"): {"ip": ""},
        os.path.join(reference_dir, "clients.json"): [],
        os.path.join(base_dir, "config", "config.json"): {
            "paths": {
                "base_dir": "data",
                "reference_dir": "data/reference",
                "logs_dir": "data/logs",
                "time_scans_dir": "data/time_scans"
            },
            "pay_period_start_date": "2023-09-17"
        }
    }

    # Create JSON files with default content if they don't exist
    for file_path, default_content in required_files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                json.dump(default_content, file, indent=4)

if __name__ == "__main__":
    setup_files_and_directories()
    print("Setup completed. Required directories and files have been created.")
