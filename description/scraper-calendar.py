import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to process a single course
def process_course(course):
    pid = course.get('pid')
    subject_code = course.get('subjectCode', {}).get('name', '')
    course_id = course.get('__catalogCourseId', '')
    title = course.get('title', '')

    print(f"Processing Course ID: {course_id}, PID: {pid}")

    # Construct the API URL
    api_url = f"https://uvic.kuali.co/api/v1/catalog/course/65eb47906641d7001c157bc4/{pid}"
    try:
        # Fetch the course details
        response = requests.get(api_url)
        if response.status_code == 200:
            course_detail = response.json()

            # Extract fields from the course detail
            description_html = course_detail.get('description', '')
            # Use BeautifulSoup to remove HTML tags
            description = BeautifulSoup(description_html, 'html.parser').get_text(separator=' ', strip=True)

            # Collect other fields as needed
            credits = course_detail.get('credits', {}).get('value', '')

            # Handle prerequisites and corequisites
            pre_and_corequisites = course_detail.get('preAndCorequisites', '')

            if isinstance(pre_and_corequisites, dict):
                pre_requisites = pre_and_corequisites.get('rulesText', '')
            elif isinstance(pre_and_corequisites, str):
                pre_requisites = BeautifulSoup(pre_and_corequisites, 'html.parser').get_text(separator=' ', strip=True)
            else:
                pre_requisites = ''

            corequisites = course_detail.get('corequisites', '')
            if isinstance(corequisites, dict):
                corequisites_text = corequisites.get('rulesText', '')
            elif isinstance(corequisites, str):
                corequisites_text = BeautifulSoup(corequisites, 'html.parser').get_text(separator=' ', strip=True)
            else:
                corequisites_text = ''

            # Recommendations and notes
            recommendations_html = course_detail.get('recommendations', '')
            recommendations = BeautifulSoup(recommendations_html, 'html.parser').get_text(separator=' ', strip=True)

            notes_html = course_detail.get('supplementalNotes', '')
            notes = BeautifulSoup(notes_html, 'html.parser').get_text(separator=' ', strip=True)

            # Create a dictionary for the course data
            course_data = {
                'PID': pid,
                'Course ID': course_id,
                'Subject Code': subject_code,
                'Title': title,
                'Description': description,
                'Credits': credits,
                'Prerequisites': pre_requisites,
                'Corequisites': corequisites_text,
                'Recommendations': recommendations,
                'Notes': notes
            }

            return course_data
        else:
            print(f"Failed to retrieve data for Course ID: {course_id}, PID: {pid}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error processing Course ID: {course_id}, PID: {pid}. Error: {e}")
        return None

# Load the courses data from the JSON file
with open('courses_list.json', 'r', encoding='utf-8') as f:
    courses_list = json.load(f)

# List to store the processed course data
course_data_list = []

# Implement concurrency using ThreadPoolExecutor
num_workers = 10  # Adjust the number of workers as needed

with ThreadPoolExecutor(max_workers=num_workers) as executor:
    future_to_course = {executor.submit(process_course, course): course for course in courses_list}

    for future in as_completed(future_to_course):
        course_data = future.result()
        if course_data:
            course_data_list.append(course_data)
        else:
            # Handle courses that failed to process
            pass

# Convert the list of course data to a DataFrame and save to CSV
df = pd.DataFrame(course_data_list)
df.to_csv('scraped_course_data.csv', index=False, encoding='utf-8')

print("Data saved to 'courses_data.csv'")