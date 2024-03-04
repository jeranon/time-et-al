from cryptography.fernet import Fernet
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
import csv
from collections import defaultdict
from pathlib import Path
import shutil
from datetime import datetime, timedelta

# Assuming the structure of the script is in the root directory
ROOT_DIR = Path(__file__).parent
AUTOMATED_DIR = ROOT_DIR / "automated"
JOB_SCANS_DIR = ROOT_DIR / "data/job_scans"
EMAILED_FILE_PATH = AUTOMATED_DIR / "job_data_emailed.json"
EMPLOYEE_FILE_PATH = ROOT_DIR / "data/reference/employees.json"

def decrypt_credentials():
    KEY_PATH = AUTOMATED_DIR / "key.bin"
    CREDENTIALS_ENCRYPTED_PATH = AUTOMATED_DIR / "production_testing_credentials.encrypted"

    with open(KEY_PATH, "rb") as key_file:
        key_data = key_file.read()
        salt = key_data[:16]
        encoded_key = key_data[16:]
    cipher = Fernet(encoded_key)

    with open(CREDENTIALS_ENCRYPTED_PATH, "rb") as encrypted_file:
        encrypted_file_contents = encrypted_file.read()
        encrypted_data = encrypted_file_contents[len(salt):]  # Exclude the salt from the encrypted data

    decrypted_data = cipher.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode('utf-8'))

def load_emailed_data():
    # Load the job_data_emailed.json or initialize it
    if EMAILED_FILE_PATH.exists():
        with open(EMAILED_FILE_PATH, 'r') as file:
            return json.load(file)
    else:
        return {}
        
def load_shift_data():
    SHIFT_FILE_PATH = ROOT_DIR / "data/reference/shifts.json"
    with open(SHIFT_FILE_PATH, 'r') as file:
        return json.load(file)

def save_emailed_data(emailed_data):
    # Save the updated job_data_emailed.json
    with open(EMAILED_FILE_PATH, 'w') as file:
        json.dump(emailed_data, file, indent=2)

def find_files_needing_action(emailed_data):
    actions_needed = {'process': [], 'email': []}
    for json_file in JOB_SCANS_DIR.rglob('*.json'):
        file_date_str = json_file.stem
        file_status = emailed_data.get(file_date_str, {'processed': False, 'emailed': False})

        if not file_status['processed']:
            actions_needed['process'].append(json_file)
        if not file_status['emailed']:
            actions_needed['email'].append(json_file)

    return actions_needed

def send_email(subject, body, file_paths, credentials):
    gmail_user = credentials["username"]
    gmail_password = credentials["password"]
    to_addresses = credentials["to"].split(',')
    cc_addresses = credentials.get("cc", "").split(',') if credentials.get("cc") else []
    bcc_addresses = credentials.get("bcc", "").split(',') if credentials.get("bcc") else []

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = ', '.join(to_addresses)
    msg['CC'] = ', '.join(cc_addresses)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    for file_path in file_paths:
        with open(file_path, "rb") as attachment_file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={Path(file_path).name}")
        msg.attach(part)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_addresses + cc_addresses + bcc_addresses, msg.as_string())
        server.close()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def extract_jobs_with_total_hours(data, shifts):
    jobs_dict = defaultdict(lambda: {'total_hours': 0, 'complete': True})

    for employee_id, records in data.items():
        for record in records:
            job_num = record.get("job_num")
            if job_num:
                job_num = job_num.upper()
                start_time = record.get("job_start")
                end_time = record.get("job_end")
                total_time = record.get("total_time", 0)
                shift_name = record.get("shift_name", "unknown")  # Get shift name from record

                if total_time is not None:
                    # Use shift_name to get lunch times
                    lunch_start = shifts[shift_name]['lunch']['start']
                    lunch_end = shifts[shift_name]['lunch']['end']
                    lunch_start_sec = time_to_seconds(lunch_start)
                    lunch_end_sec = time_to_seconds(lunch_end)
                    
                    # Check for overlap with lunch period and adjust total time
                    start_sec = time_to_seconds(start_time.split(" ")[1])
                    end_sec = time_to_seconds(end_time.split(" ")[1])
                    if start_sec < lunch_end_sec and end_sec > lunch_start_sec:
                        lunch_duration = min(end_sec, lunch_end_sec) - max(start_sec, lunch_start_sec)
                        total_time -= lunch_duration
    
                    jobs_dict[job_num]['total_hours'] += total_time / 3600
                else:
                    # Mark job as incomplete
                    jobs_dict[job_num]['complete'] = False

    # Round to the nearest quarter hour and handle values less than 0.25
    for job_num, job_info in jobs_dict.items():
        total_hours = job_info['total_hours']
        if 0 < total_hours < 0.25:
            jobs_dict[job_num]['total_hours'] = 0.25
        else:
            jobs_dict[job_num]['total_hours'] = round(total_hours * 4) / 4

    return dict(sorted(jobs_dict.items()))

