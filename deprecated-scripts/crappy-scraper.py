import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# Load the CSV file
csv_file = 'courses-list.csv'
courses_df = pd.read_csv(csv_file)

# Base URL for course schedulecls
base_url = "https://www.uvic.ca/BAN1P/bwckctlg.p_disp_listcrse"

# Term options
terms = ['202401', '202404', '202409', '202501']

# Function to scrape course data
def scrape_course_data(term, subject, course_number):
    params = {
        'term_in': term,
        'subj_in': subject,
        'crse_in': course_number,
        'schd_in': ''
    }
    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract relevant data from the page
    course_data = []
    for row in soup.find_all('tr'):  # Example: iterate over table rows
        columns = row.find_all('td')
        if columns:
            course_info = {
                'term': term,
                'subject': subject,
                'course_number': course_number,
                'details': [col.text.strip() for col in columns]
            }
            course_data.append(course_info)
    
    return course_data

# Iterate over each course and term
all_course_data = []
for _, row in courses_df.iterrows():
    subject = row['Subject']
    course_number = row['Course Number']
    for term in terms:
        course_data = scrape_course_data(term, subject, course_number)
        all_course_data.extend(course_data)

# Save data to CSV
csv_output_file = 'scraped_courses.csv'
df = pd.DataFrame(all_course_data)
df.to_csv(csv_output_file, index=False)
print(f"Data saved to {csv_output_file}")

# Save data to JSON
json_output_file = 'scraped_courses.json'
with open(json_output_file, 'w') as json_file:
    json.dump(all_course_data, json_file, indent=4)
print(f"Data saved to {json_output_file}")
