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

def extract_jobs_with_total_hours(data):
    jobs_dict = defaultdict(lambda: {'total_hours': 0, 'complete': True})
    
    for _, records in data.items():
        for record in records:
            job_num = record.get("job_num")
            
            # Normalize the job number to upper case
            if job_num:
                job_num = job_num.upper()
                
            total_time = record.get("total_time")
            
            # Check if job number exists
            if job_num:
                if total_time is not None:
                    # Convert total time from seconds to hours and aggregate
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
    
def save_to_csv(jobs_dict, csv_path):
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the headers
        writer.writerow(['Job', 'Hours', 'Status'])

        for job, job_info in jobs_dict.items():
            hours = job_info['total_hours']
            status = 'Complete' if job_info['complete'] else 'Incomplete'
            writer.writerow([job, hours, status])
    
def load_employee_names():
    with open(EMPLOYEE_FILE_PATH, 'r') as file:
        employees = json.load(file)
    return {emp_id: details["name"] for emp_id, details in employees.items()}

def generate_human_readable_report(data, report_path):
    employee_names = load_employee_names()

    # First pass: Generate the report lines without any padding
    virtual_report = []
    for employee_id, records in sorted(data.items(), key=lambda x: employee_names.get(x[0], "Unknown")):
        for record in records:
            if 'job_num' in record and record['job_num'] is not None:
                record['job_num'] = record['job_num'].upper()

        valid_records = [rec for rec in records if rec.get("job_num")]
        total_hours_employee = sum(record.get("total_time", 0) for record in valid_records) / 3600
        employee_name = employee_names.get(employee_id, "Unknown")
        employee_line = f"{employee_name} ({employee_id}) Total job-hours: {total_hours_employee:.2f} hours"
        virtual_report.append(employee_line)

        for record in valid_records:
            job_num = record.get("job_num", "").upper()
            start_time = record.get("job_start")
            end_time = record.get("job_end")
            total_hours = record.get("total_time")

            if total_hours is not None:
                job_line = f"    {job_num} : {start_time} to {end_time} - {total_hours / 3600:.2f} hours"
            else:
                # Handling incomplete data where end time or total hours is missing
                job_line = f"    {job_num} : {start_time} to [No Sign-Off] - Incomplete Data"
            
            virtual_report.append(job_line)
            
    # Determine the longest line from the virtual report
    longest_line_length = max(len(line) for line in virtual_report)

    # Second pass: Generate the report with padding
    report_lines = []
    for line in virtual_report:
        if "Total job-hours" in line:
            # Apply padding for 'Total job-hours' lines
            name_part, hours_part = line.split("Total job-hours:")
            padding_needed = longest_line_length - len(line) + len(hours_part)
            padded_line = name_part + " " * padding_needed + "Total job-hours:" + hours_part
            report_lines.append(padded_line)
        else:
            # Preserve other lines as they are, including incomplete data lines
            report_lines.append(line)

    # Write to report file
    with open(report_path, 'w') as report_file:
        report_file.writelines(line + "\n" for line in report_lines)

def process_files(actions_needed, emailed_data):
    for file_path in actions_needed['process']:
        print(f"Processing file: {file_path}")
        report_folder = AUTOMATED_DIR / "emailed" / file_path.stem
        report_folder.mkdir(parents=True, exist_ok=True)

        # Copy the original JSON file to the report folder
        shutil.copy(file_path, report_folder)

        # Load JSON data and generate reports
        with open(file_path, 'r') as file:
            data = json.load(file)

        jobs = extract_jobs_with_total_hours(data)
        csv_file_path = report_folder / (file_path.stem + ".csv")
        save_to_csv(jobs, csv_file_path)

        report_file_path = report_folder / (file_path.stem + " - Report.txt")
        generate_human_readable_report(data, report_file_path)

        # Ensure the entry exists and then update the 'processed' flag
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