# Helper function to convert time string to seconds since midnight
def time_to_seconds(datetime_str):
    # Extract the time part from the datetime string
    time_part = datetime_str.split(' ')[-1]  # Get the last part after splitting by space
    parts = time_part.split(':')
    
    # Assign hours, minutes, and seconds (defaulting seconds to 0 if not provided)
    h, m, s = map(int, parts + ['0']*(3-len(parts)))

    return h * 3600 + m * 60 + s
    
def save_to_csv(jobs_dict, csv_path):
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the headers
        writer.writerow(['Job', 'Hours', 'Status'])

        for job, job_info in jobs_dict.items():
            hours = job_info['total_hours']
            status = 'Complete' if job_info['complete'] else 'Incomplete'
            writer.writerow([job, hours, status])
    
def load_employees():
    with open(EMPLOYEE_FILE_PATH, 'r') as file:
        return json.load(file)

def generate_human_readable_report(data, report_path, employees, shifts):
    # Group employees by shift
    shift_groups = defaultdict(list)
    for employee_id, records in data.items():
        for record in records:
            shift_name = record.get("shift_name", "unknown")
            shift_groups[shift_name].append((employee_id, record))

    # First pass: Generate the virtual report lines
    virtual_report = []
    for shift, employee_records in shift_groups.items():
        virtual_report.append(f"Shift: {shift}")
        for employee_id, record in employee_records:
            virtual_report.extend(virtual_report_lines_for_employee(record, employee_id, employees, shifts))
        virtual_report.append("")
        
    longest_line_length = max(len(line) for line in virtual_report)

    # Second pass: Normalize line lengths
    report_lines = []
    for line in virtual_report:
        if "Total job-hours:" in line:
            name_part, hours_part = line.rsplit("Total job-hours:", 1)
            padding_needed = longest_line_length - len(line) + len(hours_part)
            line = name_part + " " * padding_needed + "Total job-hours:" + hours_part
        report_lines.append(line)

    # Write to report file
    with open(report_path, 'w') as report_file:
        for line in report_lines:
            report_file.write(line + "\n")

def virtual_report_lines_for_employee(record, employee_id, employees, shifts):
    virtual_report = []
    employee_name = employees[employee_id]['name']  # Retrieve employee name from employees data
    shift_name = record.get("shift_name", "unknown")
    lunch_start = shifts[shift_name]['lunch']['start'] + ":00"
    lunch_end = shifts[shift_name]['lunch']['end'] + ":00"

    total_hours_employee = 0
    job_num = record.get("job_num", "").upper()
    start_time = record.get("job_start")
    end_time = record.get("job_end")
    total_hours = record.get("total_time", 0)

    # Format lunch times with the date from the job start time
    date_str = start_time.split()[0]
    formatted_lunch_start = f"{date_str} {lunch_start}"
    formatted_lunch_end = f"{date_str} {lunch_end}"

    # Splitting the job around the lunch break
    if overlaps_lunch(start_time, end_time, formatted_lunch_start, formatted_lunch_end):
        pre_lunch_hours, post_lunch_hours = split_job_hours(start_time, end_time, formatted_lunch_start, formatted_lunch_end)
        total_hours_employee += pre_lunch_hours + post_lunch_hours

        virtual_report.append(f"    {job_num} : {start_time} to {formatted_lunch_start} - {pre_lunch_hours:.2f} hours")
        virtual_report.append(f"    {job_num} : {formatted_lunch_end} to {end_time} - {post_lunch_hours:.2f} hours")
    else:
        total_hours_employee += total_hours / 3600
        if total_hours is not None:
            job_line = f"    {job_num} : {start_time} to {end_time} - {total_hours / 3600:.2f} hours"
            virtual_report.append(job_line)

    employee_line = f"{employee_name} ({employee_id}) Total job-hours: {total_hours_employee:.2f} hours"
    virtual_report.insert(0, employee_line)  # Insert at the beginning of the list
    
    return virtual_report

