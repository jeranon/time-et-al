import os
import json
from datetime import datetime

# Source and destination directories
SOURCE_DIR = "data/job_scans/"
DEST_DIR = "data/job_scans/"

# List all year directories
year_directories = [d for d in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, d))]
print(f"Year directories: {year_directories}")

for year_dir in year_directories:
    file_list = os.listdir(SOURCE_DIR + year_dir)
    print(f"Files in {year_dir} directory: {file_list}")

    for filename in file_list:
        if filename.endswith(".json"):
            print(f"Processing file: {filename}")
            with open(os.path.join(SOURCE_DIR, year_dir, filename), 'r') as file:
                data = json.load(file)

            # For each employee's scans, create a new JSON file in the pay period folder
            for emp_id, scans in data.items():
                for scan in scans:
                    timestamp = scan['job_start']
                    date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                    pay_period_start = filename.split(".")[0]

                    dest_path = os.path.join(DEST_DIR, year_dir, pay_period_start, f"{date}.json")

                    # Ensure directory exists
                    if not os.path.exists(os.path.dirname(dest_path)):
                        os.makedirs(os.path.dirname(dest_path))

                    # If file doesn't exist, create it
                    if not os.path.exists(dest_path):
                        with open(dest_path, 'w') as dest_file:
                            json.dump({}, dest_file)

                    # Append the scan data
                    with open(dest_path, 'r') as dest_file:
                        day_data = json.load(dest_file)

                    if emp_id not in day_data:
                        day_data[emp_id] = []
                    day_data[emp_id].append(scan)

                    # Save the updated data
                    with open(dest_path, 'w') as dest_file:
                        json.dump(day_data, dest_file, indent=4)
                    print(f"Data written to {dest_path}")
