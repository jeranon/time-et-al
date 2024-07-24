import os
import py7zr
import datetime

# Set the names of the folders to backup
folders_to_backup = ['data', 'automated']

# Create the backup folder if it doesn't exist
backup_folder = 'backup'
if not os.path.exists(backup_folder):
    os.makedirs(backup_folder)

# Function to backup a folder
def backup_folder_to_archive(folder_name):
    if os.path.exists(archive_name):
        with py7zr.SevenZipFile(archive_name, 'a') as archive:
            folder_list = archive.getnames()
            folder_name_in_archive = f"{folder_name}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
            while folder_name_in_archive in folder_list:
                folder_name_in_archive += "_1"
            archive.writeall(folder_name, arcname=folder_name_in_archive)
    else:
        folder_name_in_archive = f"{folder_name}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        with py7zr.SevenZipFile(archive_name, 'w') as archive:
            archive.writeall(folder_name, arcname=folder_name_in_archive)

# Backup each folder
today = datetime.date.today().strftime('%Y-%m-%d')
archive_name = f'{backup_folder}/{today}.7z'
for folder in folders_to_backup:
    backup_folder_to_archive(folder)

# Check and maintain the backup limit
backup_files = sorted([f for f in os.listdir(backup_folder) if f.endswith('.7z')])
backup_limit = 21

if len(backup_files) > backup_limit:
    oldest_backup = backup_files[0]
    os.remove(os.path.join(backup_folder, oldest_backup))
    print(f"Deleted oldest backup: {oldest_backup}")

print(f'Backup created: {archive_name}')