def overlaps_lunch(start_time, end_time, lunch_start, lunch_end):
    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    lunch_start_dt = datetime.strptime(lunch_start, "%Y-%m-%d %H:%M:%S")
    lunch_end_dt = datetime.strptime(lunch_end, "%Y-%m-%d %H:%M:%S")

    # Adjust for overnight shifts
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    if lunch_end_dt < lunch_start_dt:
        lunch_end_dt += timedelta(days=1)

    return max(start_dt, lunch_start_dt) < min(end_dt, lunch_end_dt)

def split_job_hours(start_time, end_time, pre_lunch_end, post_lunch_start):
    # Convert time strings to datetime objects
    fmt = "%Y-%m-%d %H:%M:%S"
    start_dt = datetime.strptime(start_time, fmt)
    end_dt = datetime.strptime(end_time, fmt)
    lunch_start_dt = datetime.strptime(pre_lunch_end, fmt)
    lunch_end_dt = datetime.strptime(post_lunch_start, fmt)

    # Adjust for overnight shifts
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    if lunch_end_dt < lunch_start_dt:
        lunch_end_dt += timedelta(days=1)

    # Calculate pre-lunch and post-lunch durations in seconds
    pre_lunch_duration = (lunch_start_dt - start_dt).total_seconds()
    post_lunch_duration = (end_dt - lunch_end_dt).total_seconds()

    # Convert seconds to hours
    pre_lunch_hours = pre_lunch_duration / 3600
    post_lunch_hours = post_lunch_duration / 3600

    return pre_lunch_hours, post_lunch_hours

def process_files(actions_needed, emailed_data):
    # Load shift data
    shifts = load_shift_data()

    for file_path in actions_needed['process']:
        print(f"Processing file: {file_path}")
        report_folder = AUTOMATED_DIR / "emailed" / file_path.stem
        report_folder.mkdir(parents=True, exist_ok=True)

        # Copy the original JSON file to the report folder
        shutil.copy(file_path, report_folder)

        # Load JSON data
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Generate reports with shift data
        jobs = extract_jobs_with_total_hours(data, shifts)
        csv_file_path = report_folder / (file_path.stem + ".csv")
        save_to_csv(jobs, csv_file_path)

        # Since we need employee names for the report, load employee data
        employees = load_employees()
        report_file_path = report_folder / (file_path.stem + " - Report.txt")
        generate_human_readable_report(data, report_file_path, employees, shifts)

        # Update the 'processed' flag
        file_date_str = file_path.stem
        emailed_data.setdefault(file_date_str, {'processed': False, 'emailed': False})
        emailed_data[file_date_str]['processed'] = True

    for file_path in actions_needed['email']:
        print(f"Emailing file: {file_path}")
        credentials = decrypt_credentials()
        subject = f"Report for {file_path.stem}"
        body = "Please find attached the report."
        file_paths = [file_path, AUTOMATED_DIR / "emailed" / file_path.stem / (file_path.stem + ".csv"),
                      AUTOMATED_DIR / "emailed" / file_path.stem / (file_path.stem + " - Report.txt")]
        send_email(subject, body, file_paths, credentials)
        emailed_data[file_path.stem]['emailed'] = True

def main():
    emailed_data = load_emailed_data()
    actions_needed = find_files_needing_action(emailed_data)
    process_files(actions_needed, emailed_data)
    save_emailed_data(emailed_data)

if __name__ == "__main__":
    main()
