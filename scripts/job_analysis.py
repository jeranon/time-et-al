import os
import json
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
import csv

# ANSI Escape Codes for colors
LIGHT_GREEN = "\033[92m"
LIGHT_RED = "\033[91m"
LIGHT_BLUE = "\033[94m"
RESET_COLOR = "\033[0m"

def select_file():
    """Open a file dialog and return the selected file's path."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(title="Select the job_tracking.json file",
                                           filetypes=[("JSON files", "*.json")])
    return file_path

def extract_jobs_with_total_hours(file_path):
    """Extract all individual jobs with their total hours aggregated across all workers."""

    # Load the job tracking data from the selected file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
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
                
    # Sort the jobs dictionary by job number (alphabetically)
    sorted_jobs = dict(sorted(jobs_dict.items()))
    
    return sorted_jobs

def save_to_csv(jobs_dict, file_path):
    """Save the job totals to a CSV file."""
    
    # Deduce the CSV filename from the input file path
    csv_filename = os.path.splitext(os.path.basename(file_path))[0] + ' - Job Totals.csv'
    csv_path = os.path.join(os.path.dirname(file_path), csv_filename)
    
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the headers
        writer.writerow(['Job', 'Hours', 'Status'])

        for job, job_info in jobs_dict.items():
            hours = job_info['total_hours']
            status = 'Complete' if job_info['complete'] else 'Incomplete'
            writer.writerow([f'="{job}"', hours, status])

    return csv_path

def load_employee_names():
    """Load employee names from employees.json."""
    EMPLOYEE_FILE_PATH = os.path.join("data", "reference", "employees.json")
    with open(EMPLOYEE_FILE_PATH, 'r') as file:
        employees = json.load(file)
    return {emp_id: details["name"] for emp_id, details in employees.items()}

def generate_human_readable_report(file_path):
    """Generate a human readable report of the job tracking data."""
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Load employee names
    employee_names = load_employee_names()

    # Find the maximum length of job numbers for padding
    max_job_length = max(len(job) for employee_records in data.values() for job in [record["job_num"] for record in employee_records if record["job_num"]])

    # First pass: Generate the report lines without any padding
    virtual_report = []
    for employee_id, records in sorted(data.items(), key=lambda x: employee_names.get(x[0], "Unknown")):
        # Normalize job numbers to upper case in the records first
        for record in records:
            if 'job_num' in record:
                record['job_num'] = record['job_num'].upper()
                
        # Now proceed with the rest of your logic
        valid_records = [rec for rec in records if rec.get("job_num")]
        total_hours_employee = sum(record.get("total_time", 0) for record in valid_records) / 3600
        employee_name = employee_names.get(employee_id, "Unknown")
        employee_line = f"{employee_name} ({employee_id}) Total job-hours: {total_hours_employee:.2f} hours"
        virtual_report.append(employee_line)
        
        for record in valid_records:
            job_num = record.get("job_num")
            start_time = record.get("job_start")
            end_time = record.get("job_end")
            total_hours = record.get("total_time")

            if total_hours is not None:
                total_hours = total_hours / 3600
                job_line = f"    {job_num} : {start_time} to {end_time} - {total_hours:.2f} hours"
            else:
                job_line = f"    {job_num} : Incomplete data (Missing end time or total time)"
            
            virtual_report.append(job_line)
        virtual_report.append("")

    # Determine the longest line from the virtual report
    longest_line_length = max(len(line) for line in virtual_report)

    # Second pass: Generate the report with padding
    report_lines = []
    for employee_id, records in sorted(data.items(), key=lambda x: employee_names.get(x[0], "Unknown")):
        valid_records = [rec for rec in records if rec.get("job_num")]
        total_hours_employee = sum(record.get("total_time", 0) for record in valid_records) / 3600
        employee_name = employee_names.get(employee_id, "Unknown")
        total_hours_text = f"Total job-hours: {total_hours_employee:.2f} hours"
        padding_length = longest_line_length - len(employee_name) - len(f" ({employee_id}) ") - len(total_hours_text) + 1
        employee_line = f"{employee_name} ({employee_id})" + " " * padding_length + total_hours_text
        report_lines.append(employee_line)
        
        for record in valid_records:
            job_num = record.get("job_num")
            start_time = record.get("job_start")
            end_time = record.get("job_end")
            total_hours = record.get("total_time")

            if total_hours is not None:
                total_hours = total_hours / 3600
                padding_length = max_job_length - len(job_num)
                job_line = f"    {job_num}" + " " * padding_length + f" : {start_time} to {end_time} - {total_hours:.2f} hours"
            else:
                job_line = f"    {job_num} : Incomplete data (Missing end time or total time)"
            
            report_lines.append(job_line)
        report_lines.append("")

    # Create report file
    report_filename = os.path.splitext(os.path.basename(file_path))[0] + ' - Human Readable Report.txt'
    report_path = os.path.join(os.path.dirname(file_path), report_filename)
    with open(report_path, 'w') as report_file:
        report_file.writelines(line + "\n" for line in report_lines)

    return LIGHT_GREEN + f"{report_path}" + RESET_COLOR

def display_job_analysis_menu(message=""):
    """
    Display the job analysis menu.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(message)  # Display the message at the top
    print(LIGHT_BLUE + "\nJob Analysis Menu" + RESET_COLOR)
    print(LIGHT_BLUE + "----------------------\n" + RESET_COLOR)
    print("1. Extract Jobs with Total Hours")
    print("2. Generate Human Readable Report")
    print("3. Exit")
    choice = input("\nEnter your choice (1/2/3): ")
    return choice

def main():
    """
    Main function to run the job analysis tasks.
    """
    message = ""  # Initialize the message
    message_color = RESET_COLOR  # Initialize the message color

    while True:
        choice = display_job_analysis_menu(message)
        if choice == "1":
            file_path = select_file()
            if not file_path:
                message = "No file selected. Please try again."
                message_color = LIGHT_RED
            else:
                jobs = extract_jobs_with_total_hours(file_path)
                csv_path = save_to_csv(jobs, file_path)
                message = f"Results saved to {csv_path}"
                message_color = LIGHT_GREEN
            
        elif choice == "2":
            file_path = select_file()
            if not file_path:
                message = "No file selected. Please try again."
                message_color = LIGHT_RED
            else:
                report_path = generate_human_readable_report(file_path)
                message = f"Human readable report generated at: {report_path}"
                message_color = LIGHT_GREEN
            
        elif choice == "3":
            break  # Break out of the while loop to return to the admin.py menu
        else:
            message = "Invalid choice. Please select again."
            message_color = LIGHT_RED

        # Do not return here, just update the message and continue the loop
        # return message, message_color  # Remove this line

    # After the loop, you can return the final message if needed
    return message, message_color

if __name__ == "__main__":
    raise RuntimeError("This script cannot be run directly. Please run it through admin.py.")
