import json
import pandas as pd

# Function to read JSON data from a file
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# Function to clean and structure the data
def clean_data(json_data):
    structured_data = []

    for entry in json_data:
        term = entry['term']
        subject = entry['subject']
        course_number = entry['course_number']
        
        # Extract details
        details = entry['details']
        if len(details) >= 7:
            structured_data.append({
                "term": term,
                "subject": subject,
                "course_number": course_number,
                "frequency": details[0],
                "time": details[1],
                "days": details[2],
                "location": details[3],
                "date_range": details[4],
                "schedule_type": details[5],
                "instructor": details[6]
            })

    return pd.DataFrame(structured_data)

# Path to your JSON file
json_file_path = 'scraped_courses.json'

# Read the JSON file
json_data = read_json_file(json_file_path)

# Clean the data
df = clean_data(json_data)

# Display the cleaned data
print(df)

# Optionally, save to CSV
df.to_csv('cleaned_courses.csv', index=False)
