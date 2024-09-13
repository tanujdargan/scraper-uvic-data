import csv
import ast
from collections import defaultdict

# Read the original CSV file
input_file = 'scraped_courses.csv'
output_file = 'processed-courses.csv'

# Placeholder for processed data
processed_data = []

# Column headers for the output CSV
headers = [
    "term", "subject", "course_number", "frequency", "time", "days",
    "location", "date_range", "schedule_type", "instructor", 
    "instructional_method", "units", "additional_information"
]

# Function to parse details
def parse_details(details_list):
    # Initialize the fields
    frequency = time = days = location = date_range = schedule_type = instructor = ''
    instructional_method = units = additional_information = ''
    
    if len(details_list) > 1:
        for detail in details_list:
            if "Every Week" in detail:
                frequency = "Every Week"
            if "am" in detail or "pm" in detail:
                time = detail.split('\n')[0].strip()
            if any(day in detail for day in ["M", "T", "W", "R", "F"]):
                days = detail.split('\n')[0].strip()
            if "Building" in detail:
                location = detail.split('\n')[0].strip()
            if "-" in detail and "2024" in detail:
                date_range = detail.split('\n')[0].strip()
            if "Lecture" in detail:
                schedule_type = "Lecture"
            if "(P)" in detail:
                instructor = detail.split('\n')[0].strip()
            if "Face-to-face" in detail:
                instructional_method = "Face-to-face"
            if "1.500 Credits" in detail:
                units = "1.5"
            if "Associated Term:" in detail:
                additional_information = detail.split('\n')[0].strip()
    
    return (frequency, time, days, location, date_range, 
            schedule_type, instructor, instructional_method, units, additional_information)

# Process the input CSV file
with open(input_file, mode='r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        term = row['term']
        subject = row['subject']
        course_number = row['course_number']
        details = ast.literal_eval(row['details'].strip())
        
        (frequency, time, days, location, date_range, 
         schedule_type, instructor, instructional_method, 
         units, additional_information) = parse_details(details)

        # Append to processed data list
        processed_data.append({
            "term": term,
            "subject": subject,
            "course_number": course_number,
            "frequency": frequency,
            "time": time,
            "days": days,
            "location": location,
            "date_range": date_range,
            "schedule_type": schedule_type,
            "instructor": instructor,
            "instructional_method": instructional_method,
            "units": units,
            "additional_information": additional_information
        })

# Remove duplicates
unique_data = {frozenset(item.items()): item for item in processed_data}.values()

# Write to the new CSV file
with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    for data in unique_data:
        writer.writerow(data)
